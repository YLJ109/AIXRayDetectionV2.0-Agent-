"""用户模型"""
from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin/doctor/nurse
    department = db.Column(db.String(50))
    license_number = db.Column(db.String(50))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='active')
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    diagnoses = db.relationship('Diagnosis', foreign_keys='Diagnosis.doctor_id', backref='doctor', lazy='dynamic')
    uploaded_diagnoses = db.relationship('Diagnosis', foreign_keys='Diagnosis.technician_id', backref='technician', lazy='dynamic')
    chat_sessions = db.relationship('AiChatSession', backref='user', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    preferences = db.relationship('UserPreference', backref='user', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'role': self.role,
            'department': self.department,
            'license_number': self.license_number,
            'email': self.email,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'status': self.status,
            'last_login_at': self.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_login_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
