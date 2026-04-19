"""批量诊断API - 异步后台处理 + 文件名解析模式 + 批量PDF报告生成"""
import json
import os
import re
import threading
import time
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models.diagnosis import Diagnosis, DiseaseProbability
from models.batch import BatchRecord
from models.patient import Patient
from models.user import User
from models.report import Report
from utils.auth import token_required, role_required
from utils.validators import allowed_file
from services.ai_service import predict_image, is_model_loaded, load_model, get_runtime_params
from models.approval import Approval
from services.report_service import create_diagnosis_report
from services.pdf_service import generate_batch_pdf

batch_bp = Blueprint('batch', __name__, url_prefix='/api/v1/batch')

# 全局进度跟踪: { batch_id: progress_dict }
_batch_progress = {}
_batch_cancel = {}

# 文件名解析正则: P患者ID-姓名-性别-年龄-临床发现-图片ID.扩展名
FILENAME_RE = re.compile(r'^(P\d+)-(.+)-(male|female)-(\d+)-([A-Za-z]+)-(\d+)\.(\w+)$')

FINDING_ZH_MAP = {
    'Cough': '咳嗽', 'ChestPain': '胸痛', 'Fever': '发热',
    'Dyspnea': '呼吸困难', 'Hemoptysis': '咯血', 'Routine': '体检',
    'FollowUp': '复查', 'Fatigue': '乏力', 'Wheeze': '喘息', 'Other': '其他',
}


def parse_filename(filename):
    """解析标准文件名格式，返回患者信息"""
    match = FILENAME_RE.match(filename)
    if not match:
        return {}, False
    finding_en = match.group(5)
    return {
        'patient_no': match.group(1),
        'name': match.group(2),
        'gender': match.group(3),
        'age': int(match.group(4)),
        'finding': finding_en,
        'finding_zh': FINDING_ZH_MAP.get(finding_en, finding_en),
        'image_id': match.group(6),
    }, True


def find_or_create_patient(info, user_id):
    """根据解析的患者信息查找或创建患者记录"""
    if 'patient_no' not in info:
        return None
    patient = Patient.query.filter_by(patient_no=info['patient_no']).first()
    if patient:
        return patient
    patient = Patient(
        patient_no=info['patient_no'],
        name=info['name'],
        gender=info.get('gender', 'male'),
        age=info.get('age'),
        medical_history=f"批量上传自动创建(主要发现: {info.get('finding_zh', '未知')})",
        created_by=user_id,
    )
    db.session.add(patient)
    db.session.flush()
    return patient


def _db_commit_with_retry(max_retries=10, interval=0.3):
    """SQLite 安全提交：遇到 database is locked 时自动重试，释放连接避免长期锁库"""
    for attempt in range(max_retries):
        try:
            db.session.commit()
            return True
        except Exception as e:
            if 'database is locked' in str(e) or 'locked' in str(e):
                if attempt < max_retries - 1:
                    db.session.rollback()
                    time.sleep(interval * (attempt + 1))
                    continue
            raise
    return False


def _process_batch_async(app, batch_id, file_entries, user_id, patient_ids_map, skip_heatmap, clinical_findings_map):
    """后台流水线处理 - 逐张模式: 每张图片检测→推送→报告→完成→下一张"""
    print(f"[批量诊断] 线程启动: batch_id={batch_id}, files={len(file_entries)}")
    try:
        with app.app_context():
            print(f"[批量诊断] 进入app_context, 开始处理 batch_id={batch_id}")
            _process_batch_inner(app, batch_id, file_entries, user_id, patient_ids_map, skip_heatmap, clinical_findings_map)
            print(f"[批量诊断] 处理完成 batch_id={batch_id}")
    except Exception as e:
        import traceback
        print(f"[批量诊断] 批次{batch_id}后台线程崩溃: {e}")
        traceback.print_exc()
        # 标记失败，让前端能看到错误
        progress = _batch_progress.get(batch_id)
        if progress:
            progress['results'].append({
                'original_filename': progress.get('current_file', '未知'),
                'status': 'error',
                'error_msg': f'后台处理异常: {e}',
            })
            progress['processed'] = progress['total']
            # 更新批次记录
            try:
                batch = BatchRecord.query.get(batch_id)
                if batch:
                    batch.status = 'failed'
                    batch.error_log = f'后台线程崩溃: {e}'
                    db.session.commit()
            except Exception:
                pass


def _process_batch_inner(app, batch_id, file_entries, user_id, patient_ids_map, skip_heatmap, clinical_findings_map):
    """后台流水线内部逻辑"""
    print(f"[批量诊断] _process_batch_inner 开始: batch_id={batch_id}")
    progress = _batch_progress.get(batch_id)
    if not progress:
        print(f"[批量诊断] 错误: 找不到进度 batch_id={batch_id}")
        return

    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'images')
    heatmap_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'heatmaps')
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(heatmap_dir, exist_ok=True)

    success_count = 0
    failed_count = 0
    errors = []

    # ===== 阶段0: 过滤有效文件 + 解析患者 + 收集推理路径 =====
    valid_entries = []  # [(entry, patient, filename_orig), ...]
    for i, entry in enumerate(file_entries):
        cancel_event = _batch_cancel.get(batch_id)
        if cancel_event and cancel_event.is_set():
            progress['cancelled'] = True
            errors.append("用户取消检测")
            break

        filename_orig = entry['original_filename']
        filepath = entry['filepath']
        progress['current_file'] = filename_orig
        progress['processed'] = i

        if not allowed_file(filename_orig):
            failed_count += 1
            errors.append(f"{filename_orig}: 不支持的格式")
            progress['results'].append({
                'original_filename': filename_orig,
                'status': 'error',
                'error_msg': '不支持的格式',
            })
            continue

        # 确定患者
        patient = None
        pid = patient_ids_map.get(filename_orig, 0)
        if pid and pid > 0:
            patient = Patient.query.get(pid)
        else:
            info, is_standard = parse_filename(filename_orig)
            if is_standard:
                patient = find_or_create_patient(info, user_id)

        valid_entries.append((entry, patient, filename_orig, filepath))

    if progress.get('cancelled'):
        pass  # 已处理取消

    elif valid_entries:
        # ===== 流水线模式: 逐张处理 - 检测→推送→报告→完成 → 下一张 =====
        for idx, (entry, patient, filename_orig, filepath) in enumerate(valid_entries):
            cancel_event = _batch_cancel.get(batch_id)
            if cancel_event and cancel_event.is_set():
                progress['cancelled'] = True
                errors.append("用户取消检测")
                break

            progress['current_file'] = filename_orig
            progress['processed'] = idx + 1

            try:
                # ---- 步骤1: 单张检测 ----
                result = predict_image(filepath, skip_heatmap=True)
                if result is None:
                    failed_count += 1
                    progress['results'].append({
                        'original_filename': filename_orig,
                        'status': 'error',
                        'error_msg': '推理失败',
                    })
                    errors.append(f"{filename_orig}: 推理失败")
                    continue

                probabilities = result['probabilities']
                top_prob = probabilities[0]['probability'] if probabilities else 0

                # ---- 步骤2: 存入数据库 ----
                diagnosis_no = f"DX{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
                diagnosis = Diagnosis(
                    diagnosis_no=diagnosis_no,
                    patient_id=patient.id if patient else 0,
                    doctor_id=user_id,
                    technician_id=user_id,
                    image_path=entry['saved_path'],
                    model_version=result['model_version'],
                    report_status='reporting',
                    diagnosis_type='batch',
                    batch_id=batch_id,
                )
                db.session.add(diagnosis)
                db.session.flush()

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
                # 在关闭session前提取所有需要的数据到普通变量
                diagnosis_id = diagnosis.id
                patient_id_val = patient.id if patient else 0
                patient_name_val = patient.name if patient else ''
                patient_no_val = patient.patient_no if patient else ''
                patient_gender_val = patient.gender if patient and patient.gender else ''
                patient_age_val = patient.age if patient and patient.age else None
                patient_info_dict = patient.to_dict() if patient else {}
                _db_commit_with_retry()

                # 获取医生信息
                doctor = User.query.get(user_id)

                diag_result = {
                    'diagnosis_id': diagnosis_id,
                    'diagnosis_no': diagnosis_no,
                    'patient_id': patient_id_val,
                    'patient_name': patient_name_val,
                    'patient_no': patient_no_val,
                    'patient_gender': patient_gender_val,
                    'patient_age': patient_age_val,
                    'original_filename': filename_orig,
                    'image_url': f"/static/{entry['saved_path']}",
                    'filepath': filepath,
                    'heatmap_url': None,
                    'probabilities': probabilities,
                    'top_result': 'normal' if top_prob < 0.3 else probabilities[0]['disease_code'],
                    'top_result_name': '正常' if top_prob < 0.3 else probabilities[0]['disease_name_zh'],
                    'top5': probabilities[:5],
                    'report_id': None,
                    'clinical_finding': clinical_findings_map.get(filename_orig, ''),
                    'doctor_name': doctor.real_name if doctor else '',
                    'doctor_department': doctor.department if doctor and doctor.department else '',
                    'diagnosed_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
                }

                # ---- 步骤3: 推送检测结果到前端（概率条立即可见）----
                progress['results'].append({
                    'original_filename': filename_orig,
                    'status': 'reporting',
                    'data': diag_result,
                })

                # ---- 步骤4: 生成热力图 + LLM报告 ----
                try:
                    # 带热力图的推理（单张）
                    result_full = predict_image(filepath, skip_heatmap=False)
                    heatmap_image = result_full.get('heatmap_image')

                    heatmap_filename = None
                    if heatmap_image:
                        heatmap_filename = f"{uuid.uuid4().hex}_gradcam.png"
                        heatmap_image.save(os.path.join(heatmap_dir, heatmap_filename))
                        # 更新DB（使用新session重新查询）
                        diag = Diagnosis.query.get(diagnosis_id)
                        if diag:
                            diag.heatmap_path = f"heatmaps/{heatmap_filename}"
                        diag_result['heatmap_url'] = f"/static/heatmaps/{heatmap_filename}"

                    # LLM报告生成（使用预提取的patient信息）
                    patient_info = dict(patient_info_dict) if patient_info_dict else {}
                    clinical_finding = clinical_findings_map.get(filename_orig, '')
                    if clinical_finding:
                        patient_info['clinical_finding'] = clinical_finding

                    report_data = create_diagnosis_report(probabilities, patient_info or None)
                    report = Report(
                        diagnosis_id=diagnosis_id,
                        ai_generated_content=report_data['ai_generated_content'],
                        findings=report_data['findings'],
                        impression=report_data['impression'],
                        recommendations=report_data['recommendations'],
                        ai_model_used=report_data['ai_model_used'],
                    )
                    db.session.add(report)
                    db.session.flush()

                    approval = Approval(
                        diagnosis_id=diagnosis_id,
                        report_id=report.id,
                        patient_id=diag_result['patient_id'],
                        submitter_id=user_id,
                        status='pending',
                        priority='normal',
                    )
                    db.session.add(approval)

                    diagnosis_obj = Diagnosis.query.get(diagnosis_id)
                    if diagnosis_obj:
                        diagnosis_obj.report_status = 'pending_review'
                    _db_commit_with_retry()

                    # 补充报告数据
                    diag_result['report_id'] = report.id
                    diag_result['ai_report'] = {
                        'findings': report_data['findings'],
                        'impression': report_data['impression'],
                        'recommendations': report_data['recommendations'],
                        'full_text': report_data.get('ai_generated_content', ''),
                    }

                except Exception as report_err:
                    # 报告失败但检测已成功
                    try:
                        diagnosis_obj = Diagnosis.query.get(diagnosis_id)
                        if diagnosis_obj:
                            diagnosis_obj.report_status = 'pending_review'
                        _db_commit_with_retry()
                    except Exception:
                        pass
                    diag_result['ai_report'] = {'findings': '', 'impression': '报告生成失败', 'recommendations': ''}
                    diag_result['report_error'] = str(report_err)
                    errors.append(f"{filename_orig}: 报告生成失败 - {report_err}")

                # ---- 步骤5: 标记该患者完成 ----
                pr_entry = None
                for r in progress['results']:
                    if r['original_filename'] == filename_orig and r.get('status') == 'reporting':
                        pr_entry = r
                        break
                if pr_entry:
                    pr_entry['status'] = 'done'

                success_count += 1

            except Exception as detect_err:
                failed_count += 1
                progress['results'].append({
                    'original_filename': filename_orig,
                    'status': 'error',
                    'error_msg': f'检测异常: {detect_err}',
                })
                errors.append(f"{filename_orig}: 检测异常 - {detect_err}")

    # 更新批次记录 - 流水线全部完成
    progress['processed'] = len(file_entries)
    try:
        batch = BatchRecord.query.get(batch_id)
        if batch:
            batch.success_count = success_count
            batch.failed_count = failed_count
            if progress.get('cancelled'):
                batch.status = 'cancelled'
            else:
                batch.status = 'completed' if failed_count == 0 else ('partial_failed' if success_count > 0 else 'failed')
            batch.error_log = '\n'.join(errors) if errors else None
            batch.completed_at = datetime.now()
            _db_commit_with_retry()
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass

    # 清理取消标志
    _batch_cancel.pop(batch_id, None)


@batch_bp.route('/diagnose', methods=['POST'])
@token_required
def batch_diagnose():
    """异步批量诊断 - 立即返回batch_id，后台处理"""
    try:
        if not is_model_loaded():
            load_model()
    except Exception as e:
        current_app.logger.error(f"[批量诊断] 模型加载失败: {e}")
        return jsonify({'code': 500, 'message': f'AI模型加载失败: {e}'}), 500

    files = request.files.getlist('images')
    if not files:
        return jsonify({'code': 400, 'message': '请上传影像文件'}), 400

    try:
        # 解析 patient_ids 映射: { filename: patient_id }
        patient_ids_map = {}
        raw = request.form.get('patient_ids', '')
        if raw:
            patient_ids_map = json.loads(raw)
            patient_ids_map = {k: int(v) for k, v in patient_ids_map.items() if v}
    except Exception:
        patient_ids_map = {}

    try:
        # 解析临床发现映射: { filename: finding_text }
        clinical_findings_map = {}
        raw = request.form.get('clinical_findings', '')
        if raw:
            clinical_findings_map = json.loads(raw)
    except Exception:
        clinical_findings_map = {}

    skip_heatmap = request.form.get('skip_heatmap', 'true').lower() == 'true'

    try:
        batch_no = f"BX{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:4].upper()}"
        batch = BatchRecord(
            batch_no=batch_no,
            uploader_id=request.current_user_id,
            total_count=len(files),
            status='processing',
        )
        db.session.add(batch)
        _db_commit_with_retry()

        # 先保存所有上传文件到磁盘
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        os.makedirs(upload_dir, exist_ok=True)

        file_entries = []
        for f in files:
            if not f or not f.filename:
                continue
            ext = f.filename.rsplit('.', 1)[1].lower() if '.' in f.filename else 'png'
            saved_name = f"{uuid.uuid4().hex}.{ext}"
            saved_path = f"images/{saved_name}"
            filepath = os.path.join(upload_dir, saved_name)
            f.save(filepath)
            file_entries.append({
                'original_filename': f.filename,
                'filepath': filepath,
                'saved_path': saved_path,
            })

        # 初始化进度跟踪
        _batch_progress[batch.id] = {
            'processed': 0,
            'total': len(file_entries),
            'current_file': '',
            'cancelled': False,
            'results': [],
        }
        _batch_cancel[batch.id] = threading.Event()

        # 启动后台线程
        app = current_app._get_current_object()
        print(f"[批量诊断] 准备启动线程: batch_id={batch.id}, file_entries={len(file_entries)}")
        thread = threading.Thread(
            target=_process_batch_async,
            args=(app, batch.id, file_entries, request.current_user_id, patient_ids_map, skip_heatmap, clinical_findings_map),
            daemon=True,
        )
        thread.start()

        return jsonify({
            'code': 200,
            'data': {
                'batch_id': batch.id,
                'batch_no': batch.batch_no,
                'total_count': len(file_entries),
                'status': 'processing',
            }
        })

    except Exception as e:
        current_app.logger.error(f"[批量诊断] 请求处理异常: {e}", exc_info=True)
        return jsonify({'code': 500, 'message': f'批量诊断启动失败: {e}'}), 500


@batch_bp.route('/<int:batch_id>/progress', methods=['GET'])
@token_required
def get_batch_progress(batch_id):
    """查询批量诊断进度"""
    # 先查内存进度
    progress = _batch_progress.get(batch_id)
    if progress:
        return jsonify({
            'code': 200,
            'data': {
                'batch_id': batch_id,
                'processed': progress['processed'],
                'total': progress['total'],
                'current_file': progress['current_file'],
                'cancelled': progress['cancelled'],
                'status': ('processing'
                    if not progress['cancelled']
                    and (progress['processed'] < progress['total']
                         or any(r.get('status') in ('diagnosing', 'reporting') for r in progress['results']))
                    else 'completed'),
                'results': progress['results'],
            }
        })

    # 内存中没有，查数据库
    batch = BatchRecord.query.get(batch_id)
    if not batch:
        return jsonify({'code': 404, 'message': '批次不存在'}), 404

    # 从DB构建结果
    diagnoses = Diagnosis.query.filter_by(batch_id=batch_id).all()
    results = []
    for d in diagnoses:
        probs = [p.to_dict() for p in d.probabilities]
        probs_sorted = sorted(probs, key=lambda x: x['probability'], reverse=True)
        top_prob = probs_sorted[0]['probability'] if probs_sorted else 0
        patient = Patient.query.get(d.patient_id) if d.patient_id and d.patient_id > 0 else None
        reports = Report.query.filter_by(diagnosis_id=d.id).all()
        report = reports[0] if reports else None

        results.append({
            'original_filename': d.image_path,  # fallback
            'status': 'done',
            'data': {
                'diagnosis_id': d.id,
                'diagnosis_no': d.diagnosis_no,
                'patient_id': patient.id if patient else 0,
                'patient_name': patient.name if patient else '',
                'patient_no': patient.patient_no if patient else '',
                'image_url': f"/static/{d.image_path}",
                'heatmap_url': f"/static/{d.heatmap_path}" if d.heatmap_path else None,
                'probabilities': probs_sorted,
                'top_result': 'normal' if top_prob < 0.3 else probs_sorted[0]['disease_code'],
                'top_result_name': '正常' if top_prob < 0.3 else probs_sorted[0].get('disease_name_zh', ''),
                'top5': probs_sorted[:5],
                'report_id': report.id if report else None,
                'ai_report': {
                    'findings': report.findings if report else '',
                    'impression': report.impression if report else '',
                    'recommendations': report.recommendations if report else '',
                } if report else None,
            }
        })

    return jsonify({
        'code': 200,
        'data': {
            'batch_id': batch_id,
            'processed': batch.success_count + batch.failed_count,
            'total': batch.total_count,
            'current_file': '',
            'cancelled': batch.status == 'cancelled',
            'status': batch.status,
            'results': results,
        }
    })


@batch_bp.route('/<int:batch_id>/cancel', methods=['POST'])
@token_required
def cancel_batch(batch_id):
    """取消批量诊断"""
    cancel_event = _batch_cancel.get(batch_id)
    if cancel_event:
        cancel_event.set()
    return jsonify({'code': 200, 'message': '已发送取消信号'})


@batch_bp.route('/<int:batch_id>/generate-reports', methods=['POST'])
@token_required
def batch_generate_reports(batch_id):
    """Phase 2: 批量生成报告（热力图 + LLM报告 + 审批记录）"""
    batch = BatchRecord.query.get(batch_id)
    if not batch:
        return jsonify({'code': 404, 'message': '批次不存在'}), 404

    # 查询该批次下所有已诊断但未生成报告的记录
    diagnoses = Diagnosis.query.filter_by(
        batch_id=batch_id, report_status='diagnosed'
    ).all()

    if not diagnoses:
        # 已全部生成过，直接返回
        return jsonify({'code': 200, 'message': '所有报告已生成', 'data': {'generated': 0}})

    heatmap_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'heatmaps')
    os.makedirs(heatmap_dir, exist_ok=True)

    generated = 0
    failed = 0
    results = []

    for diagnosis in diagnoses:
        try:
            patient = None
            if diagnosis.patient_id and diagnosis.patient_id > 0:
                patient = Patient.query.get(diagnosis.patient_id)

            # 构建图片完整路径
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], diagnosis.image_path)
            if not os.path.isfile(image_path):
                failed += 1
                continue

            # Phase 2: 带热力图的AI推理
            result = predict_image(image_path, skip_heatmap=False)
            probabilities = result['probabilities']

            # 保存热力图
            heatmap_filename = None
            heatmap_image = result.get('heatmap_image')
            if heatmap_image:
                heatmap_filename = f"{uuid.uuid4().hex}_gradcam.png"
                heatmap_image.save(os.path.join(heatmap_dir, heatmap_filename))
                diagnosis.heatmap_path = f"heatmaps/{heatmap_filename}"

            # 生成LLM报告
            patient_info = patient.to_dict() if patient else {}
            clinical_finding = ''
            # 从请求中获取临床发现（如果有传递）
            try:
                cf_map = request.json.get('clinical_findings', {}) if request.is_json else {}
                clinical_finding = cf_map.get(diagnosis.image_path, '')
            except Exception:
                pass
            if clinical_finding:
                patient_info['clinical_finding'] = clinical_finding

            report_data = create_diagnosis_report(probabilities, patient_info or None)
            report = Report(
                diagnosis_id=diagnosis.id,
                ai_generated_content=report_data['ai_generated_content'],
                findings=report_data['findings'],
                impression=report_data['impression'],
                recommendations=report_data['recommendations'],
                ai_model_used=report_data['ai_model_used'],
            )
            db.session.add(report)
            db.session.flush()

            # 创建审批记录
            approval = Approval(
                diagnosis_id=diagnosis.id,
                report_id=report.id,
                patient_id=diagnosis.patient_id,
                submitter=request.current_user_id,
                status='pending',
                priority='normal',
            )
            db.session.add(approval)

            # 更新诊断状态
            diagnosis.report_status = 'pending_review'

            top_prob = probabilities[0]['probability'] if probabilities else 0
            results.append({
                'diagnosis_id': diagnosis.id,
                'heatmap_url': f"/static/{diagnosis.heatmap_path}" if diagnosis.heatmap_path else None,
                'report_id': report.id,
                'ai_report': {
                    'findings': report_data['findings'],
                    'impression': report_data['impression'],
                    'recommendations': report_data['recommendations'],
                    'full_text': report_data.get('ai_generated_content', ''),
                },
            })
            generated += 1

        except Exception as e:
            failed += 1
            current_app.logger.error(f"报告生成失败 [{diagnosis.image_path}]: {e}")

    _db_commit_with_retry()

    # 更新批次状态
    remaining = Diagnosis.query.filter_by(batch_id=batch_id, report_status='diagnosed').count()
    if remaining == 0 and batch.status == 'diagnosed':
        batch.status = 'completed' if failed == 0 else 'partial_failed'
        batch.completed_at = datetime.now()
        _db_commit_with_retry()

    return jsonify({
        'code': 200,
        'data': {
            'generated': generated,
            'failed': failed,
            'results': results,
        }
    })


@batch_bp.route('/upload', methods=['POST'])
@token_required
def batch_upload():
    """批量上传影像 - 解析文件名关联患者，生成诊断+热力图+PDF"""
    if not is_model_loaded():
        load_model()

    files = request.files.getlist('images')
    if not files:
        return jsonify({'code': 400, 'message': '请上传影像文件'}), 400

    batch_no = f"BX{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:4].upper()}"
    batch = BatchRecord(
        batch_no=batch_no,
        uploader_id=request.current_user_id,
        total_count=len(files),
        status='processing',
    )
    db.session.add(batch)
    db.session.flush()

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    heatmap_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'heatmaps')
    pdf_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdfs')
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(heatmap_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)

    success_count = 0
    failed_count = 0
    abnormal_count = 0
    errors = []
    diagnosis_results = []

    for f in files:
        if not f or not f.filename:
            continue
        if not allowed_file(f.filename):
            failed_count += 1
            errors.append(f"{f.filename}: 不支持的格式")
            continue

        try:
            patient_info, is_standard = parse_filename(f.filename)

            ext = f.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(upload_dir, filename)
            f.save(filepath)

            result = predict_image(filepath)
            probabilities = result['probabilities']
            heatmap_image = result['heatmap_image']

            heatmap_filename = None
            if heatmap_image:
                heatmap_filename = f"{uuid.uuid4().hex}_gradcam.png"
                heatmap_image.save(os.path.join(heatmap_dir, heatmap_filename))

            patient = None
            patient_id = 0
            if is_standard:
                patient = find_or_create_patient(patient_info, request.current_user_id)
                if patient:
                    patient_id = patient.id
            else:
                abnormal_count += 1

            diagnosis_no = f"DX{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
            diagnosis = Diagnosis(
                diagnosis_no=diagnosis_no,
                patient_id=patient_id,
                doctor_id=request.current_user_id,
                technician_id=request.current_user_id,
                image_path=f"images/{filename}",
                heatmap_path=f"heatmaps/{heatmap_filename}" if heatmap_filename else None,
                model_version=result['model_version'],
                report_status='pending_review',
                diagnosis_type='batch',
                batch_id=batch.id,
            )
            db.session.add(diagnosis)
            db.session.flush()

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

            report_data = create_diagnosis_report(probabilities)
            report = Report(
                diagnosis_id=diagnosis.id,
                ai_generated_content=report_data['ai_generated_content'],
                findings=report_data['findings'],
                impression=report_data['impression'],
                recommendations=report_data['recommendations'],
                ai_model_used=report_data['ai_model_used'],
            )
            db.session.add(report)
            db.session.flush()

            # 自动创建审批记录
            approval = Approval(
                diagnosis_id=diagnosis.id,
                report_id=report.id,
                patient_id=diagnosis.patient_id,
                submitter_id=request.current_user_id,
                status='pending',
                priority='normal',
            )
            db.session.add(approval)

            diagnosis_results.append({
                'diagnosis_id': diagnosis.id,
                'diagnosis_no': diagnosis_no,
                'patient_id': patient_id,
                'patient_info': patient_info,
                'is_standard': is_standard,
                'patient_name': patient.name if patient else ('未知患者' if not is_standard else patient_info.get('name', '')),
                'patient_no': patient.patient_no if patient else '',
                'original_filename': f.filename,
                'finding': patient_info.get('finding', ''),
                'finding_zh': patient_info.get('finding_zh', ''),
                'image_path': f"images/{filename}",
                'heatmap_path': f"heatmaps/{heatmap_filename}" if heatmap_filename else None,
                'probabilities': probabilities,
                'report': {
                    'findings': report_data['findings'],
                    'impression': report_data['impression'],
                    'recommendations': report_data['recommendations'],
                },
            })
            success_count += 1

        except Exception as e:
            failed_count += 1
            errors.append(f"{f.filename}: {str(e)}")

    pdf_filename = None
    if diagnosis_results:
        try:
            pdf_filename = generate_batch_pdf(batch_no, diagnosis_results, pdf_dir)
        except Exception as e:
            errors.append(f"PDF生成失败: {str(e)}")

    batch.success_count = success_count
    batch.failed_count = failed_count
    batch.status = 'completed' if failed_count == 0 else ('partial_failed' if success_count > 0 else 'failed')
    batch.error_log = '\n'.join(errors) if errors else None
    batch.completed_at = datetime.now()
    _db_commit_with_retry()

    return jsonify({
        'code': 200,
        'data': {
            'batch_id': batch.id,
            'batch_no': batch.batch_no,
            'total_count': batch.total_count,
            'success_count': success_count,
            'failed_count': failed_count,
            'abnormal_count': abnormal_count,
            'status': batch.status,
            'pdf_url': f"/static/pdfs/{pdf_filename}" if pdf_filename else None,
            'diagnoses': diagnosis_results,
        }
    })


@batch_bp.route('/list', methods=['GET'])
@token_required
def get_batch_list():
    """获取批量诊断历史"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = BatchRecord.query.order_by(BatchRecord.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for b in pagination.items:
        d = b.to_dict()
        d['diagnoses'] = []
        for diag in b.diagnoses:
            dd = diag.to_dict()
            patient = Patient.query.get(diag.patient_id) if diag.patient_id and diag.patient_id > 0 else None
            dd['patient_name'] = patient.name if patient else '未知患者'
            dd['patient_no'] = patient.patient_no if patient else ''
            d['diagnoses'].append(dd)
        items.append(d)

    return jsonify({
        'code': 200,
        'data': {
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
        }
    })


@batch_bp.route('/<int:batch_id>', methods=['GET'])
@token_required
def get_batch_detail(batch_id):
    """获取批次详情"""
    batch = BatchRecord.query.get_or_404(batch_id)
    diagnoses = Diagnosis.query.filter_by(batch_id=batch_id).all()

    diag_list = []
    for d in diagnoses:
        dd = d.to_dict()
        patient = Patient.query.get(d.patient_id) if d.patient_id and d.patient_id > 0 else None
        dd['patient_name'] = patient.name if patient else '未知患者'
        dd['patient_no'] = patient.patient_no if patient else ''
        dd['probabilities'] = [p.to_dict() for p in d.probabilities]
        reports = Report.query.filter_by(diagnosis_id=d.id).all()
        dd['reports'] = [r.to_dict() for r in reports]
        diag_list.append(dd)

    return jsonify({
        'code': 200,
        'data': {
            **batch.to_dict(),
            'diagnoses': diag_list,
        }
    })


@batch_bp.route('/<int:batch_id>/pdf', methods=['GET'])
@token_required
def download_batch_pdf(batch_id):
    """下载批次PDF报告"""
    from flask import send_file
    batch = BatchRecord.query.get_or_404(batch_id)
    pdf_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdfs')
    pdf_path = os.path.join(pdf_dir, f"{batch.batch_no}.pdf")
    if not os.path.exists(pdf_path):
        return jsonify({'code': 404, 'message': 'PDF报告不存在，请重新生成'}), 404
    return send_file(pdf_path, as_attachment=True, download_name=f"{batch.batch_no}_报告.pdf")
