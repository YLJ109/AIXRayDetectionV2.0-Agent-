"""诊断报告模型"""
from datetime import datetime
from extensions import db


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnoses.id', ondelete='CASCADE'), nullable=False)
    version_no = db.Column(db.Integer, default=1)
    ai_generated_content = db.Column(db.Text, nullable=False)
    doctor_edited_content = db.Column(db.Text)
    final_content = db.Column(db.Text)
    findings = db.Column(db.Text)
    impression = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    ai_model_used = db.Column(db.String(50))
    editor_notes = db.Column(db.Text)
    reject_reason = db.Column(db.Text)
    pdf_path = db.Column(db.String(500))
    status = db.Column(db.String(30), default='draft')
    signed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    signed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'diagnosis_id': self.diagnosis_id,
            'version_no': self.version_no,
            'ai_generated_content': self.ai_generated_content,
            'doctor_edited_content': self.doctor_edited_content,
            'final_content': self.final_content,
            'findings': self.findings,
            'impression': self.impression,
            'recommendations': self.recommendations,
            'ai_model_used': self.ai_model_used,
            'editor_notes': self.editor_notes,
            'reject_reason': self.reject_reason,
            'pdf_path': self.pdf_path,
            'status': self.status,
            'signed_by': self.signed_by,
            'signed_at': self.signed_at.strftime('%Y-%m-%d %H:%M:%S') if self.signed_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
