# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 诊断API路由
处理影像上传、AI诊断、诊断记录管理、报告生成
"""
import os
import logging
from flask import Blueprint, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from backend.utils.common import (
    success_response, error_response, paginate_data,
    get_client_ip, doctor_or_admin_required, get_current_user
)
from backend.services.diagnosis_service import diagnosis_service
from backend.utils.audit_logger import audit_logger
from backend.utils.image_preprocessor import image_preprocessor

logger = logging.getLogger(__name__)
diagnosis_bp = Blueprint('diagnosis', __name__, url_prefix='/api/diagnosis')


@diagnosis_bp.route('/upload', methods=['POST'])
@doctor_or_admin_required
def upload_and_diagnose():
    """上传影像并进行AI诊断"""
    try:
        if 'file' not in request.files:
            return error_response('请上传影像文件')

        file = request.files['file']
        if file.filename == '':
            return error_response('请选择有效的影像文件')

        if not image_preprocessor.is_allowed_file(file.filename):
            return error_response('不支持的文件格式，请上传 png/jpg/jpeg/bmp/gif/webp 格式')

        # 获取当前用户
        user = get_current_user()
        patient_id = request.form.get('patient_id', type=int)
        clinical_info = request.form.get('clinical_info', '')
        symptoms = request.form.get('symptoms', '')

        if not patient_id:
            return error_response('请指定患者ID')

        # 保存上传文件
        filename = secure_filename(file.filename)
        unique_filename = f'{os.urandom(8).hex()}_{filename}'
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)

        # 验证影像
        is_valid, msg = image_preprocessor.validate_medical_image(file_path)
        if not is_valid:
            os.remove(file_path)
            return error_response(f'影像验证失败: {msg}')

        # 获取影像信息
        info = image_preprocessor.get_image_info(file_path)

        # 执行AI诊断
        record = diagnosis_service.create_diagnosis(
            patient_id=patient_id,
            doctor_id=user.id,
            image_path=file_path,
            image_size=info['file_size'] if info else 0,
            image_width=info['width'] if info else 0,
            image_height=info['height'] if info else 0,
            clinical_info=clinical_info,
            symptoms=symptoms
        )

        audit_logger.log_diagnosis(user, record.id, detail=f'上传影像并完成AI诊断: {record.record_no}')

        return success_response({
            'record_id': record.id,
            'record_no': record.record_no,
            'ai_result': record.ai_result if isinstance(record.ai_result, str) else record.ai_result.value,
            'confidence': record.confidence,
            'probabilities': {
                'normal': record.normal_prob,
                'pneumonia': record.pneumonia_prob,
                'tuberculosis': record.tuberculosis_prob
            },
            'inference_time': record.inference_time,
            'image_path': f'/api/diagnosis/image/{os.path.basename(record.image_path)}' if record.image_path else '',
            'heatmap_path': f'/api/diagnosis/heatmap/{os.path.basename(record.heatmap_path)}' if record.heatmap_path else '',
            'created_at': record.created_at.isoformat() if record.created_at else None
        }, 'AI诊断完成')

    except Exception as e:
        logger.error(f"诊断上传失败: {str(e)}")
        return error_response(f'诊断失败: {str(e)}', 500)


@diagnosis_bp.route('/list', methods=['GET'])
@doctor_or_admin_required
def get_diagnosis_list():
    """获取诊断记录列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    patient_id = request.args.get('patient_id', type=int)
    result = request.args.get('result')
    status = request.args.get('status')
    keyword = request.args.get('keyword', '').strip()

    try:
        from datetime import datetime
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        pagination = diagnosis_service.get_diagnosis_list(
            page=page, per_page=per_page,
            patient_id=patient_id, result=result, status=status,
            start_date=start_date, end_date=end_date, keyword=keyword
        )

        # 为每条记录添加患者和医生信息
        items = []
        for record in pagination.items:
            try:
                data = record.to_dict()
            except Exception as dict_err:
                # 兼容旧数据库缺少 inference_time 列的情况
                if 'inference_time' in str(dict_err) or 'no such column' in str(dict_err).lower():
                    data = record.to_dict(exclude=['inference_time'])
                else:
                    raise
            data['patient'] = {
                'id': record.patient.id,
                'patient_no': record.patient.patient_no,
                'name': record.patient.name,
                'gender': record.patient.gender if isinstance(record.patient.gender, str) else record.patient.gender.value,
                'age': record.patient.age
            }
            data['doctor'] = {
                'id': record.doctor.id,
                'real_name': record.doctor.real_name,
                'department': record.doctor.department
            }
            items.append(data)

        return success_response({
            'items': items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        })
    except Exception as e:
        return error_response(f'查询失败: {str(e)}')


@diagnosis_bp.route('/<int:record_id>', methods=['GET'])
@doctor_or_admin_required
def get_diagnosis_detail(record_id):
    """获取诊断记录详情"""
    try:
        record = diagnosis_service.get_diagnosis_detail(record_id)
        try:
            data = record.to_dict()
        except Exception as dict_err:
            if 'inference_time' in str(dict_err) or 'no such column' in str(dict_err).lower():
                data = record.to_dict(exclude=['inference_time'])
            else:
                raise
        # 关联患者和医生信息
        data['patient'] = {
            'id': record.patient.id,
            'patient_no': record.patient.patient_no,
            'name': record.patient.name,
            'gender': record.patient.gender if isinstance(record.patient.gender, str) else record.patient.gender.value,
            'age': record.patient.age
        }
        data['doctor'] = {
            'id': record.doctor.id,
            'real_name': record.doctor.real_name,
            'department': record.doctor.department
        }
        return success_response(data)
    except ValueError as e:
        return error_response(str(e), 404)


@diagnosis_bp.route('/<int:record_id>/review', methods=['PUT'])
@doctor_or_admin_required
def review_diagnosis(record_id):
    """医生审核诊断记录"""
    user = get_current_user()
    data = request.get_json()

    remark = data.get('doctor_remark', '')
    revised_result = data.get('revised_result')

    try:
        record = diagnosis_service.review_diagnosis(
            record_id=record_id, doctor_id=user.id,
            remark=remark, revised_result=revised_result
        )
        audit_logger.log_diagnosis(user, record.id,
                                   detail=f'审核诊断记录: {record.record_no}, 状态: {record.status if isinstance(record.status, str) else record.status.value}')
        return success_response(record.to_dict(), '审核完成')
    except ValueError as e:
        return error_response(str(e))


@diagnosis_bp.route('/<int:record_id>/report', methods=['POST'])
@doctor_or_admin_required
def generate_report(record_id):
    """生成诊断报告"""
    try:
        report_content = diagnosis_service.generate_report(record_id)
        return success_response({'report_content': report_content}, '报告生成成功')
    except ValueError as e:
        return error_response(str(e), 404)
    except RuntimeError as e:
        return error_response(str(e), 500)


@diagnosis_bp.route('/<int:record_id>', methods=['DELETE'])
@doctor_or_admin_required
def delete_diagnosis(record_id):
    """删除诊断记录"""
    user = get_current_user()
    try:
        record = diagnosis_service.get_diagnosis_detail(record_id)
        diagnosis_service.delete_diagnosis(record_id)
        audit_logger.log_diagnosis(user, record_id, detail=f'删除诊断记录: {record.record_no}')
        return success_response(message='删除成功')
    except ValueError as e:
        return error_response(str(e))


@diagnosis_bp.route('/statistics', methods=['GET'])
@doctor_or_admin_required
def get_statistics():
    """获取诊断统计数据"""
    try:
        stats = diagnosis_service.get_statistics()
        return success_response(stats)
    except Exception as e:
        return error_response(f'获取统计数据失败: {str(e)}')


@diagnosis_bp.route('/image/<path:filename>', methods=['GET'])
def get_image(filename):
    """获取影像文件"""
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    return send_from_directory(upload_dir, filename)


@diagnosis_bp.route('/heatmap/<path:filename>', methods=['GET'])
def get_heatmap(filename):
    """获取热力图文件"""
    try:
        heatmap_dir = current_app.config.get('HEATMAP_FOLDER')
        if not heatmap_dir:
            logger.error("HEATMAP_FOLDER 配置缺失")
            return error_response('服务器配置错误', 500)
        
        # 安全检查：防止目录遍历攻击
        safe_filename = secure_filename(filename)
        if not safe_filename:
            return error_response('无效的文件名', 400)
        
        file_path = os.path.join(heatmap_dir, safe_filename)
        if not os.path.exists(file_path):
            logger.warning(f"热力图文件不存在: {file_path}")
            return error_response('热力图文件不存在', 404)
        
        return send_from_directory(heatmap_dir, safe_filename)
    except Exception as e:
        logger.error(f"获取热力图失败: {str(e)}")
        return error_response(f'获取热力图失败: {str(e)}', 500)
