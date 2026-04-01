# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 诊断业务服务
处理诊断记录的创建、查询、审核及报告生成
"""
import os
import uuid
import datetime
import logging
from openai import OpenAI
from backend.core.extensions import db
from backend.core.config import get_config
from backend.models.all_models import DiagnosisRecord, Patient
from backend.services.model_service import model_service, CLASS_NAMES_CN

logger = logging.getLogger(__name__)

# 加载配置并记录API密钥状态
_config = get_config()
_API_KEY = _config.OPENAI_API_KEY
_API_BASE = _config.OPENAI_API_BASE

# 记录API密钥加载状态
if _API_KEY:
    masked_key = f"{_API_KEY[:10]}...{_API_KEY[-4:]}" if len(_API_KEY) > 14 else "****"
    logger.info(f"阿里云通义千问API密钥已加载: {masked_key}")
    logger.info(f"API端点: {_API_BASE}")
else:
    logger.warning("未检测到OPENAI_API_KEY，报告生成功能将使用备用模式")


class DiagnosisService:
    """诊断业务服务"""

    @staticmethod
    def generate_record_no():
        """生成诊断记录编号 DX + 年月日 + 6位序号"""
        today = datetime.datetime.now().strftime('%Y%m%d')
        prefix = f'DX{today}'
        last_record = DiagnosisRecord.query.filter(
            DiagnosisRecord.record_no.like(f'{prefix}%')
        ).order_by(DiagnosisRecord.record_no.desc()).first()

        if last_record:
            seq = int(last_record.record_no[-6:]) + 1
        else:
            seq = 1

        return f'{prefix}{seq:06d}'

    @staticmethod
    def create_diagnosis(patient_id, doctor_id, image_path, image_size,
                         image_width, image_height, clinical_info='', symptoms=''):
        """
        创建诊断记录
        :return: DiagnosisRecord
        """
        try:
            # 确保模型已加载
            if not model_service.model_loaded:
                logger.warning("模型未加载，尝试自动初始化...")
                if not model_service.load_model():
                    raise RuntimeError("模型初始化失败，请检查后端日志")

            # 调用AI模型推理
            ai_result = model_service.predict(image_path)

            # 生成热力图
            from flask import current_app
            heatmap_filename = f'{uuid.uuid4().hex}.jpg'
            heatmap_dir = current_app.config.get('HEATMAP_FOLDER', 
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'heatmaps'))
            os.makedirs(heatmap_dir, exist_ok=True)
            heatmap_path = os.path.join(heatmap_dir, heatmap_filename)
            try:
                heatmap_img = model_service.generate_gradcam(image_path)
                model_service.save_heatmap(heatmap_img, heatmap_path)
            except Exception as e:
                logger.warning(f"热力图生成失败: {str(e)}")
                heatmap_path = ''

            # 创建诊断记录
            record = DiagnosisRecord(
                record_no=DiagnosisService.generate_record_no(),
                patient_id=patient_id,
                doctor_id=doctor_id,
                image_path=image_path,
                image_size=image_size,
                image_width=image_width,
                image_height=image_height,
                ai_result=ai_result['result'],
                confidence=ai_result['confidence'],
                normal_prob=ai_result['probabilities']['normal'],
                pneumonia_prob=ai_result['probabilities']['pneumonia'],
                tuberculosis_prob=ai_result['probabilities']['tuberculosis'],
                heatmap_path=heatmap_path,
                clinical_info=clinical_info,
                symptoms=symptoms,
                status='pending',
                inference_time=ai_result.get('inference_time', 0)
            )
            record.save()

            logger.info(f"诊断记录创建成功: {record.record_no}, 推理耗时: {ai_result.get('inference_time', 0):.1f}ms")
            return record

        except Exception as e:
            logger.error(f"创建诊断记录失败: {str(e)}")
            raise

    @staticmethod
    def get_diagnosis_list(page=1, per_page=20, patient_id=None, doctor_id=None,
                           result=None, status=None, start_date=None, end_date=None,
                           keyword=None):
        """查询诊断记录列表（支持多维度筛选）"""
        query = DiagnosisRecord.query.filter_by(is_deleted=False)

        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        if result:
            query = query.filter_by(ai_result=result)
        if status:
            query = query.filter_by(status=status)
        if start_date:
            query = query.filter(DiagnosisRecord.created_at >= start_date)
        if end_date:
            query = query.filter(DiagnosisRecord.created_at <= end_date)
        if keyword:
            query = query.join(Patient).filter(
                db.or_(
                    Patient.name.contains(keyword),
                    Patient.patient_no.contains(keyword),
                    DiagnosisRecord.record_no.contains(keyword)
                )
            )

        query = query.order_by(DiagnosisRecord.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination

    @staticmethod
    def get_diagnosis_detail(record_id):
        """获取诊断记录详情"""
        record = DiagnosisRecord.query.filter_by(id=record_id, is_deleted=False).first()
        if not record:
            raise ValueError('诊断记录不存在')
        return record

    @staticmethod
    def review_diagnosis(record_id, doctor_id, remark='', revised_result=None):
        """医生审核诊断记录"""
        record = DiagnosisService.get_diagnosis_detail(record_id)

        record.doctor_id = doctor_id
        record.doctor_remark = remark
        record.reviewed_at = datetime.datetime.now()

        if revised_result:
            record.revised_result = revised_result
            record.status = 'revised'
        else:
            record.status = 'confirmed'

        db.session.commit()
        logger.info(f"诊断记录审核完成: {record.record_no}, 状态: {record.status if isinstance(record.status, str) else record.status.value}")
        return record

    @staticmethod
    def delete_diagnosis(record_id):
        """软删除诊断记录"""
        record = DiagnosisService.get_diagnosis_detail(record_id)
        record.soft_delete()
        logger.info(f"诊断记录已删除: {record.record_no}")
        return True

    @staticmethod
    def generate_report(record_id):
        """
        使用阿里云通义千问API生成诊断报告
        支持qwen-plus模型，兼容备用模式
        """
        record = DiagnosisService.get_diagnosis_detail(record_id)
        patient = record.patient

        prompt = f"""你是一位资深放射科医生，请根据以下AI辅助诊断信息，生成一份规范、专业的胸部X光诊断报告。

【AI辅助诊断结果】
诊断结论：{CLASS_NAMES_CN[record.ai_result if isinstance(record.ai_result, str) else record.ai_result.value]}
置信度：{record.confidence:.1%}
概率分布：正常 {record.normal_prob:.1%}，肺炎 {record.pneumonia_prob:.1%}，肺结核 {record.tuberculosis_prob:.1%}
病史：{patient.medical_history or '无特殊病史'}
症状：{record.symptoms or '无特殊症状描述'}

请按照以下格式生成报告（纯文本）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
胸部X光诊断报告

一、检查所见
（根据诊断结果描述影像表现，如肺部纹理、密度影、渗出等）

二、诊断意见
（给出诊断结论，标注为AI辅助诊断参考）

三、建议
（给出进一步检查或随访建议）

四、声明
本报告由AI辅助诊断系统生成，仅供临床医生参考，最终诊断以临床医生意见为准。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
:"""

        # 检查API密钥是否存在
        if not _API_KEY:
            logger.warning(f"诊断报告生成使用备用模式（模板生成）: {record.record_no}")
            # 备用模式：生成模板报告
            report_content = DiagnosisService._generate_fallback_report(record, patient)
            DiagnosisService._save_report(record, report_content)
            return report_content

        try:
            # 使用阿里云通义千问API（qwen-plus模型）
            client = OpenAI(
                api_key=_API_KEY,
                base_url=_API_BASE
            )
            
            logger.info(f"正在调用通义千问API生成报告: {record.record_no}, 模型: qwen-plus")
            
            response = client.chat.completions.create(
                model='qwen-plus',  # 使用qwen-plus模型
                messages=[
                    {'role': 'system', 'content': '你是一位资深放射科医生，擅长胸部X光影像诊断。'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            report_content = response.choices[0].message.content

            # 保存报告
            DiagnosisService._save_report(record, report_content)
            logger.info(f"诊断报告生成成功: {record.record_no}")
            return report_content

        except Exception as e:
            logger.error(f"诊断报告生成失败（API调用异常）: {str(e)}")
            # API调用失败时使用备用模式
            logger.info(f"切换到备用模式生成报告: {record.record_no}")
            report_content = DiagnosisService._generate_fallback_report(record, patient)
            DiagnosisService._save_report(record, report_content)
            return report_content

    @staticmethod
    def _generate_fallback_report(record, patient):
        """
        备用模式：生成模板报告（当API密钥缺失或调用失败时）
        """
        from datetime import datetime
        
        result_cn = CLASS_NAMES_CN[record.ai_result if isinstance(record.ai_result, str) else record.ai_result.value]
        
        report = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
胸部X光诊断报告

一、检查所见
AI辅助诊断显示：{result_cn}（置信度：{record.confidence:.1%}）
概率分布：正常 {record.normal_prob:.1%}，肺炎 {record.pneumonia_prob:.1%}，肺结核 {record.tuberculosis_prob:.1%}

二、诊断意见
【AI辅助诊断参考】{result_cn}

三、建议
建议结合临床症状和其他检查结果进行综合判断，必要时进行进一步检查或随访观察。

四、声明
本报告由AI辅助诊断系统生成，仅供临床医生参考，最终诊断以临床医生意见为准。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        return report

    @staticmethod
    def _save_report(record, report_content):
        """保存报告到文件和数据库"""
        report_filename = f'report_{record.record_no}.txt'
        report_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'static', 'reports', report_filename
        )
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        record.report_content = report_content
        record.report_path = report_path
        db.session.commit()

    @staticmethod
    def get_statistics():
        """获取诊断统计数据"""
        from sqlalchemy import func
        today = datetime.datetime.now().date()
        seven_days_ago = today - datetime.timedelta(days=7)

        # 总诊断数
        total_count = DiagnosisRecord.query.filter_by(is_deleted=False).count()

        # 今日诊断数
        today_count = DiagnosisRecord.query.filter(
            DiagnosisRecord.is_deleted == False,
            func.date(DiagnosisRecord.created_at) == today
        ).count()

        # 近7天诊断数
        week_count = DiagnosisRecord.query.filter(
            DiagnosisRecord.is_deleted == False,
            func.date(DiagnosisRecord.created_at) >= seven_days_ago
        ).count()

        # 各类别统计
        result_stats = db.session.query(
            DiagnosisRecord.ai_result,
            func.count(DiagnosisRecord.id)
        ).filter_by(is_deleted=False).group_by(DiagnosisRecord.ai_result).all()

        # 近7天每日诊断量
        daily_stats = db.session.query(
            func.date(DiagnosisRecord.created_at).label('date'),
            func.count(DiagnosisRecord.id).label('count')
        ).filter(
            DiagnosisRecord.is_deleted == False,
            func.date(DiagnosisRecord.created_at) >= seven_days_ago
        ).group_by(func.date(DiagnosisRecord.created_at)).order_by(
            func.date(DiagnosisRecord.created_at)
        ).all()

        return {
            'total_count': total_count,
            'today_count': today_count,
            'week_count': week_count,
            'result_distribution': {
                r.value if not isinstance(r, str) else r: count for r, count in result_stats
            },
            'daily_stats': [
                {'date': str(d), 'count': c} for d, c in daily_stats
            ]
        }


# 全局诊断服务实例
diagnosis_service = DiagnosisService()
