# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 用户管理API路由
"""
import logging
from flask import Blueprint, request
from backend.utils.common import (
    success_response, error_response, paginate_data,
    admin_required, get_current_user
)
from backend.services.user_service import user_service
from backend.utils.audit_logger import audit_logger

logger = logging.getLogger(__name__)
user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('/list', methods=['GET'])
@admin_required
def get_user_list():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')
    keyword = request.args.get('keyword', '').strip()

    try:
        pagination = user_service.get_user_list(
            page=page, per_page=per_page,
            role=role, keyword=keyword
        )
        return success_response(paginate_data(pagination))
    except Exception as e:
        return error_response(f'查询失败: {str(e)}')


@user_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user_detail(user_id):
    """获取用户详情"""
    try:
        user = user_service.get_user_detail(user_id)
        return success_response(user.to_dict(exclude=['password_hash']))
    except ValueError as e:
        return error_response(str(e), 404)


@user_bp.route('/create', methods=['POST'])
@admin_required
def create_user():
    """创建用户"""
    operator = get_current_user()
    data = request.get_json()

    if not data:
        return error_response('请求参数不能为空')

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    real_name = data.get('real_name', '').strip()
    role = data.get('role', 'doctor')

    if not username or not password or not real_name:
        return error_response('用户名、密码、姓名为必填项')

    if len(password) < 6:
        return error_response('密码长度不能少于6位')

    try:
        user = user_service.create_user(
            username=username, password=password,
            real_name=real_name, role=role,
            department=data.get('department', ''),
            phone=data.get('phone', ''),
            email=data.get('email', '')
        )
        audit_logger.log_user_management(operator, user.id, 'create',
                                         detail=f'创建用户: {username}')
        return success_response(user.to_dict(exclude=['password_hash']), '用户创建成功', 201)
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f'创建失败: {str(e)}')


@user_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """更新用户信息"""
    operator = get_current_user()
    data = request.get_json()

    try:
        user = user_service.update_user(user_id, **data)
        audit_logger.log_user_management(operator, user_id, 'update',
                                         detail=f'更新用户: {user.username}')
        return success_response(user.to_dict(exclude=['password_hash']), '更新成功')
    except ValueError as e:
        return error_response(str(e))


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除用户"""
    operator = get_current_user()
    try:
        user = user_service.get_user_detail(user_id)
        if user_id == operator.id:
            return error_response('不能删除自己')
        user_service.delete_user(user_id)
        audit_logger.log_user_management(operator, user_id, 'delete',
                                         detail=f'删除用户: {user.username}')
        return success_response(message='删除成功')
    except ValueError as e:
        return error_response(str(e))


@user_bp.route('/<int:user_id>/reset-password', methods=['PUT'])
@admin_required
def reset_password(user_id):
    """管理员重置用户密码"""
    operator = get_current_user()
    data = request.get_json()
    new_password = data.get('new_password', '')

    if not new_password or len(new_password) < 6:
        return error_response('新密码不能为空且不少于6位')

    try:
        user_service.reset_password(user_id, new_password)
        audit_logger.log_user_management(operator, user_id, 'reset_password',
                                         detail=f'重置用户密码')
        return success_response(message='密码重置成功')
    except ValueError as e:
        return error_response(str(e))
