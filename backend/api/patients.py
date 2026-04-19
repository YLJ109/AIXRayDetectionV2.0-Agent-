"""患者管理API"""
from flask import Blueprint, request, jsonify
from extensions import db
from models.patient import Patient
from models.audit import AuditLog
from utils.auth import token_required, role_required
from utils.validators import validate_patient_no, validate_id_card

patients_bp = Blueprint('patients', __name__, url_prefix='/api/v1/patients')


@patients_bp.route('/', methods=['GET'])
@token_required
def get_patients():
    """获取患者列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '').strip()

    query = Patient.query
    if keyword:
        query = query.filter(
            db.or_(Patient.name.like(f'%{keyword}%'),
                   Patient.patient_no.like(f'%{keyword}%'),
                   Patient.phone.like(f'%{keyword}%'),
                   Patient.id_card.like(f'%{keyword}%'))
        )

    query = query.order_by(Patient.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
        }
    })


@patients_bp.route('/<int:patient_id>', methods=['GET'])
@token_required
def get_patient(patient_id):
    """获取患者详情"""
    patient = Patient.query.get_or_404(patient_id)
    return jsonify({'code': 200, 'data': patient.to_dict()})


@patients_bp.route('/', methods=['POST'])
@token_required
def create_patient():
    """创建患者"""
    data = request.get_json()
    patient_no = data.get('patient_no', '').strip()
    name = data.get('name', '').strip()

    if not patient_no or not name:
        return jsonify({'code': 400, 'message': '患者编号和姓名不能为空'}), 400

    if Patient.query.filter_by(patient_no=patient_no).first():
        return jsonify({'code': 400, 'message': '患者编号已存在'}), 400

    patient = Patient(
        patient_no=patient_no,
        name=name,
        gender=data.get('gender'),
        birth_date=data.get('birth_date'),
        age=data.get('age'),
        id_card=data.get('id_card'),
        phone=data.get('phone'),
        address=data.get('address'),
        emergency_contact=data.get('emergency_contact'),
        emergency_phone=data.get('emergency_phone'),
        blood_type=data.get('blood_type'),
        height=data.get('height'),
        weight=data.get('weight'),
        medical_history=data.get('medical_history'),
        allergy_history=data.get('allergy_history'),
        created_by=request.current_user_id,
    )
    db.session.add(patient)
    db.session.commit()

    _log_audit(request.current_user_id, 'CREATE_PATIENT', 'patient', patient.id)
    return jsonify({'code': 200, 'data': patient.to_dict()})


@patients_bp.route('/<int:patient_id>', methods=['PUT'])
@token_required
def update_patient(patient_id):
    """更新患者信息"""
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()

    for field in ['name', 'gender', 'birth_date', 'age', 'id_card', 'phone',
                  'address', 'emergency_contact', 'emergency_phone', 'blood_type',
                  'height', 'weight', 'medical_history', 'allergy_history']:
        if field in data:
            setattr(patient, field, data[field])

    db.session.commit()
    _log_audit(request.current_user_id, 'UPDATE_PATIENT', 'patient', patient_id)
    return jsonify({'code': 200, 'data': patient.to_dict()})


@patients_bp.route('/<int:patient_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_patient(patient_id):
    """删除患者"""
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    _log_audit(request.current_user_id, 'DELETE_PATIENT', 'patient', patient_id)
    return jsonify({'code': 200, 'message': '患者已删除'})


def _log_audit(user_id, action, resource_type, resource_id):
    try:
        log = AuditLog(user_id=user_id, action=action,
                       resource_type=resource_type, resource_id=resource_id,
                       ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
