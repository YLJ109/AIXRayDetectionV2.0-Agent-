"""批量诊断记录模型"""
from datetime import datetime
from extensions import db


class BatchRecord(db.Model):
    __tablename__ = 'batch_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    batch_no = db.Column(db.String(50), unique=True, nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='processing')
    error_log = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime)

    # 关系
    diagnoses = db.relationship('Diagnosis', backref='batch_record', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'batch_no': self.batch_no,
            'uploader_id': self.uploader_id,
            'total_count': self.total_count,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'status': self.status,
            'error_log': self.error_log,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
        }
