"""AI咨询模型"""
from datetime import datetime
from extensions import db


class AiChatSession(db.Model):
    __tablename__ = 'ai_chat_sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_no = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_persona = db.Column(db.String(30))
    title = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_message_at = db.Column(db.DateTime)

    # 关系
    messages = db.relationship('AiChatMessage', backref='session',
                               cascade='all, delete-orphan', lazy='dynamic',
                               order_by='AiChatMessage.created_at')

    def to_dict(self):
        return {
            'id': self.id,
            'session_no': self.session_no,
            'user_id': self.user_id,
            'doctor_persona': self.doctor_persona,
            'title': self.title,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_message_at': self.last_message_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_message_at else None,
        }


class AiChatMessage(db.Model):
    __tablename__ = 'ai_chat_messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('ai_chat_sessions.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user/assistant/system
    content = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer)
    llm_model = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'tokens_used': self.tokens_used,
            'llm_model': self.llm_model,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
