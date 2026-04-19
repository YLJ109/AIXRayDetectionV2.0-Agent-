"""大模型配置管理API"""
import json
from flask import Blueprint, request, jsonify
from extensions import db
from models.llm_config import LlmConfig
from models.audit import AuditLog
from utils.auth import token_required, role_required
from utils.encryption import encrypt_value, decrypt_value
from openai import OpenAI

llm_configs_bp = Blueprint('llm_configs', __name__, url_prefix='/api/v1/llm-configs')


@llm_configs_bp.route('/', methods=['GET'])
@token_required
@role_required('admin')
def get_configs():
    """获取大模型配置列表"""
    configs = LlmConfig.query.order_by(LlmConfig.priority.asc()).all()
    return jsonify({
        'code': 200,
        'data': [c.to_dict() for c in configs]
    })


@llm_configs_bp.route('/', methods=['POST'])
@token_required
@role_required('admin')
def create_config():
    """创建大模型配置"""
    data = request.get_json()
    model_name = data.get('model_name', '').strip()

    if not model_name:
        return jsonify({'code': 400, 'message': '模型名称不能为空'}), 400

    if LlmConfig.query.filter_by(model_name=model_name).first():
        return jsonify({'code': 400, 'message': '模型名称已存在'}), 400

    config = LlmConfig(
        model_name=model_name,
        provider=data.get('provider', ''),
        api_endpoint=data.get('api_endpoint', ''),
        api_key_encrypted=encrypt_value(data.get('api_key', '')),
        default_params=json.dumps(data.get('default_params', {}), ensure_ascii=False),
        is_default=data.get('is_default', False),
        priority=data.get('priority', 1),
        status=data.get('status', 'active'),
    )
    db.session.add(config)

    # 如果设为默认，取消其他默认
    if config.is_default:
        LlmConfig.query.filter(LlmConfig.id != config.id).update({'is_default': False})

    db.session.commit()
    _log_audit(request.current_user_id, 'CREATE_LLM_CONFIG', 'llm_config', config.id)
    return jsonify({'code': 200, 'data': config.to_dict()})


@llm_configs_bp.route('/<int:config_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_config(config_id):
    """更新大模型配置"""
    config = LlmConfig.query.get_or_404(config_id)
    data = request.get_json()

    if 'provider' in data:
        config.provider = data['provider']
    if 'api_endpoint' in data:
        config.api_endpoint = data['api_endpoint']
    if 'api_key' in data:
        config.api_key_encrypted = encrypt_value(data['api_key'])
    if 'default_params' in data:
        config.default_params = json.dumps(data['default_params'], ensure_ascii=False)
    if 'is_default' in data:
        if data['is_default']:
            LlmConfig.query.filter(LlmConfig.id != config_id).update({'is_default': False})
        config.is_default = data['is_default']
    if 'priority' in data:
        config.priority = data['priority']
    if 'status' in data:
        config.status = data['status']

    db.session.commit()
    _log_audit(request.current_user_id, 'UPDATE_LLM_CONFIG', 'llm_config', config_id)
    return jsonify({'code': 200, 'data': config.to_dict()})


@llm_configs_bp.route('/<int:config_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_config(config_id):
    """删除大模型配置"""
    config = LlmConfig.query.get_or_404(config_id)
    if config.is_default:
        return jsonify({'code': 400, 'message': '不能删除默认模型配置'}), 400
    db.session.delete(config)
    db.session.commit()
    _log_audit(request.current_user_id, 'DELETE_LLM_CONFIG', 'llm_config', config_id)
    return jsonify({'code': 200, 'message': '配置已删除'})


@llm_configs_bp.route('/<int:config_id>/test', methods=['POST'])
@token_required
@role_required('admin')
def test_connection(config_id):
    """测试大模型连通性"""
    config = LlmConfig.query.get_or_404(config_id)
    api_key = decrypt_value(config.api_key_encrypted)

    try:
        client = OpenAI(api_key=api_key, base_url=config.api_endpoint)
        response = client.chat.completions.create(
            model=config.model_name,
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=10,
        )
        return jsonify({
            'code': 200,
            'data': {
                'success': True,
                'response': response.choices[0].message.content,
            }
        })
    except Exception as e:
        return jsonify({
            'code': 200,
            'data': {
                'success': False,
                'error': str(e),
            }
        })


def _log_audit(user_id, action, resource_type, resource_id):
    try:
        log = AuditLog(user_id=user_id, action=action,
                       resource_type=resource_type, resource_id=resource_id,
                       ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
