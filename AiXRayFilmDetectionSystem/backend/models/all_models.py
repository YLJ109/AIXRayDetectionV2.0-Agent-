# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 所有业务数据模型
包含用户、患者、诊断记录、审计日志等模型
使用 String 列存储枚举值，确保 SQLite 兼容性
"""
import os
import enum
from datetime import datetime
from backend.core.extensions import db
from backend.models.database import BaseModel


class UserRole(enum.Enum):
    """用户角色枚举"""
    ADMIN = 'admin'
    DOCTOR = 'doctor'
    NURSE = 'nurse'


class GenderEnum(enum.Enum):
    """性别枚举"""
    MALE = 'male'
    FEMALE = 'female'


class DiagnosisResult(enum.Enum):
    """诊断结果枚举"""
    NORMAL = 'normal'
    PNEUMONIA = 'pneumonia'
    TUBERCULOSIS = 'tuberculosis'


class DiagnosisStatus(enum.Enum):
    """诊断状态枚举"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    REVISED = 'revised'


# ============ 用户模型 ============
class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'

    username = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='用户名')
    password_hash = db.Column(db.String(256), nullable=False, comment='密码哈希')
    real_name = db.Column(db.String(50), nullable=False, comment='真实姓名')
    role = db.Column(db.String(20), default='doctor', nullable=False, comment='用户角色')
    department = db.Column(db.String(100), default='', comment='所属科室')
    phone = db.Column(db.String(20), default='', comment='联系电话')
    email = db.Column(db.String(100), default='', comment='电子邮箱')
    avatar = db.Column(db.String(500), default='', comment='用户头像URL')
    is_active = db.Column(db.Boolean, default=True, nullable=False, comment='是否启用')
    last_login_at = db.Column(db.DateTime, comment='最后登录时间')

    # 关联
    diagnoses = db.relationship('DiagnosisRecord', backref='doctor', lazy='dynamic',
                                foreign_keys='DiagnosisRecord.doctor_id')

    def __repr__(self):
        return f'<User {self.username}>'


# ============ 患者模型 ============
class Patient(BaseModel):
    """患者模型"""
    __tablename__ = 'patients'

    patient_no = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='患者编号')
    name = db.Column(db.String(100), nullable=False, comment='姓名')
    gender = db.Column(db.String(10), nullable=False, comment='性别')
    age = db.Column(db.Integer, nullable=False, comment='年龄')
    id_card = db.Column(db.String(18), default='', comment='身份证号（加密存储）')
    phone = db.Column(db.String(20), default='', comment='联系电话')
    address = db.Column(db.String(255), default='', comment='地址')
    medical_history = db.Column(db.Text, default='', comment='病史记录')
    allergy_history = db.Column(db.Text, default='', comment='过敏史')
    remarks = db.Column(db.Text, default='', comment='备注')

    # 关联
    diagnoses = db.relationship('DiagnosisRecord', backref='patient', lazy='dynamic')

    def __repr__(self):
        return f'<Patient {self.patient_no} - {self.name}>'


# ============ 诊断记录模型 ============
class DiagnosisRecord(BaseModel):
    """诊断记录模型"""
    __tablename__ = 'diagnosis_records'

    record_no = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='记录编号')
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True, comment='患者ID')
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, comment='医生ID')

    # 影像信息
    image_path = db.Column(db.String(500), nullable=False, comment='影像文件路径')
    image_size = db.Column(db.Integer, default=0, comment='影像文件大小(bytes)')
    image_width = db.Column(db.Integer, default=0, comment='影像宽度')
    image_height = db.Column(db.Integer, default=0, comment='影像高度')

    # AI诊断结果
    ai_result = db.Column(db.String(20), nullable=False, comment='AI诊断结果')
    confidence = db.Column(db.Float, nullable=False, comment='诊断置信度(0-1)')
    normal_prob = db.Column(db.Float, default=0.0, comment='正常概率')
    pneumonia_prob = db.Column(db.Float, default=0.0, comment='肺炎概率')
    tuberculosis_prob = db.Column(db.Float, default=0.0, comment='肺结核概率')

    # 推理耗时
    inference_time = db.Column(db.Float, default=0.0, comment='AI推理耗时(毫秒)')

    # 热力图
    heatmap_path = db.Column(db.String(500), default='', comment='Grad-CAM热力图路径')

    # 临床信息（多模态融合）
    clinical_info = db.Column(db.Text, default='', comment='临床补充信息')
    symptoms = db.Column(db.String(500), default='', comment='症状描述')

    # 医生审核
    status = db.Column(db.String(20), default='pending', comment='诊断状态')
    doctor_remark = db.Column(db.Text, default='', comment='医生备注')
    revised_result = db.Column(db.String(20), nullable=True, comment='医生修正结果')
    reviewed_at = db.Column(db.DateTime, comment='审核时间')

    # 诊断报告
    report_path = db.Column(db.String(500), default='', comment='诊断报告路径')
    report_content = db.Column(db.Text, default='', comment='诊断报告内容(纯文本)')

    def to_dict(self, exclude=None):
        """转换为字典，image_path和heatmap_path只返回文件名"""
        data = super().to_dict(exclude=exclude)
        if self.image_path:
            # 只返回文件名，前端会拼接为 /api/diagnosis/image/{filename}
            data['image_path'] = os.path.basename(self.image_path)
        if self.heatmap_path:
            # 只返回文件名，前端会拼接为 /api/diagnosis/heatmap/{filename}
            data['heatmap_path'] = os.path.basename(self.heatmap_path)
        return data

    def __repr__(self):
        return f'<DiagnosisRecord {self.record_no}>'


# ============ 审计日志模型 ============
class AuditLog(BaseModel):
    """审计日志模型"""
    __tablename__ = 'audit_logs'

    user_id = db.Column(db.Integer, nullable=True, index=True, comment='操作用户ID')
    username = db.Column(db.String(50), default='', comment='操作用户名')
    action = db.Column(db.String(50), nullable=False, index=True, comment='操作类型')
    resource_type = db.Column(db.String(50), default='', comment='资源类型')
    resource_id = db.Column(db.Integer, default=0, comment='资源ID')
    detail = db.Column(db.Text, default='', comment='操作详情')
    ip_address = db.Column(db.String(50), default='', comment='IP地址')
    user_agent = db.Column(db.String(500), default='', comment='用户代理')

    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action}>'


# ============ 系统配置模型 ============
class SystemConfig(BaseModel):
    """系统配置模型"""
    __tablename__ = 'system_configs'

    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='配置键')
    config_value = db.Column(db.Text, default='', comment='配置值')
    config_type = db.Column(db.String(20), default='string', comment='配置类型(string/number/boolean/json)')
    description = db.Column(db.String(255), default='', comment='配置说明')
    group_name = db.Column(db.String(50), default='general', comment='配置分组')

    def __repr__(self):
        return f'<SystemConfig {self.config_key}>'


# ============ 大模型提供商模型 ============
class LLMProvider(BaseModel):
    """大模型API提供商配置"""
    __tablename__ = 'llm_providers'

    name = db.Column(db.String(50), nullable=False, comment='提供商名称')
    provider_type = db.Column(db.String(30), nullable=False, comment='提供商类型(openai/anthropic/doubao/deepseek/custom)')
    api_key_encrypted = db.Column(db.Text, nullable=False, comment='加密存储的API密钥')
    api_endpoint = db.Column(db.String(500), nullable=False, comment='API端点URL')
    default_model = db.Column(db.String(100), default='', comment='默认模型名称')
    config_json = db.Column(db.Text, default='{}', comment='其他配置参数JSON(temperature/max_tokens等)')
    is_active = db.Column(db.Boolean, default=True, nullable=False, comment='是否启用')
    priority = db.Column(db.Integer, default=0, comment='优先级(数字越大优先级越高)')
    last_used_at = db.Column(db.DateTime, comment='最后使用时间')
    total_calls = db.Column(db.Integer, default=0, comment='累计调用次数')
    last_error = db.Column(db.Text, default='', comment='最后一次错误信息')

    def __repr__(self):
        return f'<LLMProvider {self.name}>'


# ============ LLM调用记录模型 ============
class LLMCallLog(BaseModel):
    """大模型调用日志"""
    __tablename__ = 'llm_call_logs'

    provider_id = db.Column(db.Integer, db.ForeignKey('llm_providers.id'), nullable=False, index=True, comment='提供商ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, comment='调用用户ID')
    model_name = db.Column(db.String(100), default='', comment='使用的模型名称')
    prompt_tokens = db.Column(db.Integer, default=0, comment='提示词token数')
    completion_tokens = db.Column(db.Integer, default=0, comment='补全token数')
    total_tokens = db.Column(db.Integer, default=0, comment='总token数')
    response_time = db.Column(db.Float, default=0.0, comment='响应时间(秒)')
    is_success = db.Column(db.Boolean, default=True, nullable=False, comment='是否成功')
    error_message = db.Column(db.Text, default='', comment='错误信息')

    # 关联
    provider = db.relationship('LLMProvider', backref='call_logs')
    user = db.relationship('User', backref='llm_calls')

    def __repr__(self):
        return f'<LLMCallLog {self.id}>'


