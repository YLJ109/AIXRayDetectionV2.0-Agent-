# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 图像预处理工具
负责胸部X光影像的加载、预处理、格式验证
"""
import os
import logging
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """图像预处理器"""

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp'}

    @staticmethod
    def is_allowed_file(filename):
        """验证文件扩展名"""
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in ImagePreprocessor.ALLOWED_EXTENSIONS

    @staticmethod
    def preprocess_image(image_path, target_size=(224, 224)):
        """
        预处理胸部X光影像
        :param image_path: 影像文件路径
        :param target_size: 目标尺寸
        :return: (preprocessed_image, width, height)
        """
        try:
            img = Image.open(image_path).convert('RGB')
            original_width, original_height = img.size

            # 保存原始尺寸信息
            width, height = original_width, original_height

            # 灰度化后转回RGB（统一3通道）
            gray = img.convert('L')

            # 对比度增强
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(gray)
            gray = enhancer.enhance(1.2)

            # 亮度调整
            enhancer = ImageEnhance.Brightness(gray)
            gray = enhancer.enhance(1.1)

            # 调整尺寸
            gray = gray.resize(target_size, Image.LANCZOS)

            # 转回RGB
            rgb_img = gray.convert('RGB')

            return rgb_img, width, height

        except Exception as e:
            logger.error(f"图像预处理失败: {str(e)}")
            raise RuntimeError(f"图像预处理失败: {str(e)}")

    @staticmethod
    def validate_medical_image(image_path):
        """
        验证是否为有效的医学影像
        :return: (is_valid, message)
        """
        try:
            if not os.path.exists(image_path):
                return False, '文件不存在'

            img = Image.open(image_path)
            img.verify()

            # 重新打开（verify后文件指针已移动）
            img = Image.open(image_path)
            width, height = img.size

            if width < 100 or height < 100:
                return False, f'图像尺寸过小: {width}x{height}'

            if width > 10000 or height > 10000:
                return False, f'图像尺寸过大: {width}x{height}'

            return True, '验证通过'

        except Exception as e:
            logger.error(f"影像验证失败: {str(e)}")
            return False, f'影像验证失败: {str(e)}'

    @staticmethod
    def get_image_info(image_path):
        """获取影像信息"""
        try:
            img = Image.open(image_path)
            file_size = os.path.getsize(image_path)
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'file_size': file_size
            }
        except Exception as e:
            logger.error(f"获取影像信息失败: {str(e)}")
            return None


image_preprocessor = ImagePreprocessor()
