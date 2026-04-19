"""系统设置和用户偏好模型"""
from datetime import datetime
from extensions import db


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    value_type = db.Column(db.String(20), default='string')
    description = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'value_type': self.value_type,
            'description': self.description,
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }


class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    theme = db.Column(db.String(20), default='light')
    language = db.Column(db.String(10), default='zh-CN')
    notification_enabled = db.Column(db.Boolean, default=True)
    default_llm_model = db.Column(db.String(50))
    dashboard_layout = db.Column(db.Text)  # JSON

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'language': self.language,
            'notification_enabled': self.notification_enabled,
            'default_llm_model': self.default_llm_model,
            'dashboard_layout': json.loads(self.dashboard_layout) if self.dashboard_layout else None,
        }


class LoginSession(db.Model):
    __tablename__ = 'login_sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    logout_at = db.Column(db.DateTime)
