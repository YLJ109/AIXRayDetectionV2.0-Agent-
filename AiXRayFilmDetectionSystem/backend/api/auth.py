# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 认证API路由
处理用户登录、登出、token刷新
"""
import logging
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from backend.utils.common import success_response, error_response, get_client_ip
from backend.services.user_service import user_service
from backend.utils.audit_logger import audit_logger

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    if not data:
        return error_response('请求参数不能为空')

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return error_response('用户名和密码不能为空')

    user = user_service.authenticate(username, password)
    if not user:
        return error_response('用户名或密码错误', 401)

    # 生成Token
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    # 记录登录日志
    audit_logger.log_login(user, ip_address=get_client_ip(),
                           user_agent=request.headers.get('User-Agent', ''))

    return success_response({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'role': user.role if isinstance(user.role, str) else user.role.value,
            'department': user.department
        }
    }, '登录成功')


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新Token"""
    user_id = get_jwt_identity()
    user = user_service.get_user_detail(int(user_id))
    if not user:
        return error_response('用户不存在', 401)

    access_token = create_access_token(identity=str(user.id))
    return success_response({'access_token': access_token}, 'Token刷新成功')


@auth_bp.route('/info', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取当前用户信息"""
    user_id = get_jwt_identity()
    user = user_service.get_user_detail(int(user_id))
    if not user:
        return error_response('用户不存在', 401)

    return success_response({
        'id': user.id,
        'username': user.username,
        'real_name': user.real_name,
        'role': user.role if isinstance(user.role, str) else user.role.value,
        'department': user.department,
        'phone': user.phone,
        'email': user.email
    })


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码"""
    user_id = get_jwt_identity()
    data = request.get_json()

    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return error_response('原密码和新密码不能为空')

    if len(new_password) < 6:
        return error_response('新密码长度不能少于6位')

    try:
        user_service.change_password(int(user_id), old_password, new_password)
        return success_response(message='密码修改成功')
    except ValueError as e:
        return error_response(str(e))
