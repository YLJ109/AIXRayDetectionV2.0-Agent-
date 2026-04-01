# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 用户管理服务
处理用户认证、创建、权限管理
"""
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.core.extensions import db
from backend.models.all_models import User

logger = logging.getLogger(__name__)


class UserService:
    """用户管理服务"""

    @staticmethod
    def create_user(username, password, real_name, role='doctor',
                    department='', phone='', email=''):
        """创建用户"""
        if User.query.filter_by(username=username, is_deleted=False).first():
            raise ValueError('用户名已存在')

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            real_name=real_name,
            role=role,
            department=department,
            phone=phone,
            email=email
        )
        user.save()
        logger.info(f"用户创建成功: {username}")
        return user

    @staticmethod
    def authenticate(username, password):
        """用户认证"""
        user = User.query.filter_by(username=username, is_deleted=False, is_active=True).first()
        if not user or not check_password_hash(user.password_hash, password):
            return None
        user.last_login_at = datetime.now()
        db.session.commit()
        return user

    @staticmethod
    def get_user_list(page=1, per_page=20, role=None, keyword=None):
        """获取用户列表"""
        query = User.query.filter_by(is_deleted=False)

        if role:
            query = query.filter_by(role=role)
        if keyword:
            query = query.filter(db.or_(
                User.username.contains(keyword),
                User.real_name.contains(keyword),
                User.department.contains(keyword)
            ))

        query = query.order_by(User.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_user_detail(user_id):
        """获取用户详情"""
        user = User.query.filter_by(id=user_id, is_deleted=False).first()
        if not user:
            raise ValueError('用户不存在')
        return user

    @staticmethod
    def update_user(user_id, **kwargs):
        """更新用户信息"""
        user = UserService.get_user_detail(user_id)
        allowed_fields = ['real_name', 'role', 'department', 'phone', 'email', 'is_active']
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                if key == 'role':
                    value = value
                setattr(user, key, value)
        db.session.commit()
        logger.info(f"用户信息更新: {user.username}")
        return user

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """修改密码"""
        user = UserService.get_user_detail(user_id)
        if not check_password_hash(user.password_hash, old_password):
            raise ValueError('原密码错误')
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True

    @staticmethod
    def reset_password(user_id, new_password):
        """管理员重置密码"""
        user = UserService.get_user_detail(user_id)
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        logger.info(f"密码已重置: {user.username}")
        return True

    @staticmethod
    def delete_user(user_id):
        """软删除用户"""
        user = UserService.get_user_detail(user_id)
        user.soft_delete()
        logger.info(f"用户已删除: {user.username}")
        return True


user_service = UserService()
