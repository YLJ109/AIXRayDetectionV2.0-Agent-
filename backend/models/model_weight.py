"""模型权重文件模型"""
from datetime import datetime
from extensions import db


class ModelWeight(db.Model):
    __tablename__ = 'model_weights'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version_name = db.Column(db.String(50), unique=True, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    file_hash = db.Column(db.String(64))
    architecture = db.Column(db.String(50))
    training_dataset = db.Column(db.String(100))
    metrics = db.Column(db.Text)  # JSON
    is_active = db.Column(db.Boolean, default=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.Text)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'version_name': self.version_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'architecture': self.architecture,
            'training_dataset': self.training_dataset,
            'metrics': json.loads(self.metrics) if self.metrics else None,
            'is_active': self.is_active,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if self.uploaded_at else None,
            'description': self.description,
        }
