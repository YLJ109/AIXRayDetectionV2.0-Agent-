"""系统设置API"""
import json
from flask import Blueprint, request, jsonify
from extensions import db
from models.settings import SystemSetting
from models.audit import AuditLog
from utils.auth import token_required, role_required

settings_bp = Blueprint('settings', __name__, url_prefix='/api/v1/settings')


@settings_bp.route('/', methods=['GET'])
@token_required
@role_required('admin')
def get_settings():
    """获取所有系统设置"""
    settings = SystemSetting.query.all()
    result = {}
    for s in settings:
        value = s.setting_value
        if s.value_type == 'int':
            value = int(value)
        elif s.value_type == 'float':
            value = float(value)
        elif s.value_type == 'bool':
            value = value.lower() == 'true'
        elif s.value_type == 'json':
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                pass
        result[s.setting_key] = value

    return jsonify({'code': 200, 'data': result})


@settings_bp.route('/<key>', methods=['PUT'])
@token_required
@role_required('admin')
def update_setting(key):
    """更新系统设置"""
    setting = SystemSetting.query.filter_by(setting_key=key).first()
    data = request.get_json()

    value = data.get('value')
    if value is None:
        return jsonify({'code': 400, 'message': '设置值不能为空'}), 400

    if setting:
        setting.setting_value = str(value)
        setting.updated_by = request.current_user_id
    else:
        setting = SystemSetting(
            setting_key=key,
            setting_value=str(value),
            value_type=data.get('value_type', 'string'),
            description=data.get('description'),
            updated_by=request.current_user_id,
        )
        db.session.add(setting)

    db.session.commit()
    _log_audit(request.current_user_id, 'UPDATE_SETTING', 'setting', key)
    return jsonify({'code': 200, 'data': setting.to_dict()})


@settings_bp.route('/batch', methods=['PUT'])
@token_required
@role_required('admin')
def batch_update_settings():
    """批量更新系统设置"""
    data = request.get_json()
    settings = data.get('settings', {})

    for key, value in settings.items():
        setting = SystemSetting.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = str(value)
            setting.updated_by = request.current_user_id
        else:
            setting = SystemSetting(
                setting_key=key,
                setting_value=str(value),
                value_type='string',
                updated_by=request.current_user_id,
            )
            db.session.add(setting)

    db.session.commit()
    _log_audit(request.current_user_id, 'BATCH_UPDATE_SETTINGS', 'setting', None)
    return jsonify({'code': 200, 'message': '设置已更新'})


def _log_audit(user_id, action, resource_type, resource_id):
    try:
        log = AuditLog(user_id=user_id, action=action,
                       resource_type=resource_type, resource_id=resource_id if isinstance(resource_id, int) else None,
                       details=json.dumps({'key': resource_id}) if resource_id else None,
                       ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
