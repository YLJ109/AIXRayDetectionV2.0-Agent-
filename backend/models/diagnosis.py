"""诊断记录模型"""
from datetime import datetime
from extensions import db


class Diagnosis(db.Model):
    __tablename__ = 'diagnoses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diagnosis_no = db.Column(db.String(50), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_path = db.Column(db.String(500), nullable=False)
    heatmap_path = db.Column(db.String(500))
    image_metadata = db.Column(db.Text)  # JSON
    model_version = db.Column(db.String(50))
    report_status = db.Column(db.String(30), default='pending_review')
    diagnosis_type = db.Column(db.String(20), default='single')
    batch_id = db.Column(db.Integer, db.ForeignKey('batch_records.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 关系
    disease_probabilities = db.relationship('DiseaseProbability', backref='diagnosis',
                                           cascade='all, delete-orphan', lazy='dynamic')
    reports = db.relationship('Report', backref='diagnosis',
                              cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'diagnosis_no': self.diagnosis_no,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'technician_id': self.technician_id,
            'image_path': self.image_path,
            'heatmap_path': self.heatmap_path,
            'image_metadata': self.image_metadata,
            'model_version': self.model_version,
            'report_status': self.report_status,
            'diagnosis_type': self.diagnosis_type,
            'batch_id': self.batch_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'reviewed_at': self.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if self.reviewed_at else None,
            'reviewed_by': self.reviewed_by,
        }


class DiseaseProbability(db.Model):
    __tablename__ = 'disease_probabilities'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnoses.id', ondelete='CASCADE'), nullable=False)
    disease_code = db.Column(db.String(30), nullable=False)
    disease_name_zh = db.Column(db.String(50), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    threshold_exceeded = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (db.UniqueConstraint('diagnosis_id', 'disease_code'),)

    def to_dict(self):
        return {
            'id': self.id,
            'diagnosis_id': self.diagnosis_id,
            'disease_code': self.disease_code,
            'disease_name_zh': self.disease_name_zh,
            'probability': round(self.probability, 4),
            'threshold_exceeded': self.threshold_exceeded,
        }
