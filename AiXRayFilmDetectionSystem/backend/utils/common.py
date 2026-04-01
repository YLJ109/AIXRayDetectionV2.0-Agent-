# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 通用工具模块
提供统一响应格式、参数校验、分页等通用功能
"""
import os
import uuid
from functools import wraps
from flask import jsonify, request, g
from backend.core.extensions import jwt


def success_response(data=None, message='操作成功', code=200):
    """统一成功响应格式"""
    response = {
        'code': code,
        'message': message,
        'data': data
    }
    return jsonify(response), code


def error_response(message='操作失败', code=400, data=None):
    """统一错误响应格式"""
    response = {
        'code': code,
        'message': message,
        'data': data
    }
    return jsonify(response), code


def paginate_data(pagination):
    """将分页对象转为字典"""
    return {
        'items': [item.to_dict() if hasattr(item, 'to_dict') else item
                  for item in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }


def generate_uuid():
    """生成UUID字符串"""
    return uuid.uuid4().hex


def safe_filename(filename):
    """生成安全的文件名"""
    from werkzeug.utils import secure_filename
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return f'{uuid.uuid4().hex}.{ext}'


def get_client_ip():
    """获取客户端IP"""
    if request.headers.getlist('X-Forwarded-For'):
        return request.headers.getlist('X-Forwarded-For')[0]
    return request.remote_addr


def admin_required(fn):
    """管理员权限装饰器"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        from backend.models.all_models import User, UserRole
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id, is_deleted=False).first()
        user_role = user.role if isinstance(user.role, str) else user.role.value
        if not user or user_role != UserRole.ADMIN.value:
            return error_response('权限不足，需要管理员权限', 403)
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper


def doctor_or_admin_required(fn):
    """医生或管理员权限装饰器"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        from backend.models.all_models import User
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id, is_deleted=False).first()
        if not user or not user.is_active:
            return error_response('用户不存在或已禁用', 401)
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """获取当前登录用户"""
    from flask_jwt_extended import get_jwt_identity
    from backend.models.all_models import User
    user_id = get_jwt_identity()
    return User.query.filter_by(id=user_id, is_deleted=False).first()


# 需要导入的装饰器
from flask_jwt_extended import jwt_required, verify_jwt_in_request


def get_jwt_identity():
    """获取JWT身份"""
    from flask_jwt_extended import get_jwt_identity as _get_jwt_identity
    return _get_jwt_identity()
