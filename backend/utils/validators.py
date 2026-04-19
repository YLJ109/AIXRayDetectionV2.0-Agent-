"""数据校验工具"""
import re


def validate_username(username):
    """校验用户名：4-20位字母数字下划线"""
    return bool(re.match(r'^[a-zA-Z0-9_]{4,20}$', username))


def validate_phone(phone):
    """校验手机号"""
    return bool(re.match(r'^1[3-9]\d{9}$', phone)) if phone else True


def validate_email(email):
    """校验邮箱"""
    return bool(re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email)) if email else True


def validate_patient_no(patient_no):
    """校验患者编号"""
    return bool(patient_no and len(patient_no) <= 50)


def validate_id_card(id_card):
    """校验身份证号（简单校验）"""
    if not id_card:
        return True
    return bool(re.match(r'^\d{17}[\dXx]$', id_card))


ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm', 'dicom'}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
