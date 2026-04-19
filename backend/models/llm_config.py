"""大模型配置模型"""
from datetime import datetime
from extensions import db


class LlmConfig(db.Model):
    __tablename__ = 'llm_configs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_name = db.Column(db.String(50), unique=True, nullable=False)
    provider = db.Column(db.String(30))
    api_endpoint = db.Column(db.String(500), nullable=False)
    api_key_encrypted = db.Column(db.String(500), nullable=False)
    default_params = db.Column(db.Text)  # JSON
    is_default = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self, include_key=False):
        import json
        result = {
            'id': self.id,
            'model_name': self.model_name,
            'provider': self.provider,
            'api_endpoint': self.api_endpoint,
            'default_params': json.loads(self.default_params) if self.default_params else None,
            'is_default': self.is_default,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
        if include_key:
            result['api_key'] = '******'
        return result
