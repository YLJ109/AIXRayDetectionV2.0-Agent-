# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 大模型API管理路由
支持多种大模型（豆包、DeepSeek、ChatGPT等）的统一管理
"""
import json
import logging
from datetime import datetime
from flask import Blueprint, request
from backend.utils.common import success_response, error_response, paginate_data, admin_required, doctor_or_admin_required
from backend.utils.audit_logger import audit_logger
from backend.core.extensions import db
from backend.models.all_models import LLMProvider, LLMCallLog
from backend.services.llm_service import llm_service

logger = logging.getLogger(__name__)
llm_bp = Blueprint('llm', __name__, url_prefix='/api/llm')


# ============ 提供商管理 ============

@llm_bp.route('/providers', methods=['GET'])
@admin_required
def list_providers():
    """获取所有LLM提供商配置"""
    try:
        providers = LLMProvider.query.filter_by(is_deleted=False).order_by(LLMProvider.priority.desc()).all()
        
        data = []
        for p in providers:
            item = {
                'id': p.id,
                'name': p.name,
                'provider_type': p.provider_type,
                'api_endpoint': p.api_endpoint,
                'default_model': p.default_model,
                'is_active': p.is_active,
                'priority': p.priority,
                'last_used_at': p.last_used_at.strftime('%Y-%m-%d %H:%M:%S') if p.last_used_at else None,
                'total_calls': p.total_calls,
                'last_error': p.last_error,
                'created_at': p.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': p.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            # 不返回加密的API密钥
            item['api_key_masked'] = '******' if p.api_key_encrypted else ''
            data.append(item)
        
        return success_response({'providers': data})
    except Exception as e:
        logger.error(f"获取LLM提供商列表失败: {str(e)}", exc_info=True)
        return error_response(f"获取LLM提供商列表失败: {str(e)}")


@llm_bp.route('/providers', methods=['POST'])
@admin_required
def create_provider():
    """创建LLM提供商配置"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    provider_type = data.get('provider_type', '').strip()
    api_key = data.get('api_key', '').strip()
    api_endpoint = data.get('api_endpoint', '').strip()
    default_model = data.get('default_model', '').strip()
    config_json = data.get('config_json', {})
    is_active = data.get('is_active', True)
    priority = data.get('priority', 0)
    
    # 验证必填字段
    if not all([name, provider_type, api_key, api_endpoint]):
        return error_response("缺少必填字段")
    
    # 验证配置
    is_valid, error_msg = llm_service.validate_provider_config(provider_type, {
        'api_key': api_key,
        'api_endpoint': api_endpoint
    })
    if not is_valid:
        return error_response(error_msg)
    
    # 检查名称是否已存在
    existing = LLMProvider.query.filter_by(name=name, is_deleted=False).first()
    if existing:
        return error_response("提供商名称已存在")
    
    try:
        # 加密API密钥
        api_key_encrypted = llm_service.encrypt_api_key(api_key)
        
        provider = LLMProvider(
            name=name,
            provider_type=provider_type,
            api_key_encrypted=api_key_encrypted,
            api_endpoint=api_endpoint,
            default_model=default_model or llm_service.get_default_model(provider_type),
            config_json=json.dumps(config_json) if config_json else '{}',
            is_active=is_active,
            priority=priority
        )
        
        db.session.add(provider)
        db.session.commit()
        
        audit_logger.log(
            action='create_llm_provider',
            resource_type='llm_provider',
            resource_id=provider.id,
            detail=f"创建LLM提供商: {name}"
        )
        
        return success_response({
            'id': provider.id,
            'name': provider.name,
            'message': 'LLM提供商创建成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建LLM提供商失败: {str(e)}", exc_info=True)
        return error_response(f"创建LLM提供商失败: {str(e)}")


@llm_bp.route('/providers/<int:provider_id>', methods=['PUT'])
@admin_required
def update_provider(provider_id):
    """更新LLM提供商配置"""
    provider = LLMProvider.query.filter_by(id=provider_id, is_deleted=False).first()
    if not provider:
        return error_response("提供商不存在", 404)
    
    data = request.get_json()
    
    try:
        # 更新字段
        if 'name' in data:
            name = data['name'].strip()
            if name != provider.name:
                existing = LLMProvider.query.filter_by(name=name, is_deleted=False).first()
                if existing:
                    return error_response("提供商名称已存在")
                provider.name = name
        
        if 'api_key' in data and data['api_key']:
            api_key = data['api_key'].strip()
            is_valid, error_msg = llm_service.validate_provider_config(provider.provider_type, {
                'api_key': api_key,
                'api_endpoint': provider.api_endpoint
            })
            if not is_valid:
                return error_response(error_msg)
            provider.api_key_encrypted = llm_service.encrypt_api_key(api_key)
        
        if 'api_endpoint' in data:
            api_endpoint = data['api_endpoint'].strip()
            if not api_endpoint.startswith(('http://', 'https://')):
                return error_response("API端点必须是有效的HTTP/HTTPS URL")
            provider.api_endpoint = api_endpoint
        
        if 'default_model' in data:
            provider.default_model = data['default_model'].strip()
        
        if 'config_json' in data:
            provider.config_json = json.dumps(data['config_json'])
        
        if 'is_active' in data:
            provider.is_active = data['is_active']
        
        if 'priority' in data:
            provider.priority = data['priority']
        
        provider.updated_at = datetime.now()
        db.session.commit()
        
        audit_logger.log(
            action='update_llm_provider',
            resource_type='llm_provider',
            resource_id=provider.id,
            detail=f"更新LLM提供商: {provider.name}"
        )
        
        return success_response({'message': '更新成功'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新LLM提供商失败: {str(e)}", exc_info=True)
        return error_response(f"更新LLM提供商失败: {str(e)}")


@llm_bp.route('/providers/<int:provider_id>', methods=['DELETE'])
@admin_required
def delete_provider(provider_id):
    """删除LLM提供商配置"""
    provider = LLMProvider.query.filter_by(id=provider_id, is_deleted=False).first()
    if not provider:
        return error_response("提供商不存在", 404)
    
    try:
        provider.is_deleted = True
        provider.updated_at = datetime.now()
        db.session.commit()
        
        audit_logger.log(
            action='delete_llm_provider',
            resource_type='llm_provider',
            resource_id=provider.id,
            detail=f"删除LLM提供商: {provider.name}"
        )
        
        return success_response({'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除LLM提供商失败: {str(e)}", exc_info=True)
        return error_response(f"删除LLM提供商失败: {str(e)}")


@llm_bp.route('/providers/<int:provider_id>/test', methods=['POST'])
@admin_required
def test_provider(provider_id):
    """测试LLM提供商连接"""
    provider = LLMProvider.query.filter_by(id=provider_id, is_deleted=False).first()
    if not provider:
        return error_response("提供商不存在", 404)
    
    try:
        result = llm_service.test_connection(provider)
        
        # 更新提供商状态
        if result['success']:
            provider.last_error = ''
        else:
            provider.last_error = result.get('message', '')
        provider.updated_at = datetime.now()
        db.session.commit()
        
        return success_response(result)
    except Exception as e:
        logger.error(f"测试LLM提供商失败: {str(e)}", exc_info=True)
        return error_response(f"测试失败: {str(e)}")


# ============ 统一调用接口 ============

@llm_bp.route('/chat', methods=['POST'])
@doctor_or_admin_required
def chat():
    """
    统一LLM调用接口
    body: {
        "provider_id": 1,  // 可选，不传则使用优先级最高的活跃提供商
        "messages": [{"role": "user", "content": "..."}],
        "temperature": 0.7,  // 可选
        "max_tokens": 2000   // 可选
    }
    """
    from flask_jwt_extended import get_jwt_identity
    
    data = request.get_json()
    messages = data.get('messages', [])
    provider_id = data.get('provider_id')
    kwargs = {
        'temperature': data.get('temperature', 0.7),
        'max_tokens': data.get('max_tokens', 2000),
    }
    # 仅在用户明确指定 model 时传入，避免 None 覆盖默认值
    if data.get('model'):
        kwargs['model'] = data['model']
    
    if not messages:
        return error_response("消息列表不能为空")
    
    try:
        # 获取提供商
        if provider_id:
            provider = LLMProvider.query.filter_by(id=provider_id, is_deleted=False, is_active=True).first()
            if not provider:
                return error_response("提供商不存在或未启用", 404)
        else:
            # 使用优先级最高的活跃提供商
            provider = LLMProvider.query.filter_by(is_deleted=False, is_active=True).order_by(LLMProvider.priority.desc()).first()
            if not provider:
                return error_response("没有可用的LLM提供商")
        
        # 调用API
        result = llm_service.call_api(provider, messages, **kwargs)
        
        # 记录调用日志
        user_id = get_jwt_identity()
        call_log = LLMCallLog(
            provider_id=provider.id,
            user_id=user_id,
            model_name=result.get('model', provider.default_model),
            prompt_tokens=result.get('tokens', {}).get('prompt', 0),
            completion_tokens=result.get('tokens', {}).get('completion', 0),
            total_tokens=result.get('tokens', {}).get('total', 0),
            response_time=result.get('response_time', 0),
            is_success=result['success'],
            error_message=result.get('error', '')
        )
        db.session.add(call_log)
        
        # 更新提供商统计
        provider.total_calls += 1
        provider.last_used_at = datetime.now()
        if not result['success']:
            provider.last_error = result.get('error', '')
        else:
            provider.last_error = ''
        
        db.session.commit()
        
        return success_response(result)
    except Exception as e:
        db.session.rollback()
        logger.error(f"LLM调用失败: {str(e)}", exc_info=True)
        return error_response(f"LLM调用失败: {str(e)}")


# ============ 调用日志 ============

@llm_bp.route('/logs', methods=['GET'])
@admin_required
def get_call_logs():
    """获取LLM调用日志"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    provider_id = request.args.get('provider_id', type=int)
    user_id = request.args.get('user_id', type=int)
    
    try:
        query = LLMCallLog.query.filter_by(is_deleted=False)
        
        if provider_id:
            query = query.filter_by(provider_id=provider_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        pagination = query.order_by(LLMCallLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        logs = []
        for log in pagination.items:
            logs.append({
                'id': log.id,
                'provider_id': log.provider_id,
                'provider_name': log.provider.name if log.provider else '',
                'user_id': log.user_id,
                'user_name': log.user.real_name if log.user else '',
                'model_name': log.model_name,
                'prompt_tokens': log.prompt_tokens,
                'completion_tokens': log.completion_tokens,
                'total_tokens': log.total_tokens,
                'response_time': round(log.response_time, 2),
                'is_success': log.is_success,
                'error_message': log.error_message,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return success_response({
            'items': logs,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        logger.error(f"获取LLM调用日志失败: {str(e)}", exc_info=True)
        return error_response(f"获取LLM调用日志失败: {str(e)}")


# ============ 提供商类型 ============

@llm_bp.route('/provider-types', methods=['GET'])
def get_provider_types():
    """获取支持的提供商类型"""
    types = [
        {
            'value': 'openai',
            'label': 'OpenAI (ChatGPT)',
            'default_endpoint': llm_service.get_default_endpoint('openai'),
            'default_model': llm_service.get_default_model('openai')
        },
        {
            'value': 'anthropic',
            'label': 'Anthropic (Claude)',
            'default_endpoint': llm_service.get_default_endpoint('anthropic'),
            'default_model': llm_service.get_default_model('anthropic')
        },
        {
            'value': 'doubao',
            'label': '豆包 (字节跳动)',
            'default_endpoint': llm_service.get_default_endpoint('doubao'),
            'default_model': llm_service.get_default_model('doubao')
        },
        {
            'value': 'deepseek',
            'label': 'DeepSeek',
            'default_endpoint': llm_service.get_default_endpoint('deepseek'),
            'default_model': llm_service.get_default_model('deepseek')
        },
        {
            'value': 'qwen',
            'label': '阿里云通义千问 (Qwen)',
            'default_endpoint': llm_service.get_default_endpoint('qwen'),
            'default_model': llm_service.get_default_model('qwen')
        },
        {
            'value': 'custom',
            'label': '自定义',
            'default_endpoint': '',
            'default_model': ''
        }
    ]
    return success_response({'types': types})
