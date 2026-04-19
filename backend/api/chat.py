"""AI咨询API"""
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, Response, stream_with_context
from extensions import db
from models.chat import AiChatSession, AiChatMessage
from models.audit import AuditLog
from utils.auth import token_required
from services.llm_service import chat_stream

chat_bp = Blueprint('chat', __name__, url_prefix='/api/v1/chat')


@chat_bp.route('/sessions', methods=['GET'])
@token_required
def get_sessions():
    """获取会话列表"""
    sessions = AiChatSession.query.filter_by(
        user_id=request.current_user_id, is_active=True
    ).order_by(AiChatSession.last_message_at.desc().nullsfirst()).all()

    return jsonify({
        'code': 200,
        'data': [s.to_dict() for s in sessions]
    })


@chat_bp.route('/sessions', methods=['POST'])
@token_required
def create_session():
    """创建新会话"""
    data = request.get_json()
    session_no = f"CH{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:4].upper()}"

    session = AiChatSession(
        session_no=session_no,
        user_id=request.current_user_id,
        doctor_persona=data.get('persona', 'radiologist'),
        title=data.get('title', '新会话'),
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({'code': 200, 'data': session.to_dict()})


@chat_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@token_required
def delete_session(session_id):
    """删除（关闭）会话"""
    session = AiChatSession.query.filter_by(
        id=session_id, user_id=request.current_user_id
    ).first_or_404()
    session.is_active = False
    db.session.commit()
    return jsonify({'code': 200, 'message': '会话已关闭'})


@chat_bp.route('/sessions/<int:session_id>/messages', methods=['GET'])
@token_required
def get_messages(session_id):
    """获取会话消息"""
    session = AiChatSession.query.filter_by(
        id=session_id, user_id=request.current_user_id
    ).first_or_404()

    messages = AiChatMessage.query.filter_by(session_id=session_id)\
        .order_by(AiChatMessage.created_at.asc()).all()

    return jsonify({
        'code': 200,
        'data': [m.to_dict() for m in messages]
    })


@chat_bp.route('/sessions/<int:session_id>/send', methods=['POST'])
@token_required
def send_message(session_id):
    """发送消息（流式返回）"""
    session = AiChatSession.query.filter_by(
        id=session_id, user_id=request.current_user_id
    ).first_or_404()

    data = request.get_json()
    user_content = data.get('content', '').strip()

    if not user_content:
        return jsonify({'code': 400, 'message': '消息不能为空'}), 400

    # 保存用户消息
    user_msg = AiChatMessage(
        session_id=session_id,
        role='user',
        content=user_content,
    )
    db.session.add(user_msg)

    # 更新会话标题（首条消息）
    if not session.title or session.title == '新会话':
        session.title = user_content[:50]
    session.last_message_at = datetime.now()
    db.session.commit()

    # 获取历史消息
    history = AiChatMessage.query.filter_by(session_id=session_id)\
        .order_by(AiChatMessage.created_at.asc()).all()
    messages = [{"role": m.role, "content": m.content} for m in history]

    # 流式响应
    def generate():
        full_response = ""
        for chunk in chat_stream(messages, persona=session.doctor_persona):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"

        # 保存AI回复
        ai_msg = AiChatMessage(
            session_id=session_id,
            role='assistant',
            content=full_response,
            llm_model='qwen',
        )
        db.session.add(ai_msg)
        db.session.commit()

        yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )
