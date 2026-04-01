# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 数据库初始化脚本
创建所有数据表并初始化默认数据
包含5名医生、10名患者、系统管理员
"""
import sys
import os
import logging
import random
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.app import app
from backend.core.extensions import db
from backend.models.all_models import User, UserRole, Patient, DiagnosisRecord
from backend.services.user_service import user_service
from backend.services.patient_service import patient_service

logging.basicConfig(level=logging.INFO)


# ============ 医生数据 ============
DOCTORS = [
    {
        'username': 'doctor_wang',
        'password': 'doctor123',
        'real_name': '王建国',
        'role': 'doctor',
        'department': '放射科',
        'phone': '13812345678',
        'email': 'wangjianguo@hospital.com'
    },
    {
        'username': 'doctor_li',
        'password': 'doctor123',
        'real_name': '李秀芳',
        'role': 'doctor',
        'department': '放射科',
        'phone': '13923456789',
        'email': 'lixiufang@hospital.com'
    },
    {
        'username': 'doctor_zhang',
        'password': 'doctor123',
        'real_name': '张明远',
        'role': 'doctor',
        'department': '呼吸内科',
        'phone': '13634567890',
        'email': 'zhangmingyuan@hospital.com'
    },
    {
        'username': 'doctor_chen',
        'password': 'doctor123',
        'real_name': '陈思远',
        'role': 'doctor',
        'department': '影像科',
        'phone': '13745678901',
        'email': 'chensiyuan@hospital.com'
    },
    {
        'username': 'doctor_liu',
        'password': 'doctor123',
        'real_name': '刘婉清',
        'role': 'doctor',
        'department': '胸外科',
        'phone': '13556789012',
        'email': 'liuwanqing@hospital.com'
    },
]

# ============ 患者数据 ============
PATIENTS = [
    {
        'patient_no': 'P20260315001',
        'name': '张伟',
        'gender': 'male',
        'age': 45,
        'id_card': '320106197903152038',
        'phone': '15812341234',
        'address': '江苏省南京市玄武区中山东路128号',
        'medical_history': '高血压病史5年，规律服用降压药',
        'allergy_history': '青霉素过敏',
        'remarks': ''
    },
    {
        'patient_no': 'P20260315002',
        'name': '李娜',
        'gender': 'female',
        'age': 32,
        'id_card': '110101198905081624',
        'phone': '13698761234',
        'address': '北京市东城区东四十条22号',
        'medical_history': '无特殊病史',
        'allergy_history': '无',
        'remarks': ''
    },
    {
        'patient_no': 'P20260315003',
        'name': '王强',
        'gender': 'male',
        'age': 58,
        'id_card': '440305196501122417',
        'phone': '13987651234',
        'address': '广东省深圳市南山区科技园路66号',
        'medical_history': '2型糖尿病8年，慢性阻塞性肺疾病3年',
        'allergy_history': '磺胺类药物过敏',
        'remarks': '长期吸烟史，约20支/天'
    },
    {
        'patient_no': 'P20260315004',
        'name': '赵雪梅',
        'gender': 'female',
        'age': 67,
        'id_card': '510104195503283026',
        'phone': '13876543210',
        'address': '四川省成都市锦江区红星路三段1号',
        'medical_history': '冠心病10年，高血压15年，甲状腺功能减退',
        'allergy_history': '碘造影剂过敏',
        'remarks': ''
    },
    {
        'patient_no': 'P20260315005',
        'name': '陈志豪',
        'gender': 'male',
        'age': 28,
        'id_card': '330102199307043018',
        'phone': '15112349876',
        'address': '浙江省杭州市上城区延安路98号',
        'medical_history': '无特殊病史',
        'allergy_history': '无',
        'remarks': '职业：建筑工人，长期接触粉尘'
    },
    {
        'patient_no': 'P20260315006',
        'name': '周丽华',
        'gender': 'female',
        'age': 41,
        'id_card': '420106198106153622',
        'phone': '13723456789',
        'address': '湖北省武汉市江汉区解放大道688号',
        'medical_history': '支气管哮喘5年',
        'allergy_history': '花粉、尘螨过敏',
        'remarks': ''
    },
    {
        'patient_no': 'P20260315007',
        'name': '孙博文',
        'gender': 'male',
        'age': 73,
        'id_card': '210102194807221519',
        'phone': '13534567890',
        'address': '辽宁省沈阳市和平区太原北街55号',
        'medical_history': '肺结核病史（20年前治愈），慢性支气管炎',
        'allergy_history': '无',
        'remarks': '退休矿工，有矽尘接触史'
    },
    {
        'patient_no': 'P20260315008',
        'name': '黄晓燕',
        'gender': 'female',
        'age': 55,
        'id_card': '350104196805111428',
        'phone': '15845678901',
        'address': '福建省福州市鼓楼区五四路89号',
        'medical_history': '类风湿关节炎10年，长期服用免疫抑制剂',
        'allergy_history': '头孢类药物过敏',
        'remarks': ''
    },
    {
        'patient_no': 'P20260315009',
        'name': '刘浩然',
        'gender': 'male',
        'age': 36,
        'id_card': '610104198709064216',
        'phone': '13956789012',
        'address': '陕西省西安市碑林区南大街45号',
        'medical_history': '无特殊病史',
        'allergy_history': '无',
        'remarks': '近期有咳嗽、低热症状2周'
    },
    {
        'patient_no': 'P20260315010',
        'name': '吴美玲',
        'gender': 'female',
        'age': 49,
        'id_card': '320501197402182034',
        'phone': '13667890123',
        'address': '江苏省苏州市姑苏区人民路538号',
        'medical_history': '高血压3年，高脂血症',
        'allergy_history': '无',
        'remarks': '体检发现肺部阴影，建议进一步检查'
    },
]


def init_db():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print('[OK] 数据库表创建完成')

        # ========== 兼容性迁移：新增字段 ==========
        try:
            db.session.execute(db.text('PRAGMA table_info(diagnosis_records)'))
            columns = [row[1] for row in db.session.execute(db.text('PRAGMA table_info(diagnosis_records)')).fetchall()]
            if 'inference_time' not in columns:
                db.session.execute(db.text("ALTER TABLE diagnosis_records ADD COLUMN inference_time REAL DEFAULT 0.0"))
                db.session.commit()
                print('[OK] diagnosis_records 表新增 inference_time 字段')
        except Exception as e:
            db.session.rollback()
            print(f'[WARN] 迁移检查跳过: {str(e)}')

        # ========== 创建系统管理员 ==========
        admin_exists = User.query.filter_by(username='admin', is_deleted=False).first()
        if not admin_exists:
            user_service.create_user(
                username='admin',
                password='admin123',
                real_name='系统管理员',
                role='admin',
                department='信息科',
                phone='',
                email='admin@hospital.com'
            )
            print('[OK] 默认管理员账号创建成功 (用户名: admin, 密码: admin123)')

        # ========== 创建5名医生 ==========
        doctor_count = 0
        for doc_data in DOCTORS:
            exists = User.query.filter_by(username=doc_data['username'], is_deleted=False).first()
            if not exists:
                user_service.create_user(**doc_data)
                doctor_count += 1
                print(f'[OK] 医生创建成功: {doc_data["real_name"]} ({doc_data["department"]})')
        if doctor_count > 0:
            print(f'[OK] 共创建 {doctor_count} 名医生')
        else:
            print('[SKIP] 医生已存在，跳过创建')

        # ========== 创建10名患者 ==========
        patient_count = 0
        for pat_data in PATIENTS:
            exists = Patient.query.filter_by(patient_no=pat_data['patient_no'], is_deleted=False).first()
            if not exists:
                patient_service.create_patient(**pat_data)
                patient_count += 1
                gender_cn = '男' if pat_data['gender'] == 'male' else '女'
                print(f'[OK] 患者创建成功: {pat_data["name"]} ({gender_cn}, {pat_data["age"]}岁)')
        if patient_count > 0:
            print(f'[OK] 共创建 {patient_count} 名患者')
        else:
            print('[SKIP] 患者已存在，跳过创建')

        print('[OK] 数据库初始化完成')


if __name__ == '__main__':
    init_db()
