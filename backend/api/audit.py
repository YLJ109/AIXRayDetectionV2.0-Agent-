"""审计日志API"""
from flask import Blueprint, request, jsonify
from extensions import db
from models.audit import AuditLog
from utils.auth import token_required, role_required

audit_bp = Blueprint('audit', __name__, url_prefix='/api/v1/audit')


@audit_bp.route('/logs', methods=['GET'])
@token_required
@role_required('admin')
def get_logs():
    """获取审计日志列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    action = request.args.get('action')
    keyword = request.args.get('keyword', '').strip()
    resource_type = request.args.get('resource_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = AuditLog.query

    if action:
        query = query.filter_by(action=action)
    if keyword:
        query = query.filter(AuditLog.username.ilike(f'%{keyword}%'))
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)

    query = query.order_by(AuditLog.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [l.to_dict() for l in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
        }
    })


@audit_bp.route('/actions', methods=['GET'])
@token_required
@role_required('admin')
def get_action_types():
    """获取所有操作类型"""
    actions = db.session.query(AuditLog.action).distinct().all()
    return jsonify({
        'code': 200,
        'data': [a[0] for a in actions]
    })
