"""大模型调用服务 - 报告生成 + AI咨询"""
import json
import time
from openai import OpenAI
from models.llm_config import LlmConfig
from utils.encryption import decrypt_value


def _get_llm_client(llm_config_id=None):
    """获取LLM客户端配置"""
    if llm_config_id:
        config = LlmConfig.query.get(llm_config_id)
    else:
        config = LlmConfig.query.filter_by(is_default=True, status='active').first()
        if not config:
            config = LlmConfig.query.filter_by(status='active').order_by(LlmConfig.priority).first()

    if not config:
        return None, None, None

    api_key = decrypt_value(config.api_key_encrypted)
    default_params = json.loads(config.default_params) if config.default_params else {}

    client = OpenAI(
        api_key=api_key,
        base_url=config.api_endpoint,
    )
    return client, config.model_name, default_params


def generate_report(probabilities, patient_info=None):
    """调用大模型生成结构化诊断报告

    Args:
        probabilities: 14种疾病概率列表
        patient_info: 患者信息字典

    Returns:
        dict: 包含findings, impression, recommendations的报告
    """
    client, model_name, default_params = _get_llm_client()
    if not client:
        return _generate_fallback_report(probabilities, patient_info)

    # 构建概率摘要
    top_diseases = [p for p in probabilities if p['probability'] >= 0.3][:5]
    probs_text = "\n".join([
        f"- {p['disease_name_zh']}({p['disease_code']}): {p['probability']*100:.1f}%"
        for p in probabilities
    ])

    patient_text = ""
    if patient_info:
        patient_text = f"""
患者信息：
- 姓名：{patient_info.get('name', '未知')}
- 性别：{patient_info.get('gender_zh', '未知')}
- 年龄：{patient_info.get('age', '未知')}岁
- 既往病史：{patient_info.get('medical_history', '无')}
- 临床症状：{patient_info.get('clinical_finding', '未提供')}
"""

    # CRISPE框架提示词
    prompt = f"""你是一位拥有20年经验的资深胸部放射科医师。

请根据以下AI检测结果和患者信息，生成一份专业的放射学诊断报告。

{patient_text}

该患者胸部X光影像经AI模型分析，14种疾病检测概率如下：
{probs_text}

重点关注疾病：{', '.join([p['disease_name_zh'] for p in top_diseases])}

报告需包含以下三部分，使用专业医学术语：
1. 检查所见：描述影像学表现，结合概率最高的几项疾病进行描述
2. 诊断意见：列出可能的诊断结论及对应概率，使用"提示/考虑/建议进一步检查"等谨慎表述
3. 建议：给出进一步检查或治疗的建议

请用JSON格式返回，格式如下：
{{
  "findings": "检查所见内容",
  "impression": "诊断意见内容",
  "recommendations": "建议内容"
}}"""

    try:
        temperature = default_params.get('temperature', 0.3)
        max_tokens = default_params.get('max_tokens', 2048)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是一位专业的胸部放射科医师，擅长影像诊断和报告撰写。请用中文回复。"},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content.strip()
        # 尝试解析JSON
        try:
            # 处理markdown代码块包裹
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            report = json.loads(content)
        except json.JSONDecodeError:
            report = {
                'findings': content,
                'impression': '',
                'recommendations': '',
            }

        report['ai_model_used'] = model_name
        return report

    except Exception as e:
        print(f"[LLM服务] 报告生成失败: {e}")
        return _generate_fallback_report(probabilities, patient_info)


def _generate_fallback_report(probabilities, patient_info=None):
    """备用报告生成（LLM不可用时）"""
    top = [p for p in probabilities if p['probability'] >= 0.5]
    moderate = [p for p in probabilities if 0.3 <= p['probability'] < 0.5]

    findings_parts = []
    impression_parts = []
    rec_parts = []

    if top:
        for d in top:
            findings_parts.append(f"影像提示{d['disease_name_zh']}可能，AI检测概率{d['probability']*100:.1f}%")
            impression_parts.append(f"{d['disease_name_zh']}（概率{d['probability']*100:.1f}%）")
    if moderate:
        for d in moderate:
            findings_parts.append(f"不能排除{d['disease_name_zh']}，AI检测概率{d['probability']*100:.1f}%")
            impression_parts.append(f"{d['disease_name_zh']}待排（概率{d['probability']*100:.1f}%）")

    if not top and not moderate:
        findings_parts.append("胸部X光影像未见明显异常")
        impression_parts.append("未见明显异常")

    rec_parts.append("建议结合临床表现和其他检查结果综合判断")
    # 如果有临床症状，加入相关建议
    clinical_finding = patient_info.get('clinical_finding', '') if patient_info else ''
    if clinical_finding:
        findings_parts.insert(0, f"患者主诉：{clinical_finding}")
        rec_parts.append(f"针对患者\"{clinical_finding}\"症状，建议针对性检查")
    if top:
        rec_parts.append("建议进一步行CT检查以明确诊断")
        rec_parts.append("建议相关专科会诊")

    return {
        'findings': '\n'.join(findings_parts),
        'impression': '\n'.join([f"{i+1}. {item}" for i, item in enumerate(impression_parts)]),
        'recommendations': '\n'.join([f"{i+1}. {item}" for i, item in enumerate(rec_parts)]),
        'ai_model_used': 'fallback-rule',
    }


def chat_stream(messages, llm_config_id=None, persona=None):
    """AI咨询流式对话

    Args:
        messages: 消息列表 [{"role": "user/assistant", "content": "..."}]
        llm_config_id: LLM配置ID
        persona: 医生角色预设

    Yields:
        str: 流式返回的文本片段
    """
    client, model_name, default_params = _get_llm_client(llm_config_id)
    if not client:
        yield "AI服务暂不可用，请检查大模型配置。"
        return

    system_msg = {"role": "system", "content": "你是一位专业的医学AI助手，请用中文回答医学相关问题。"}
    persona_map = {
        'radiologist': '你是一位资深胸部放射科专家，擅长影像解读、疾病鉴别诊断。',
        'respiratory': '你是一位资深呼吸科临床专家，擅长疾病诊疗方案、用药指导。',
        'thoracic': '你是一位资深胸外科专家，擅长手术指征评估、术后管理。',
        'emergency': '你是一位资深急诊科专家，擅长急危重症识别和处理。',
        'general': '你是一位全科医学顾问，擅长综合性医学咨询。',
    }
    if persona and persona in persona_map:
        system_msg = {"role": "system", "content": persona_map[persona]}

    api_messages = [system_msg] + messages[-10:]  # 保留最近10轮

    temperature = default_params.get('temperature', 0.7) if default_params else 0.7
    max_tokens = default_params.get('max_tokens', 2048) if default_params else 2048

    try:
        stream = client.chat.completions.create(
            model=model_name,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"[AI回复出错: {str(e)}]"


def triage_analyze(symptoms, severity, vital_signs=None):
    """智能分诊分析

    Args:
        symptoms: 症状列表
        severity: 严重程度
        vital_signs: 生命体征

    Returns:
        dict: 分诊结果
    """
    # 基于规则的分诊逻辑
    emergency_keywords = ['咯血', '呼吸困难', '胸痛', '意识障碍', '窒息']
    urgent_keywords = ['高热', '持续咳嗽', '大量咳痰', '气促']

    symptom_text = ' '.join(symptoms) if isinstance(symptoms, list) else symptoms

    category = '呼吸科'
    urgency = '普通'
    reasoning = []

    # 紧急程度判断
    for kw in emergency_keywords:
        if kw in symptom_text:
            urgency = '危急'
            category = '急诊科'
            reasoning.append(f"检测到危重症状: {kw}")
            break

    if urgency != '危急':
        for kw in urgent_keywords:
            if kw in symptom_text:
                urgency = '严重'
                reasoning.append(f"检测到较重症状: {kw}")
                break

    if severity == 'emergency':
        urgency = '危急'
        category = '急诊科'
    elif severity == 'severe':
        urgency = '严重'
        if category != '急诊科':
            category = '呼吸科'

    # 科室推荐
    if '心' in symptom_text or '心脏' in symptom_text:
        category = '心内科'
        reasoning.append("症状涉及心脏，建议心内科就诊")
    elif '外伤' in symptom_text or '骨折' in symptom_text:
        category = '胸外科'
        reasoning.append("症状涉及外伤，建议胸外科就诊")

    if not reasoning:
        reasoning.append("根据症状描述，建议呼吸科常规就诊")

    return {
        'category': category,
        'urgency': urgency,
        'reasoning': '；'.join(reasoning),
    }
