# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 大模型API统一管理服务
支持多种大模型API（豆包、DeepSeek、ChatGPT等）的统一调用
"""
import os
import json
import time
import logging
import hashlib
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import requests

logger = logging.getLogger(__name__)


class LLMService:
    """大模型API统一管理服务"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._cipher = None
        self._init_encryption()
    
    def _init_encryption(self):
        """初始化加密器"""
        # 使用环境变量或默认密钥进行加密
        secret_key = os.environ.get('LLM_ENCRYPTION_KEY', 'aixray-llm-encryption-secret-key-2024')
        salt = b'aixray_llm_salt_v2'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self._cipher = Fernet(key)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """加密API密钥"""
        if not api_key:
            return ''
        return self._cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """解密API密钥"""
        if not encrypted_key:
            return ''
        try:
            return self._cipher.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            logger.error(f"解密API密钥失败: {str(e)}")
            return ''
    
    def validate_provider_config(self, provider_type: str, config: dict) -> tuple:
        """
        验证提供商配置
        :return: (is_valid, error_message)
        """
        required_fields = {
            'openai': ['api_key', 'api_endpoint'],
            'anthropic': ['api_key', 'api_endpoint'],
            'doubao': ['api_key', 'api_endpoint'],
            'deepseek': ['api_key', 'api_endpoint'],
            'qwen': ['api_key', 'api_endpoint'],  # 阿里云通义千问
            'custom': ['api_key', 'api_endpoint']
        }
        
        if provider_type not in required_fields:
            return False, f"不支持的提供商类型: {provider_type}"
        
        for field in required_fields[provider_type]:
            if not config.get(field):
                return False, f"缺少必填字段: {field}"
        
        # 验证URL格式
        api_endpoint = config.get('api_endpoint', '')
        if not api_endpoint.startswith(('http://', 'https://')):
            return False, "API端点必须是有效的HTTP/HTTPS URL"
        
        return True, ''
    
    def get_default_endpoint(self, provider_type: str) -> str:
        """获取默认API端点"""
        endpoints = {
            'openai': 'https://api.openai.com/v1/chat/completions',
            'anthropic': 'https://api.anthropic.com/v1/messages',
            'doubao': 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
            'deepseek': 'https://api.deepseek.com/v1/chat/completions',
            'qwen': 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',  # 阿里云通义千问
        }
        return endpoints.get(provider_type, '')
    
    def get_default_model(self, provider_type: str) -> str:
        """获取默认模型名称"""
        models = {
            'openai': 'gpt-3.5-turbo',
            'anthropic': 'claude-3-sonnet-20240229',
            'doubao': 'doubao-pro-32k',
            'deepseek': 'deepseek-chat',
            'qwen': 'qwen-plus',  # 阿里云通义千问默认使用qwen-plus
        }
        return models.get(provider_type, '')
    
    def build_request(self, provider_type: str, api_key: str, messages: list, default_model: str = '', **kwargs):
        """
        构建API请求
        :param provider_type: 提供商类型
        :param api_key: API密钥
        :param messages: 消息列表
        :param default_model: 提供商配置的默认模型名称
        :param kwargs: 其他参数（temperature, max_tokens等）
        :return: (headers, data)
        """
        # 使用 or 运算符确保 None 值也能回退到默认值
        model = kwargs.get('model') or default_model or self.get_default_model(provider_type)
        temperature = kwargs.get('temperature') or 0.7
        max_tokens = kwargs.get('max_tokens') or 2000

        if not model:
            raise ValueError(f"未指定模型名称，且无法获取 {provider_type} 的默认模型")

        logger.info(f"构建LLM请求: provider={provider_type}, model={model}, temperature={temperature}, max_tokens={max_tokens}")

        default_config = {
            'temperature': temperature,
            'max_tokens': max_tokens,
            'model': model
        }
        
        if provider_type == 'openai':
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': default_config['model'],
                'messages': messages,
                'temperature': default_config['temperature'],
                'max_tokens': default_config['max_tokens']
            }
            return headers, data
        
        elif provider_type == 'anthropic':
            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            data = {
                'model': default_config['model'],
                'messages': messages,
                'max_tokens': default_config['max_tokens']
            }
            return headers, data
        
        elif provider_type in ['doubao', 'deepseek', 'qwen']:  # qwen使用OpenAI兼容格式
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': default_config['model'],
                'messages': messages,
                'temperature': default_config['temperature'],
                'max_tokens': default_config['max_tokens']
            }
            return headers, data
        
        else:  # custom
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': default_config['model'],
                'messages': messages,
                'temperature': default_config['temperature'],
                'max_tokens': default_config['max_tokens']
            }
            return headers, data
    
    def call_api(self, provider, messages: list, **kwargs):
        """
        统一调用API
        :param provider: LLMProvider对象
        :param messages: 消息列表
        :param kwargs: 其他参数
        :return: dict 包含响应内容和元数据
        """
        start_time = time.time()
        
        try:
            # 解密API密钥
            api_key = self.decrypt_api_key(provider.api_key_encrypted)
            if not api_key:
                raise ValueError("API密钥解密失败")
            
            # 解析配置
            config = json.loads(provider.config_json) if provider.config_json else {}
            # kwargs（用户显式传参）优先级高于 config（数据库默认配置）
            merged_kwargs = {**config, **kwargs}
            # 过滤掉 None 值，避免覆盖有效默认值
            merged_kwargs = {k: v for k, v in merged_kwargs.items() if v is not None}
            
            # 构建请求
            headers, data = self.build_request(
                provider.provider_type,
                api_key,
                messages,
                default_model=provider.default_model or '',
                **merged_kwargs
            )
            
            # 发送请求
            response = requests.post(
                provider.api_endpoint,
                headers=headers,
                json=data,
                timeout=60
            )
            
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                error_msg = f"API调用失败: HTTP {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'response_time': response_time
                }
            
            # 解析响应
            result = response.json()
            
            # 提取内容（不同提供商响应格式略有不同）
            content = ''
            tokens = {'prompt': 0, 'completion': 0, 'total': 0}
            
            if provider.provider_type == 'anthropic':
                content = result.get('content', [{}])[0].get('text', '')
                tokens = {
                    'prompt': result.get('usage', {}).get('input_tokens', 0),
                    'completion': result.get('usage', {}).get('output_tokens', 0),
                    'total': result.get('usage', {}).get('input_tokens', 0) + result.get('usage', {}).get('output_tokens', 0)
                }
            else:  # openai格式
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                tokens = {
                    'prompt': result.get('usage', {}).get('prompt_tokens', 0),
                    'completion': result.get('usage', {}).get('completion_tokens', 0),
                    'total': result.get('usage', {}).get('total_tokens', 0)
                }
            
            return {
                'success': True,
                'content': content,
                'model': result.get('model', ''),
                'tokens': tokens,
                'response_time': response_time,
                'raw_response': result
            }
            
        except requests.exceptions.Timeout:
            error_msg = "API调用超时"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'response_time': time.time() - start_time
            }
        except Exception as e:
            error_msg = f"API调用异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'response_time': time.time() - start_time
            }
    
    def test_connection(self, provider):
        """
        测试连接
        :param provider: LLMProvider对象
        :return: dict 包含测试结果
        """
        test_messages = [
            {'role': 'user', 'content': '你好，请回复"连接成功"'}
        ]
        
        result = self.call_api(provider, test_messages, max_tokens=50)
        
        if result['success']:
            return {
                'success': True,
                'message': '连接测试成功',
                'response_time': result['response_time'],
                'response_content': result.get('content', '')
            }
        else:
            return {
                'success': False,
                'message': f"连接测试失败: {result.get('error', '未知错误')}",
                'response_time': result.get('response_time', 0)
            }


# 全局服务实例
llm_service = LLMService()
