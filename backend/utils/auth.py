"""JWT认证工具"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models.user import User


def generate_token(user_id, role, username):
    """生成JWT Token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'username': username,
        'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']),
        'iat': datetime.utcnow(),
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


def decode_token(token):
    """解码JWT Token"""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'code': 401, 'message': '缺少认证Token'}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({'code': 401, 'message': 'Token无效或已过期'}), 401

        user = User.query.get(payload['user_id'])
        if not user or user.status != 'active':
            return jsonify({'code': 401, 'message': '用户不存在或已被禁用'}), 401

        request.current_user = user
        request.current_user_id = payload['user_id']
        request.current_user_role = payload['role']
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """角色验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user_role'):
                return jsonify({'code': 401, 'message': '请先登录'}), 401
            if request.current_user_role not in roles:
                return jsonify({'code': 403, 'message': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
