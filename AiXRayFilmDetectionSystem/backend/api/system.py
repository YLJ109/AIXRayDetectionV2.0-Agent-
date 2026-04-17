# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 系统相关API路由
处理系统监控、审计日志、系统配置、数据统计等
"""
import json
import platform
import logging
from datetime import datetime
from flask import Blueprint, request
from backend.utils.common import success_response, error_response, paginate_data, admin_required, doctor_or_admin_required
from backend.utils.audit_logger import audit_logger
from backend.core.extensions import db

logger = logging.getLogger(__name__)
system_bp = Blueprint('system', __name__, url_prefix='/api/system')


@system_bp.route('/info', methods=['GET'])
def system_info():
    """获取系统信息"""
    info = {
        'system_name': '胸影智诊V2.0',
        'version': '2.0.0',
        'description': '企业级医疗AI胸部X光智能辅助诊断系统',
        'python_version': platform.python_version(),
        'platform': platform.platform()
    }
    return success_response(info)


@system_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    from backend.services.model_service import model_service
    return success_response({
        'status': 'healthy',
        'model_loaded': model_service.model_loaded,
        'device': str(model_service.device) if model_service.device else 'N/A'
    })


@system_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    """获取审计日志"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        pagination = audit_logger.get_logs(
            page=page, per_page=per_page,
            user_id=user_id, action=action,
            start_date=start_date, end_date=end_date
        )
        return success_response(paginate_data(pagination))
    except Exception as e:
        return error_response(f'查询失败: {str(e)}')


@system_bp.route('/dashboard', methods=['GET'])
@doctor_or_admin_required
def get_dashboard_data():
    """获取数据看板数据（全部来源于数据库实时查询）"""
    try:
        from backend.services.diagnosis_service import diagnosis_service
        from backend.services.patient_service import patient_service
        from backend.services.user_service import user_service
        from backend.models.all_models import User, Patient, DiagnosisRecord
        from sqlalchemy import func, case

        # 诊断统计
        stats = diagnosis_service.get_statistics()

        # 患者总数
        patient_count = patient_service.get_patient_count()

        # 用户总数
        users = user_service.get_user_list(page=1, per_page=1)
        user_count = users.total

        # 病种分布（中文标签）
        result_cn = {
            'normal': '正常',
            'pneumonia': '肺炎',
            'tuberculosis': '肺结核'
        }
        distribution = []
        for key, value in stats['result_distribution'].items():
            distribution.append({
                'name': result_cn.get(key, key),
                'value': value
            })

        # ===== 医生列表（从数据库查询） =====
        doctor_list = User.query.filter_by(
            is_deleted=False, is_active=True, role='doctor'
        ).order_by(User.created_at.asc()).all()
        doctors_data = []
        for d in doctor_list:
            diag_count = DiagnosisRecord.query.filter_by(
                doctor_id=d.id, is_deleted=False
            ).count()
            today_count = DiagnosisRecord.query.filter(
                DiagnosisRecord.doctor_id == d.id,
                DiagnosisRecord.is_deleted == False,
                func.date(DiagnosisRecord.created_at) == datetime.now().date()
            ).count()
            doctors_data.append({
                'id': d.id,
                'real_name': d.real_name,
                'department': d.department,
                'phone': d.phone,
                'email': d.email,
                'avatar': d.avatar or '',
                'total_diagnoses': diag_count,
                'today_diagnoses': today_count
            })

        # ===== 患者列表（从数据库查询） =====
        patient_list = Patient.query.filter_by(
            is_deleted=False
        ).order_by(Patient.created_at.desc()).limit(20).all()
        patients_data = []
        for p in patient_list:
            last_diag = DiagnosisRecord.query.filter_by(
                patient_id=p.id, is_deleted=False
            ).order_by(DiagnosisRecord.created_at.desc()).first()
            gender_cn = '男' if p.gender in ('male', 'MALE', 'Male') else '女'
            patients_data.append({
                'id': p.id,
                'patient_no': p.patient_no,
                'name': p.name,
                'gender': gender_cn,
                'age': p.age,
                'phone': p.phone,
                'address': p.address,
                'medical_history': p.medical_history or '',
                'last_diagnosis': {
                    'result': result_cn.get(last_diag.ai_result, last_diag.ai_result) if last_diag else None,
                    'confidence': last_diag.confidence if last_diag else None,
                    'date': last_diag.created_at.strftime('%Y-%m-%d %H:%M') if last_diag else None
                },
                'total_diagnoses': DiagnosisRecord.query.filter_by(
                    patient_id=p.id, is_deleted=False
                ).count()
            })

        # ===== 最近诊断记录（从数据库查询） =====
        recent_records = DiagnosisRecord.query.filter_by(
            is_deleted=False
        ).order_by(DiagnosisRecord.created_at.desc()).limit(10).all()
        recent_diagnoses = []
        for r in recent_records:
            pat = Patient.query.filter_by(id=r.patient_id, is_deleted=False).first()
            doc = User.query.filter_by(id=r.doctor_id, is_deleted=False).first()
            recent_diagnoses.append({
                'id': r.id,
                'record_no': r.record_no,
                'patient_name': pat.name if pat else '未知',
                'doctor_name': doc.real_name if doc else '未知',
                'ai_result': result_cn.get(r.ai_result, r.ai_result) if isinstance(r.ai_result, str) else r.ai_result.value,
                'confidence': r.confidence,
                'status': r.status,
                'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        # ===== 置信度分布（从数据库统计） =====
        high_conf = DiagnosisRecord.query.filter(
            DiagnosisRecord.is_deleted == False,
            DiagnosisRecord.confidence > 0.9
        ).count()
        mid_conf = DiagnosisRecord.query.filter(
            DiagnosisRecord.is_deleted == False,
            DiagnosisRecord.confidence >= 0.6,
            DiagnosisRecord.confidence <= 0.9
        ).count()
        low_conf = DiagnosisRecord.query.filter(
            DiagnosisRecord.is_deleted == False,
            DiagnosisRecord.confidence < 0.6
        ).count()

        # ===== 性别分布统计 =====
        male_count = Patient.query.filter_by(is_deleted=False, gender='male').count()
        female_count = Patient.query.filter_by(is_deleted=False, gender='female').count()

        # ===== 年龄段分布 =====
        age_groups = db.session.query(
            case(
                (Patient.age < 18, '未成年'),
                (Patient.age.between(18, 35), '青年'),
                (Patient.age.between(36, 55), '中年'),
                (Patient.age > 55, '老年')
            ),
            func.count(Patient.id)
        ).filter(Patient.is_deleted == False).group_by(
            case(
                (Patient.age < 18, '未成年'),
                (Patient.age.between(18, 35), '青年'),
                (Patient.age.between(36, 55), '中年'),
                (Patient.age > 55, '老年')
            )
        ).all()
        age_distribution = [{'name': name, 'value': count} for name, count in age_groups]

        dashboard = {
            'overview': {
                'total_diagnoses': stats['total_count'],
                'today_diagnoses': stats['today_count'],
                'week_diagnoses': stats['week_count'],
                'total_patients': patient_count,
                'total_users': user_count,
                'total_doctors': len(doctors_data)
            },
            'result_distribution': distribution,
            'daily_stats': stats['daily_stats'],
            'doctors': doctors_data,
            'patients': patients_data,
            'recent_diagnoses': recent_diagnoses,
            'confidence_distribution': {
                'high': high_conf,
                'mid': mid_conf,
                'low': low_conf
            },
            'gender_distribution': {
                'male': male_count,
                'female': female_count
            },
            'age_distribution': age_distribution
        }
        return success_response(dashboard)
    except Exception as e:
        logger.error(f"获取看板数据失败: {str(e)}", exc_info=True)
        return error_response(f'获取看板数据失败: {str(e)}')


# ============ 管理员专用API ============

@system_bp.route('/admin/overview', methods=['GET'])
@admin_required
def get_admin_overview():
    """获取管理员系统概览"""
    try:
        from backend.services.diagnosis_service import diagnosis_service
        from backend.services.patient_service import patient_service
        from backend.services.user_service import user_service
        from backend.models.all_models import AuditLog, DiagnosisRecord

        # 诊断统计
        stats = diagnosis_service.get_statistics()

        # 患者总数
        patient_count = patient_service.get_patient_count()

        # 用户统计
        users_pagination = user_service.get_user_list(page=1, per_page=1000)
        user_count = users_pagination.total
        active_users = sum(1 for u in users_pagination.items if u.is_active)
        role_distribution = {}
        for u in users_pagination.items:
            role = u.role if isinstance(u.role, str) else u.role.value
            role_distribution[role] = role_distribution.get(role, 0) + 1

        # 今日活跃统计
        today_logs = AuditLog.query.filter(
            AuditLog.is_deleted == False,
            AuditLog.action == 'login'
        ).count()

        # 待审核记录
        pending_count = DiagnosisRecord.query.filter(
            DiagnosisRecord.is_deleted == False,
            DiagnosisRecord.status == 'pending'
        ).count()

        return success_response({
            'overview': {
                'total_diagnoses': stats['total_count'],
                'today_diagnoses': stats['today_count'],
                'week_diagnoses': stats['week_count'],
                'total_patients': patient_count,
                'total_users': user_count,
                'active_users': active_users,
                'today_logins': today_logs,
                'pending_reviews': pending_count
            },
            'role_distribution': role_distribution,
            'result_distribution': stats['result_distribution'],
            'daily_stats': stats['daily_stats']
        })
    except Exception as e:
        logger.error(f"获取管理员概览失败: {str(e)}")
        return error_response(f'获取概览数据失败: {str(e)}')


# ============ 系统配置API ============

@system_bp.route('/configs', methods=['GET'])
@admin_required
def get_configs():
    """获取系统配置列表"""
    try:
        from backend.models.all_models import SystemConfig

        group = request.args.get('group')
        query = SystemConfig.query.filter_by(is_deleted=False)
        if group:
            query = query.filter_by(group_name=group)
        configs = query.order_by(SystemConfig.group_name, SystemConfig.config_key).all()

        grouped = {}
        for c in configs:
            g = c.group_name or 'general'
            if g not in grouped:
                grouped[g] = []
            value = c.config_value
            if c.config_type == 'number':
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        pass
            elif c.config_type == 'boolean':
                value = value.lower() in ('true', '1', 'yes')
            elif c.config_type == 'json':
                try:
                    value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass
            grouped[g].append({
                'id': c.id,
                'key': c.config_key,
                'value': value,
                'type': c.config_type,
                'description': c.description,
                'group': c.group_name
            })
        return success_response(grouped)
    except Exception as e:
        return error_response(f'获取配置失败: {str(e)}')


@system_bp.route('/configs', methods=['POST'])
@admin_required
def create_config():
    """创建系统配置"""
    from backend.utils.common import get_current_user
    operator = get_current_user()
    data = request.get_json()
    if not data:
        return error_response('请求参数不能为空')

    config_key = data.get('key', '').strip()
    config_value = data.get('value', '')
    config_type = data.get('type', 'string')
    description = data.get('description', '')
    group_name = data.get('group', 'general')

    if not config_key:
        return error_response('配置键不能为空')

    try:
        from backend.models.all_models import SystemConfig
        if SystemConfig.query.filter_by(config_key=config_key, is_deleted=False).first():
            return error_response('配置键已存在')

        config = SystemConfig(
            config_key=config_key,
            config_value=str(config_value),
            config_type=config_type,
            description=description,
            group_name=group_name
        )
        config.save()
        audit_logger.log_user_management(operator, config.id, 'create_config',
                                         detail=f'创建配置: {config_key}')
        return success_response(config.to_dict(), '配置创建成功', 201)
    except Exception as e:
        return error_response(f'创建配置失败: {str(e)}')


@system_bp.route('/configs/<int:config_id>', methods=['PUT'])
@admin_required
def update_config(config_id):
    """更新系统配置"""
    from backend.utils.common import get_current_user
    operator = get_current_user()
    data = request.get_json()

    try:
        from backend.models.all_models import SystemConfig
        config = SystemConfig.query.filter_by(id=config_id, is_deleted=False).first()
        if not config:
            return error_response('配置不存在', 404)

        if 'value' in data:
            config.config_value = str(data['value'])
        if 'description' in data:
            config.description = data['description']
        if 'group' in data:
            config.group_name = data['group']
        if 'type' in data:
            config.config_type = data['type']

        db.session.commit()
        audit_logger.log_user_management(operator, config_id, 'update_config',
                                         detail=f'更新配置: {config.config_key}')
        return success_response(config.to_dict(), '配置更新成功')
    except Exception as e:
        return error_response(f'更新配置失败: {str(e)}')


@system_bp.route('/configs/<int:config_id>', methods=['DELETE'])
@admin_required
def delete_config(config_id):
    """删除系统配置"""
    from backend.utils.common import get_current_user
    operator = get_current_user()

    try:
        from backend.models.all_models import SystemConfig
        config = SystemConfig.query.filter_by(id=config_id, is_deleted=False).first()
        if not config:
            return error_response('配置不存在', 404)

        config.soft_delete()
        audit_logger.log_user_management(operator, config_id, 'delete_config',
                                         detail=f'删除配置: {config.config_key}')
        return success_response(message='配置删除成功')
    except Exception as e:
        return error_response(f'删除配置失败: {str(e)}')


# ============ 数据统计API ============

@system_bp.route('/admin/statistics', methods=['GET'])
@admin_required
def get_admin_statistics():
    """获取管理员高级统计"""
    try:
        from backend.models.all_models import User, Patient, DiagnosisRecord, AuditLog
        from sqlalchemy import func, extract

        # 用户增长趋势（近7天）
        user_trend = []
        for i in range(6, -1, -1):
            from datetime import datetime, timedelta
            day = datetime.now() - timedelta(days=i)
            count = User.query.filter(
                User.is_deleted == False,
                func.date(User.created_at) == day.date()
            ).count()
            user_trend.append({'date': day.strftime('%m-%d'), 'count': count})

        # 诊断状态分布
        status_stats = {}
        for status in ['pending', 'confirmed', 'revised']:
            count = DiagnosisRecord.query.filter(
                DiagnosisRecord.is_deleted == False,
                DiagnosisRecord.status == status
            ).count()
            status_stats[status] = count

        # 操作日志统计
        action_stats = db.session.query(
            AuditLog.action, func.count(AuditLog.id)
        ).filter(
            AuditLog.is_deleted == False
        ).group_by(AuditLog.action).all()
        action_distribution = {a: c for a, c in action_stats}

        return success_response({
            'user_trend': user_trend,
            'diagnosis_status': status_stats,
            'action_distribution': action_distribution
        })
    except Exception as e:
        logger.error(f"获取高级统计失败: {str(e)}")
        return error_response(f'获取统计数据失败: {str(e)}')


# ============ 模型管理API ============

@system_bp.route('/admin/models', methods=['GET'])
@admin_required
def list_models():
    """列出所有可用模型文件"""
    try:
        from backend.services.model_service import model_service
        models = model_service.list_available_models()
        status = model_service.get_model_status()
        return success_response({'models': models, 'status': status})
    except Exception as e:
        return error_response(f'获取模型列表失败: {str(e)}')


@system_bp.route('/admin/models/upload', methods=['POST'])
@admin_required
def upload_model():
    """上传模型文件"""
    from backend.utils.common import get_current_user
    operator = get_current_user()
    import os
    from flask import current_app
    from werkzeug.utils import secure_filename

    if 'file' not in request.files:
        return error_response('请上传模型文件')
    file = request.files['file']
    if file.filename == '':
        return error_response('请选择有效的模型文件')

    allowed_ext = ('.pth', '.pt', '.onnx', '.pkl', '.bin')
    if not file.filename.lower().endswith(allowed_ext):
        return error_response(f'不支持的模型格式，请上传 {", ".join(allowed_ext)} 格式')

    try:
        weights_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'weights'
        )
        os.makedirs(weights_dir, exist_ok=True)
        filename = secure_filename(file.filename)
        filepath = os.path.join(weights_dir, filename)
        file.save(filepath)
        audit_logger.log_user_management(operator, 0, 'upload_model',
                                         detail=f'上传模型文件: {filename}')
        return success_response({
            'filename': filename,
            'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2)
        }, '模型上传成功')
    except Exception as e:
        return error_response(f'模型上传失败: {str(e)}')


@system_bp.route('/admin/models/switch', methods=['PUT'])
@admin_required
def switch_model():
    """切换当前使用的模型"""
    from backend.utils.common import get_current_user
    operator = get_current_user()
    data = request.get_json()
    filename = data.get('filename', '').strip()

    if not filename:
        return error_response('请指定模型文件名')

    try:
        from backend.services.model_service import model_service
        weights_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'weights'
        )
        filepath = os.path.join(weights_dir, filename)
        if not os.path.exists(filepath):
            return error_response('模型文件不存在', 404)

        success = model_service.reload_model(filepath)
        if success:
            audit_logger.log_user_management(operator, 0, 'switch_model',
                                             detail=f'切换模型: {filename}')
            return success_response(model_service.get_model_status(), '模型切换成功')
        else:
            return error_response('模型加载失败')
    except Exception as e:
        return error_response(f'模型切换失败: {str(e)}')


@system_bp.route('/admin/models/params', methods=['PUT'])
@admin_required
def update_model_params():
    """更新模型推理参数（修改后自动持久化到数据库）"""
    from backend.utils.common import get_current_user
    operator = get_current_user()
    data = request.get_json()

    if not data:
        return error_response('请求参数不能为空')

    try:
        from backend.services.model_service import model_service, VALID_IMAGE_SIZES

        # image_size 前置校验
        if 'image_size' in data and data['image_size'] is not None:
            try:
                size = int(float(data['image_size']))
                if size not in VALID_IMAGE_SIZES:
                    return error_response(
                        f'图像尺寸无效: {data["image_size"]}，'
                        f'允许值: {", ".join(f"{s}x{s}" for s in VALID_IMAGE_SIZES)}',
                        400
                    )
            except (ValueError, TypeError):
                return error_response(f'图像尺寸必须为整数，收到: {data["image_size"]}', 400)

        # num_classes 前置校验（只允许3类）
        if 'num_classes' in data and data['num_classes'] is not None:
            if int(data['num_classes']) != 3:
                return error_response('分类数量固定为3类（正常、肺炎、肺结核），不可修改', 400)

        # 过滤空值
        params = {k: v for k, v in data.items() if v is not None}
        if not params:
            return error_response('没有需要更新的参数')

        changed = model_service.update_params(**params)

        # 保存到数据库
        if changed:
            try:
                model_service.save_params_to_db()
            except Exception as db_err:
                logger.warning(f"参数保存到数据库失败（已生效到内存）: {str(db_err)}")

        audit_logger.log_user_management(operator, 0, 'update_model_params',
                                         detail=f'更新模型参数: {params}')
        return success_response(model_service.get_model_status(),
                                '参数更新成功' if changed else '参数无变化')
    except ValueError as e:
        return error_response(f'参数校验失败: {str(e)}', 400)
    except Exception as e:
        logger.error(f"参数更新失败: {str(e)}")
        return error_response(f'参数更新失败: {str(e)}')


@system_bp.route('/admin/models/params/reset', methods=['PUT'])
@admin_required
def reset_model_params():
    """重置模型推理参数为默认值"""
    from backend.utils.common import get_current_user
    operator = get_current_user()

    try:
        from backend.services.model_service import model_service
        model_service.reset_params()

        audit_logger.log_user_management(operator, 0, 'reset_model_params',
                                         detail='重置模型参数为默认值')
        return success_response(model_service.get_model_status(), '参数已重置为默认值')
    except Exception as e:
        logger.error(f"参数重置失败: {str(e)}")
        return error_response(f'参数重置失败: {str(e)}')


# ============ API管理接口 ============

@system_bp.route('/admin/api-routes', methods=['GET'])
@admin_required
def list_api_routes():
    """获取所有已注册的API路由"""
    try:
        from flask import current_app
        routes = []
        seen = set()
        for rule in current_app.url_map.iter_rules():
            if rule.endpoint == 'static' or rule.rule.startswith('/static'):
                continue
            if rule.rule in seen:
                continue
            seen.add(rule.rule)
            methods = [m for m in rule.methods if m not in ('HEAD', 'OPTIONS')]
            routes.append({
                'path': rule.rule,
                'methods': sorted(methods),
                'endpoint': rule.endpoint
            })
        routes.sort(key=lambda x: x['path'])
        return success_response(routes)
    except Exception as e:
        return error_response(f'获取API列表失败: {str(e)}')
