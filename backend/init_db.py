"""数据库初始化脚本 - 参考V2.0丰富患者和医生数据"""
import os
import sys
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import *
from models.settings import SystemSetting, UserPreference


def init_db():
    """初始化数据库和默认数据"""
    app = create_app()

    with app.app_context():
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)

        db.create_all()
        print("[数据库] 所有表已创建")

        # ======================== 用户 ========================
        users_data = [
            # 管理员
            dict(username='admin', password='admin123', real_name='系统管理员',
                 role='admin', department='信息科', email='admin@hospital.com', status='active'),
            # 5名医生 (参考V2.0)
            dict(username='doctor_wang', password='doctor123', real_name='王建国',
                 role='doctor', department='放射科', license_number='YS20240001',
                 phone='13812345678', email='wangjianguo@hospital.com', status='active'),
            dict(username='doctor_li', password='doctor123', real_name='李秀芳',
                 role='doctor', department='放射科', license_number='YS20240002',
                 phone='13923456789', email='lixiufang@hospital.com', status='active'),
            dict(username='doctor_zhang', password='doctor123', real_name='张明远',
                 role='doctor', department='呼吸内科', license_number='YS20240003',
                 phone='13634567890', email='zhangmingyuan@hospital.com', status='active'),
            dict(username='doctor_chen', password='doctor123', real_name='陈思远',
                 role='doctor', department='影像科', license_number='YS20240004',
                 phone='13745678901', email='chensiyuan@hospital.com', status='active'),
            dict(username='doctor_liu', password='doctor123', real_name='刘婉清',
                 role='doctor', department='胸外科', license_number='YS20240005',
                 phone='13556789012', email='liuwanqing@hospital.com', status='active'),
            # 2名护士
            dict(username='nurse_sun', password='nurse123', real_name='孙小美',
                 role='nurse', department='放射科', phone='15812341234', status='active'),
            dict(username='nurse_zhao', password='nurse123', real_name='赵雅婷',
                 role='nurse', department='呼吸内科', phone='15923456789', status='active'),
        ]
        for u in users_data:
            if not User.query.filter_by(username=u['username']).first():
                pwd = u.pop('password')
                user = User(password_hash=generate_password_hash(pwd), **u)
                db.session.add(user)
                db.session.flush()
                db.session.add(UserPreference(user_id=user.id, theme='dark'))
        print("[数据库] 用户数据已创建 (1管理员+5医生+2护士)")

        # ======================== 10名患者 (参考V2.0) ========================
        patients_data = [
            dict(patient_no='P20260315001', name='张伟', gender='male', age=45,
                 id_card='320106197903152038', phone='15812341234',
                 address='江苏省南京市玄武区中山东路128号',
                 medical_history='高血压病史5年，规律服用降压药',
                 allergy_history='青霉素过敏'),
            dict(patient_no='P20260315002', name='李娜', gender='female', age=32,
                 id_card='110101198905081624', phone='13698761234',
                 address='北京市东城区东四十条22号',
                 medical_history='无特殊病史', allergy_history='无'),
            dict(patient_no='P20260315003', name='王强', gender='male', age=58,
                 id_card='440305196501122417', phone='13987651234',
                 address='广东省深圳市南山区科技园路66号',
                 medical_history='2型糖尿病8年，慢性阻塞性肺疾病3年',
                 allergy_history='磺胺类药物过敏'),
            dict(patient_no='P20260315004', name='赵雪梅', gender='female', age=67,
                 id_card='510104195503283026', phone='13876543210',
                 address='四川省成都市锦江区红星路三段1号',
                 medical_history='冠心病10年，高血压15年，甲状腺功能减退',
                 allergy_history='碘造影剂过敏'),
            dict(patient_no='P20260315005', name='陈志豪', gender='male', age=28,
                 id_card='330102199307043018', phone='15112349876',
                 address='浙江省杭州市上城区延安路98号',
                 medical_history='无特殊病史', allergy_history='无'),
            dict(patient_no='P20260315006', name='周丽华', gender='female', age=41,
                 id_card='420106198106153622', phone='13723456789',
                 address='湖北省武汉市江汉区解放大道688号',
                 medical_history='支气管哮喘5年',
                 allergy_history='花粉、尘螨过敏'),
            dict(patient_no='P20260315007', name='孙博文', gender='male', age=73,
                 id_card='210102194807221519', phone='13534567890',
                 address='辽宁省沈阳市和平区太原北街55号',
                 medical_history='肺结核病史（20年前治愈），慢性支气管炎',
                 allergy_history='无'),
            dict(patient_no='P20260315008', name='黄晓燕', gender='female', age=55,
                 id_card='350104196805111428', phone='15845678901',
                 address='福建省福州市鼓楼区五四路89号',
                 medical_history='类风湿关节炎10年，长期服用免疫抑制剂',
                 allergy_history='头孢类药物过敏'),
            dict(patient_no='P20260315009', name='刘浩然', gender='male', age=36,
                 id_card='610104198709064216', phone='13956789012',
                 address='陕西省西安市碑林区南大街45号',
                 medical_history='无特殊病史', allergy_history='无'),
            dict(patient_no='P20260315010', name='吴美玲', gender='female', age=49,
                 id_card='320501197402182034', phone='13667890123',
                 address='江苏省苏州市姑苏区人民路538号',
                 medical_history='高血压3年，高脂血症', allergy_history='无'),
        ]
        for p in patients_data:
            if not Patient.query.filter_by(patient_no=p['patient_no']).first():
                patient = Patient(**p)
                db.session.add(patient)
        print("[数据库] 10名患者数据已创建")

        # ======================== 大模型配置 ========================
        if not LlmConfig.query.first():
            from utils.encryption import encrypt_value
            llm = LlmConfig(
                model_name='qwen-plus', provider='qwen',
                api_endpoint='https://dashscope.aliyuncs.com/compatible-mode/v1',
                api_key_encrypted=encrypt_value(app.config.get('OPENAI_API_KEY', '')),
                default_params='{"temperature": 0.3, "max_tokens": 2048}',
                is_default=True, priority=1, status='active',
            )
            db.session.add(llm)
            print("[数据库] 默认大模型配置已创建")

        # ======================== 系统设置 ========================
        default_settings = {
            'system_name': ('胸影智诊V3.0', 'string', '系统名称'),
            'disease_threshold': ('0.7', 'float', '疾病概率告警阈值'),
            'max_upload_size': ('20', 'int', '最大上传文件大小(MB)'),
            'session_timeout': ('12', 'int', '会话超时时间(小时)'),
            'audit_retention_days': ('180', 'int', '审计日志保留天数'),
            'batch_concurrency': ('2', 'int', '批量处理并发数'),
        }
        for key, (value, vtype, desc) in default_settings.items():
            if not SystemSetting.query.filter_by(setting_key=key).first():
                db.session.add(SystemSetting(
                    setting_key=key, setting_value=value,
                    value_type=vtype, description=desc,
                ))
        print("[数据库] 默认系统设置已创建")

        db.session.commit()
        print("[数据库] 初始化完成!")


if __name__ == '__main__':
    init_db()
