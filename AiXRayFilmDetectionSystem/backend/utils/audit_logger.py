# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 审计日志工具
记录所有关键操作，支持安全审计与追溯
"""
import logging
from datetime import datetime
from backend.core.extensions import db
from backend.models.all_models import AuditLog

logger = logging.getLogger(__name__)


class AuditLogger:
    """审计日志记录器"""

    @staticmethod
    def log(user_id, username, action, resource_type='', resource_id=0,
            detail='', ip_address='', user_agent=''):
        """记录审计日志"""
        try:
            log_entry = AuditLog(
                user_id=user_id,
                username=username or 'system',
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                detail=detail,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            logger.error(f"审计日志记录失败: {str(e)}")
            db.session.rollback()

    @staticmethod
    def log_login(user, ip_address='', user_agent=''):
        """记录登录"""
        AuditLogger.log(
            user_id=user.id, username=user.username,
            action='login', resource_type='user', resource_id=user.id,
            detail=f'用户登录: {user.real_name}', ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_logout(user_id, username, ip_address=''):
        """记录登出"""
        AuditLogger.log(
            user_id=user_id, username=username,
            action='logout', resource_type='user',
            detail=f'用户登出', ip_address=ip_address
        )

    @staticmethod
    def log_diagnosis(user, record_id, detail=''):
        """记录诊断操作"""
        AuditLogger.log(
            user_id=user.id, username=user.username,
            action='diagnosis', resource_type='diagnosis_record',
            resource_id=record_id, detail=detail
        )

    @staticmethod
    def log_patient(user, patient_id, action='create', detail=''):
        """记录患者操作"""
        AuditLogger.log(
            user_id=user.id, username=user.username,
            action=f'patient_{action}', resource_type='patient',
            resource_id=patient_id, detail=detail
        )

    @staticmethod
    def log_user_management(operator, target_id, action='create', detail=''):
        """记录用户管理操作"""
        AuditLogger.log(
            user_id=operator.id, username=operator.username,
            action=f'user_{action}', resource_type='user',
            resource_id=target_id, detail=detail
        )

    @staticmethod
    def get_logs(page=1, per_page=20, user_id=None, action=None, start_date=None, end_date=None):
        """查询审计日志"""
        query = AuditLog.query.filter_by(is_deleted=False)
        if user_id:
            query = query.filter_by(user_id=user_id)
        if action:
            query = query.filter_by(action=action)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        return query.order_by(AuditLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )


audit_logger = AuditLogger()
