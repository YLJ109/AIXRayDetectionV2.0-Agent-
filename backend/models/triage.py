"""智能分诊记录模型"""
from datetime import datetime
from extensions import db


class TriageRecord(db.Model):
    __tablename__ = 'triage_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    symptoms = db.Column(db.Text, nullable=False)
    symptom_duration = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    vital_signs = db.Column(db.Text)  # JSON
    ai_triage_result = db.Column(db.Text)  # JSON
    doctor_confirmed = db.Column(db.Boolean)
    confirmed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'symptoms': self.symptoms,
            'symptom_duration': self.symptom_duration,
            'severity': self.severity,
            'vital_signs': json.loads(self.vital_signs) if self.vital_signs else None,
            'ai_triage_result': json.loads(self.ai_triage_result) if self.ai_triage_result else None,
            'doctor_confirmed': self.doctor_confirmed,
            'confirmed_by': self.confirmed_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
