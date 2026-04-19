"""诊断中心API"""
import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from extensions import db
from services.ai_service import predict_image, get_runtime_params
from models.diagnosis import Diagnosis, DiseaseProbability
from models.patient import Patient
from models.report import Report
from models.audit import AuditLog
from utils.auth import token_required, role_required
from utils.validators import allowed_file
from services.ai_service import predict_image, load_model, is_model_loaded, CN_NAMES, CLASS_NAMES
from services.report_service import create_diagnosis_report
from models.approval import Approval

diagnose_bp = Blueprint('diagnose', __name__, url_prefix='/api/v1/diagnose')


@diagnose_bp.route('/single', methods=['POST'])
@token_required
def diagnose_single():
    """单张影像AI诊断"""
    # 检查模型是否加载
    if not is_model_loaded():
        load_model()

    # 获取参数
    patient_id = request.form.get('patient_id', type=int)
    image_file = request.files.get('image')
    skip_report = request.form.get('skip_report', 'false').lower() == 'true'

    if not image_file:
        return jsonify({'code': 400, 'message': '请上传影像文件'}), 400

    if not allowed_file(image_file.filename):
        return jsonify({'code': 400, 'message': '不支持的文件格式'}), 400

    # 验证患者
    patient = None
    if patient_id:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'code': 404, 'message': '患者不存在'}), 404

    # 保存原始影像
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    os.makedirs(upload_dir, exist_ok=True)
    ext = image_file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    image_path = os.path.join(upload_dir, filename)
    image_file.save(image_path)

    try:
        # AI推理
        result = predict_image(image_path)
        probabilities = result['probabilities']
        heatmap_image = result['heatmap_image']

        # 保存热力图
        heatmap_path = None
        if heatmap_image:
            heatmap_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'heatmaps')
            os.makedirs(heatmap_dir, exist_ok=True)
            heatmap_filename = f"{uuid.uuid4().hex}_gradcam.png"
            heatmap_path = os.path.join(heatmap_dir, heatmap_filename)
            heatmap_image.save(heatmap_path)

        # 生成诊断编号
        diagnosis_no = f"DX{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:4].upper()}"

        # 创建诊断记录
        diagnosis = Diagnosis(
            diagnosis_no=diagnosis_no,
            patient_id=patient.id if patient else 0,
            doctor_id=request.current_user_id,
            technician_id=request.current_user_id,
            image_path=f"images/{filename}",
            heatmap_path=f"heatmaps/{heatmap_filename}" if heatmap_path else None,
            model_version=result['model_version'],
            report_status='pending_review',
            diagnosis_type='single',
        )
        db.session.add(diagnosis)
        db.session.flush()

        # 保存疾病概率
        threshold = get_runtime_params().get('disease_threshold', 0.7)
        for prob in probabilities:
            dp = DiseaseProbability(
                diagnosis_id=diagnosis.id,
                disease_code=prob['disease_code'],
                disease_name_zh=prob['disease_name_zh'],
                probability=prob['probability'],
                threshold_exceeded=prob['probability'] >= threshold,
            )
            db.session.add(dp)

        # 生成AI报告（skip_report=True 时跳过，仅创建空报告记录供后续生成）
        report = None
        report_data = None

        if skip_report:
            # 创建空报告记录（用于后续生成），NOT NULL 字段填空字符串
            report = Report(
                diagnosis_id=diagnosis.id,
                version_no=1,
                ai_generated_content='',
                findings='',
                impression='',
                recommendations='',
                ai_model_used=result['model_version'],
                status='draft',
            )
            db.session.add(report)
            db.session.flush()
        else:
            # 完整流程：检测 + 报告一起生成
            patient_info = patient.to_dict() if patient else None
            if patient_info:
                gender_map = {'male': '男', 'female': '女', 'other': '其他'}
                patient_info['gender_zh'] = gender_map.get(patient_info.get('gender'), '未知')

            report_data = create_diagnosis_report(probabilities, patient_info)

            report = Report(
                diagnosis_id=diagnosis.id,
                version_no=1,
                ai_generated_content=report_data['ai_generated_content'],
                findings=report_data['findings'],
                impression=report_data['impression'],
                recommendations=report_data['recommendations'],
                ai_model_used=report_data['ai_model_used'],
                status='draft',
            )
            db.session.add(report)

        # 创建审批记录
        approval = Approval(
            diagnosis_id=diagnosis.id,
            report_id=report.id if report else None,
            patient_id=diagnosis.patient_id,
            submitter_id=request.current_user_id,
            status='pending',
            priority='normal',
        )
        db.session.add(approval)

        db.session.commit()

        # 构建响应
        prob_list = []
        for dp in DiseaseProbability.query.filter_by(diagnosis_id=diagnosis.id).all():
            prob_list.append(dp.to_dict())

        response_data = {
            'diagnosis_id': diagnosis.id,
            'diagnosis_no': diagnosis.diagnosis_no,
            'probabilities': prob_list,
            'heatmap_url': f"/static/heatmaps/{heatmap_filename}" if heatmap_path else None,
            'image_url': f"/static/images/{filename}",
            'report_id': report.id if report else None,
            'skip_report': skip_report,
        }

        # 仅在未跳过时返回报告内容
        if not skip_report and report_data:
            response_data['ai_report'] = {
                'findings': report_data['findings'],
                'impression': report_data['impression'],
                'recommendations': report_data['recommendations'],
                'ai_model_used': report_data['ai_model_used'],
            }

        return jsonify({'code': 200, 'data': response_data})

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'诊断失败: {str(e)}'}), 500


@diagnose_bp.route('/<int:diagnosis_id>', methods=['GET'])
@token_required
def get_diagnosis(diagnosis_id):
    """获取诊断详情"""
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)
    probs = DiseaseProbability.query.filter_by(diagnosis_id=diagnosis_id).all()
    reports = Report.query.filter_by(diagnosis_id=diagnosis_id).order_by(Report.version_no.desc()).all()

    patient = Patient.query.get(diagnosis.patient_id) if diagnosis.patient_id else None

    return jsonify({
        'code': 200,
        'data': {
            **diagnosis.to_dict(),
            'patient': patient.to_dict() if patient else None,
            'probabilities': [p.to_dict() for p in probs],
            'reports': [r.to_dict() for r in reports],
        }
    })


@diagnose_bp.route('/list', methods=['GET'])
@token_required
def get_diagnosis_list():
    """获取诊断记录列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    keyword = request.args.get('keyword', '').strip()
    disease = request.args.get('disease')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Diagnosis.query
    if status:
        query = query.filter_by(report_status=status)
    if keyword:
        query = query.join(Patient).filter(
            db.or_(Patient.name.like(f'%{keyword}%'),
                   Patient.patient_no.like(f'%{keyword}%'))
        )
    if start_date:
        query = query.filter(Diagnosis.created_at >= start_date)
    if end_date:
        query = query.filter(Diagnosis.created_at <= end_date + ' 23:59:59')
    if disease:
        # 按主要疾病筛选：查找有该疾病且概率最高的诊断记录
        subquery = db.session.query(DiseaseProbability.diagnosis_id)\
            .filter(DiseaseProbability.disease_code == disease)\
            .subquery()
        query = query.filter(Diagnosis.id.in_(subquery))

    query = query.order_by(Diagnosis.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for d in pagination.items:
        patient = Patient.query.get(d.patient_id) if d.patient_id else None
        top_probs = DiseaseProbability.query.filter_by(diagnosis_id=d.id)\
            .order_by(DiseaseProbability.probability.desc()).limit(3).all()
        items.append({
            **d.to_dict(),
            'patient_name': patient.name if patient else '未知',
            'patient_no': patient.patient_no if patient else '',
            'patient_gender': patient.gender if patient else '',
            'patient_age': patient.age if patient else None,
            'top_diseases': [p.to_dict() for p in top_probs],
        })

    return jsonify({
        'code': 200,
        'data': {
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
        }
    })


@diagnose_bp.route('/<int:diagnosis_id>', methods=['DELETE'])
@token_required
def delete_diagnosis(diagnosis_id):
    """删除诊断记录"""
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)
    # 级联删除关联的概率和报告
    DiseaseProbability.query.filter_by(diagnosis_id=diagnosis_id).delete()
    Report.query.filter_by(diagnosis_id=diagnosis_id).delete()
    db.session.delete(diagnosis)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'})
