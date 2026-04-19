"""LLM直接对话API - 非流式，供AI咨询和智能分诊使用"""
import time
from flask import Blueprint, request, jsonify
from utils.auth import token_required
from services.llm_service import _get_llm_client

llm_bp = Blueprint('llm', __name__, url_prefix='/api/v1/llm')


@llm_bp.route('/chat', methods=['POST'])
@token_required
def chat():
    """直接调用LLM对话接口（非流式）

    请求体:
    {
        "messages": [{"role": "system/user/assistant", "content": "..."}],
        "temperature": 0.7,  // 可选
        "max_tokens": 2000   // 可选
    }

    返回:
    {
        "success": true,
        "content": "AI回复内容",
        "model": "模型名称",
        "tokens": {"prompt": N, "completion": N, "total": N},
        "response_time": 1.23
    }
    """
    data = request.get_json()
    messages = data.get('messages', [])

    if not messages:
        return jsonify({'success': False, 'error': '消息不能为空'}), 400

    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 2000)

    client, model_name, default_params = _get_llm_client()
    if not client:
        return jsonify({
            'success': False,
            'error': 'AI服务暂不可用，请检查大模型配置',
        }), 503

    # 使用默认参数作为基础，请求参数覆盖
    if default_params:
        temperature = temperature or default_params.get('temperature', 0.7)
        max_tokens = max_tokens or default_params.get('max_tokens', 2048)

    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        elapsed = round(time.time() - start_time, 2)

        content = response.choices[0].message.content.strip()
        tokens = {}
        if hasattr(response, 'usage') and response.usage:
            tokens = {
                'prompt': getattr(response.usage, 'prompt_tokens', 0),
                'completion': getattr(response.usage, 'completion_tokens', 0),
                'total': getattr(response.usage, 'total_tokens', 0),
            }

        return jsonify({
            'success': True,
            'content': content,
            'model': model_name,
            'tokens': tokens,
            'response_time': elapsed,
        })
    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        return jsonify({
            'success': False,
            'error': str(e),
            'model': model_name,
            'response_time': elapsed,
        }), 500
