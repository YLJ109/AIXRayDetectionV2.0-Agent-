"""报告生成服务"""
import os
from datetime import datetime
from services.llm_service import generate_report
from services.ai_service import CLASS_NAMES, CN_NAMES


def create_diagnosis_report(probabilities, patient_info=None, llm_config_id=None):
    """生成完整的诊断报告

    Args:
        probabilities: 14种疾病概率列表
        patient_info: 患者信息
        llm_config_id: LLM配置ID

    Returns:
        dict: 完整报告
    """
    # 调用LLM生成报告
    report = generate_report(probabilities, patient_info)

    # 构建完整报告文本
    full_text = f"""检查所见：
{report.get('findings', '')}

诊断意见：
{report.get('impression', '')}

建议：
{report.get('recommendations', '')}
"""

    return {
        'ai_generated_content': full_text,
        'findings': report.get('findings', ''),
        'impression': report.get('impression', ''),
        'recommendations': report.get('recommendations', ''),
        'ai_model_used': report.get('ai_model_used', 'unknown'),
    }
