"""诊断审批模型"""
from datetime import datetime
from extensions import db


class Approval(db.Model):
    """诊断审批记录 - 管理诊断报告的审批流程"""
    __tablename__ = 'approvals'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnoses.id', ondelete='CASCADE'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id', ondelete='SET NULL'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 审批状态: pending / approved / rejected / revision_needed
    status = db.Column(db.String(30), default='pending', nullable=False, index=True)
    # 优先级: normal / urgent / critical
    priority = db.Column(db.String(20), default='normal', nullable=False)

    # 审批内容
    review_notes = db.Column(db.Text)       # 审批意见
    reject_reason = db.Column(db.Text)      # 驳回原因

    # 时间
    submitted_at = db.Column(db.DateTime, default=datetime.now)
    reviewed_at = db.Column(db.DateTime)

    # 关系
    diagnosis = db.relationship('Diagnosis', backref=db.backref('approval', uselist=False))
    report = db.relationship('Report', backref=db.backref('approval_record', uselist=False))
    patient = db.relationship('Patient', backref='approvals')
    submitter = db.relationship('User', foreign_keys=[submitter_id], backref='submitted_approvals')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviewed_approvals')

    def to_dict(self, include_detail=False):
        result = {
            'id': self.id,
            'diagnosis_id': self.diagnosis_id,
            'report_id': self.report_id,
            'patient_id': self.patient_id,
            'submitter_id': self.submitter_id,
            'reviewer_id': self.reviewer_id,
            'status': self.status,
            'priority': self.priority,
            'review_notes': self.review_notes,
            'reject_reason': self.reject_reason,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if self.submitted_at else None,
            'reviewed_at': self.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if self.reviewed_at else None,
        }
        if include_detail:
            if self.diagnosis:
                result['diagnosis'] = self.diagnosis.to_dict()
            if self.report:
                result['report'] = self.report.to_dict()
            if self.patient:
                result['patient'] = {
                    'id': self.patient.id,
                    'patient_no': self.patient.patient_no,
                    'name': self.patient.name,
                    'gender': self.patient.gender,
                    'age': self.patient.age,
                }
            if self.submitter:
                result['submitter'] = {
                    'id': self.submitter.id,
                    'real_name': self.submitter.real_name,
                    'role': self.submitter.role,
                }
            if self.reviewer:
                result['reviewer'] = {
                    'id': self.reviewer.id,
                    'real_name': self.reviewer.real_name,
                    'role': self.reviewer.role,
                }
            # 疾病概率
            if self.diagnosis:
                probs = self.diagnosis.disease_probabilities.all()
                result['probabilities'] = [p.to_dict() for p in probs]
                # 影像URL
                if self.diagnosis.image_path:
                    result['image_url'] = f"/static/{self.diagnosis.image_path}"
                if self.diagnosis.heatmap_path:
                    result['heatmap_url'] = f"/static/{self.diagnosis.heatmap_path}"
        return result
