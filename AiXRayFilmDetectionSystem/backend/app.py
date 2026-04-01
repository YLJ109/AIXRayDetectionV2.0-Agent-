# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - Flask应用入口
企业级医疗AI胸部X光智能辅助诊断系统
"""
import os
import sys
import logging
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

# 添加项目根目录到系统路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.core.config import get_config
from backend.core.extensions import init_extensions, db, jwt
from backend.api import all_blueprints


def init_default_llm_provider(app):
    """初始化默认的LLM提供商配置"""
    from backend.models.all_models import LLMProvider
    from backend.services.llm_service import llm_service
    from datetime import datetime
    
    try:
        # 检查是否已存在默认提供商
        existing = LLMProvider.query.filter_by(name='阿里云通义千问', is_deleted=False).first()
        if existing:
            app.logger.info('默认LLM提供商已存在')
            return
        
        # 从配置获取API密钥
        config = get_config()
        api_key = config.OPENAI_API_KEY
        
        if not api_key:
            app.logger.warning('未配置OPENAI_API_KEY，跳过默认LLM提供商初始化')
            return
        
        # 加密API密钥
        api_key_encrypted = llm_service.encrypt_api_key(api_key)
        
        # 创建默认提供商
        provider = LLMProvider(
            name='阿里云通义千问',
            provider_type='qwen',
            api_key_encrypted=api_key_encrypted,
            api_endpoint='https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
            default_model='qwen-plus',
            config_json='{"temperature": 0.7, "max_tokens": 2000}',
            is_active=True,
            priority=100,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.session.add(provider)
        db.session.commit()
        
        app.logger.info('默认LLM提供商初始化成功: 阿里云通义千问 (qwen-plus)')
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'初始化默认LLM提供商失败: {str(e)}')
        raise


def create_app(config_name=None):
    """创建Flask应用工厂"""
    app = Flask(__name__)

    # 加载配置
    if config_name:
        app.config.from_object(config_name)
    else:
        config = get_config()
        app.config.from_object(config)

    # 初始化扩展
    init_extensions(app)

    # JWT回调配置
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'code': 401, 'message': 'Token已过期', 'data': None}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'code': 401, 'message': '无效的Token', 'data': None}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'code': 401, 'message': '缺少认证Token', 'data': None}), 401

    # 注册蓝图
    for bp in all_blueprints:
        app.register_blueprint(bp)

    # 静态文件服务
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.config['UPLOAD_FOLDER'] = static_dir
    app.config['REPORT_FOLDER'] = os.path.join(static_dir, 'reports')
    app.config['HEATMAP_FOLDER'] = os.path.join(static_dir, 'heatmaps')

    # 确保目录存在
    for subdir in ['uploads/images', 'reports', 'heatmaps']:
        os.makedirs(os.path.join(static_dir, subdir), exist_ok=True)

    # 加载AI模型和初始化默认LLM提供商
    with app.app_context():
        try:
            from backend.services.model_service import model_service
            model_service.load_model()
            app.logger.info('AI模型加载成功')
        except Exception as e:
            app.logger.error(f'AI模型加载失败: {str(e)}')
        
        # 初始化默认LLM提供商
        try:
            init_default_llm_provider(app)
        except Exception as e:
            app.logger.error(f'初始化默认LLM提供商失败: {str(e)}')

    return app


# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
