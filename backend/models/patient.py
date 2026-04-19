"""患者模型"""
from datetime import datetime
from extensions import db


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    age = db.Column(db.Integer)
    id_card = db.Column(db.String(18))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(50))
    emergency_phone = db.Column(db.String(20))
    blood_type = db.Column(db.String(5))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    medical_history = db.Column(db.Text)  # JSON格式
    allergy_history = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    diagnoses = db.relationship('Diagnosis', backref='patient', lazy='dynamic')
    triage_records = db.relationship('TriageRecord', backref='patient', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_no': self.patient_no,
            'name': self.name,
            'gender': self.gender,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'age': self.age,
            'id_card': self.id_card,
            'phone': self.phone,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'blood_type': self.blood_type,
            'height': self.height,
            'weight': self.weight,
            'medical_history': self.medical_history,
            'allergy_history': self.allergy_history,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
