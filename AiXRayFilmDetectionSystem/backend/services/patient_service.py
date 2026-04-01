# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 患者管理服务
处理患者档案的增删改查
"""
import logging
from backend.core.extensions import db
from backend.models.all_models import Patient


logger = logging.getLogger(__name__)


class PatientService:
    """患者管理服务"""

    @staticmethod
    def create_patient(patient_no, name, gender, age, id_card='', phone='',
                       address='', medical_history='', allergy_history='', remarks=''):
        """创建患者档案"""
        try:
            patient = Patient(
                patient_no=patient_no,
                name=name,
                gender=gender,
                age=age,
                id_card=id_card,
                phone=phone,
                address=address,
                medical_history=medical_history,
                allergy_history=allergy_history,
                remarks=remarks
            )
            patient.save()
            logger.info(f"患者档案创建成功: {patient_no} - {name}")
            return patient
        except Exception as e:
            logger.error(f"创建患者档案失败: {str(e)}")
            raise

    @staticmethod
    def get_patient_list(page=1, per_page=20, keyword=None, gender=None):
        """查询患者列表"""
        query = Patient.query.filter_by(is_deleted=False)

        if keyword:
            query = query.filter(db.or_(
                Patient.name.contains(keyword),
                Patient.patient_no.contains(keyword),
                Patient.phone.contains(keyword)
            ))
        if gender:
            query = query.filter_by(gender=gender)

        query = query.order_by(Patient.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination

    @staticmethod
    def get_patient_detail(patient_id):
        """获取患者详情"""
        patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first()
        if not patient:
            raise ValueError('患者不存在')
        return patient

    @staticmethod
    def update_patient(patient_id, **kwargs):
        """更新患者信息"""
        patient = PatientService.get_patient_detail(patient_id)
        allowed_fields = ['name', 'gender', 'age', 'phone', 'address',
                         'medical_history', 'allergy_history', 'remarks']
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                if key == 'gender':
                    value = value
                setattr(patient, key, value)
        db.session.commit()
        logger.info(f"患者信息更新成功: {patient.patient_no}")
        return patient

    @staticmethod
    def delete_patient(patient_id):
        """软删除患者"""
        patient = PatientService.get_patient_detail(patient_id)
        patient.soft_delete()
        logger.info(f"患者档案已删除: {patient.patient_no}")
        return True

    @staticmethod
    def get_patient_diagnoses(patient_id, page=1, per_page=20):
        """获取患者诊断历史"""
        from backend.models.all_models import DiagnosisRecord
        pagination = DiagnosisRecord.query.filter_by(
            patient_id=patient_id, is_deleted=False
        ).order_by(DiagnosisRecord.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return pagination

    @staticmethod
    def get_patient_count():
        """获取患者总数"""
        return Patient.query.filter_by(is_deleted=False).count()


patient_service = PatientService()
