# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 扩展管理模块
统一管理数据库、JWT、CORS、限流器等扩展实例
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 数据库实例
db = SQLAlchemy()

# JWT管理器
jwt = JWTManager()

# CORS跨域支持
cors = CORS()

# API限流器
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['200 per minute'],
    storage_uri='memory://',
    strategy='fixed-window'
)


def init_extensions(app):
    """初始化所有扩展"""
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['*']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    limiter.init_app(app)
