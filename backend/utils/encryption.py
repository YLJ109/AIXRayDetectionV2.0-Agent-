"""AES加密工具"""
import base64
import hashlib
from cryptography.fernet import Fernet
from config import Config


def _get_fernet():
    """获取Fernet加密器"""
    key = Config.LLM_ENCRYPTION_KEY.encode()
    # 将密钥转为32字节base64编码的Fernet密钥
    hashed = hashlib.sha256(key).digest()
    fernet_key = base64.urlsafe_b64encode(hashed)
    return Fernet(fernet_key)


def encrypt_value(plain_text):
    """加密字符串"""
    if not plain_text:
        return ''
    f = _get_fernet()
    return f.encrypt(plain_text.encode()).decode()


def decrypt_value(encrypted_text):
    """解密字符串"""
    if not encrypted_text:
        return ''
    try:
        f = _get_fernet()
        return f.decrypt(encrypted_text.encode()).decode()
    except Exception:
        return ''
