# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 患者管理API路由
"""
import logging
from flask import Blueprint, request
from backend.utils.common import (
    success_response, error_response, paginate_data,
    doctor_or_admin_required, get_current_user
)
from backend.services.patient_service import patient_service
from backend.utils.audit_logger import audit_logger

logger = logging.getLogger(__name__)
patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')


@patient_bp.route('/list', methods=['GET'])
@doctor_or_admin_required
def get_patient_list():
    """获取患者列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '').strip()
    gender = request.args.get('gender')

    try:
        pagination = patient_service.get_patient_list(
            page=page, per_page=per_page,
            keyword=keyword, gender=gender
        )
        return success_response(paginate_data(pagination))
    except Exception as e:
        return error_response(f'查询失败: {str(e)}')


@patient_bp.route('/<int:patient_id>', methods=['GET'])
@doctor_or_admin_required
def get_patient_detail(patient_id):
    """获取患者详情"""
    try:
        patient = patient_service.get_patient_detail(patient_id)
        data = patient.to_dict()
        # 获取最近诊断记录
        diagnoses = patient_service.get_patient_diagnoses(patient_id, page=1, per_page=5)
        data['recent_diagnoses'] = paginate_data(diagnoses)
        return success_response(data)
    except ValueError as e:
        return error_response(str(e), 404)


@patient_bp.route('/create', methods=['POST'])
@doctor_or_admin_required
def create_patient():
    """创建患者档案"""
    user = get_current_user()
    data = request.get_json()

    if not data:
        return error_response('请求参数不能为空')

    patient_no = data.get('patient_no', '').strip()
    name = data.get('name', '').strip()
    gender = data.get('gender', '')
    age = data.get('age')
    if age is not None:
        try:
            age = int(age)
        except (ValueError, TypeError):
            return error_response('年龄格式不正确')

    if not patient_no or not name or not gender or not age:
        return error_response('患者编号、姓名、性别、年龄为必填项')

    try:
        patient = patient_service.create_patient(
            patient_no=patient_no,
            name=name,
            gender=gender,
            age=age,
            id_card=data.get('id_card', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            medical_history=data.get('medical_history', ''),
            allergy_history=data.get('allergy_history', ''),
            remarks=data.get('remarks', '')
        )
        audit_logger.log_patient(user, patient.id, 'create',
                                 detail=f'创建患者档案: {patient_no} - {name}')
        return success_response(patient.to_dict(), '患者档案创建成功', 201)
    except Exception as e:
        return error_response(f'创建失败: {str(e)}')


@patient_bp.route('/<int:patient_id>', methods=['PUT'])
@doctor_or_admin_required
def update_patient(patient_id):
    """更新患者信息"""
    user = get_current_user()
    data = request.get_json()

    try:
        patient = patient_service.update_patient(patient_id, **data)
        audit_logger.log_patient(user, patient_id, 'update',
                                 detail=f'更新患者信息: {patient.patient_no}')
        return success_response(patient.to_dict(), '更新成功')
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f'更新失败: {str(e)}')


@patient_bp.route('/<int:patient_id>', methods=['DELETE'])
@doctor_or_admin_required
def delete_patient(patient_id):
    """删除患者档案"""
    user = get_current_user()
    try:
        patient = patient_service.get_patient_detail(patient_id)
        patient_service.delete_patient(patient_id)
        audit_logger.log_patient(user, patient_id, 'delete',
                                 detail=f'删除患者档案: {patient.patient_no}')
        return success_response(message='删除成功')
    except ValueError as e:
        return error_response(str(e))


@patient_bp.route('/<int:patient_id>/diagnoses', methods=['GET'])
@doctor_or_admin_required
def get_patient_diagnoses(patient_id):
    """获取患者诊断历史"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    try:
        pagination = patient_service.get_patient_diagnoses(patient_id, page, per_page)
        return success_response(paginate_data(pagination))
    except Exception as e:
        return error_response(f'查询失败: {str(e)}')
