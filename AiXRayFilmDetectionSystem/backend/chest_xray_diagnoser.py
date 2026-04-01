# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 胸部X光诊断推理模块
基于MobileNetV2预训练模型的独立诊断工具

功能：
- 加载.pth格式预训练模型
- 预处理X光影像
- 执行AI推理
- 输出结构化诊断结果

作者：胸影智诊开发团队
版本：2.0.0
"""
import os
import logging
from dataclasses import dataclass
from typing import Optional, Union, BinaryIO
from pathlib import Path

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from torchvision import transforms, models

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DiagnosisResult:
    """诊断结果数据类"""
    conclusion: str              # 诊断结论 (正常/肺炎/肺结核)
    conclusion_en: str           # 英文诊断结论
    confidence: float            # 置信度 (0-1)
    confidence_percent: float    # 置信度百分比
    probabilities: dict          # 各类别概率
    inference_time_ms: float     # 推理耗时(毫秒)
    success: bool                # 是否成功
    error_message: str = ""      # 错误信息

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'conclusion': self.conclusion,
            'conclusion_en': self.conclusion_en,
            'confidence': self.confidence,
            'confidence_percent': self.confidence_percent,
            'probabilities': self.probabilities,
            'inference_time_ms': self.inference_time_ms,
            'success': self.success,
            'error_message': self.error_message
        }

    def __str__(self) -> str:
        """字符串表示"""
        if not self.success:
            return f"诊断失败: {self.error_message}"
        return (
            f"诊断结论: {self.conclusion} "
            f"(置信度: {self.confidence_percent:.1f}%)\n"
            f"  - 正常概率: {self.probabilities['normal']*100:.1f}%\n"
            f"  - 肺炎概率: {self.probabilities['pneumonia']*100:.1f}%\n"
            f"  - 肺结核概率: {self.probabilities['tuberculosis']*100:.1f}%"
        )


class ChestXrayDiagnoser:
    """
    胸部X光AI诊断器
    
    使用预训练的MobileNetV2模型进行胸部X光影像诊断
    
    Attributes:
        model_path: 模型文件路径
        device: 计算设备 (cuda/cpu)
        model: 加载的PyTorch模型
        transform: 图像预处理变换
    """
    
    # 类别映射
    CLASS_NAMES = {
        0: 'normal',
        1: 'pneumonia', 
        2: 'tuberculosis'
    }
    
    CLASS_NAMES_CN = {
        'normal': '正常',
        'pneumonia': '肺炎',
        'tuberculosis': '肺结核'
    }
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        num_classes: int = 3,
        image_size: int = 224
    ):
        """
        初始化诊断器
        
        Args:
            model_path: 预训练模型文件路径 (.pth)
            device: 计算设备 ('cuda', 'cpu', 或 None自动选择)
            num_classes: 分类数量 (默认3类: 正常/肺炎/肺结核)
            image_size: 输入图像尺寸 (默认224)
        """
        self.model_path = model_path
        self.num_classes = num_classes
        self.image_size = image_size
        self.model = None
        
        # 设置计算设备
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        logger.info(f"诊断器初始化 - 设备: {self.device}")
        
        # 初始化图像预处理
        self._init_transform()
        
        # 如果提供了模型路径，自动加载
        if model_path:
            self.load_model(model_path)
    
    def _init_transform(self) -> None:
        """初始化图像预处理变换"""
        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.Grayscale(num_output_channels=3),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def load_model(self, model_path: str) -> bool:
        """
        加载预训练模型
        
        Args:
            model_path: 模型权重文件路径 (.pth)
            
        Returns:
            bool: 加载是否成功
            
        Raises:
            FileNotFoundError: 模型文件不存在
            RuntimeError: 模型加载失败
        """
        try:
            # 验证文件存在
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"模型文件不存在: {model_path}")
            
            logger.info(f"正在加载模型: {model_path}")
            
            # 创建MobileNetV2模型架构
            self.model = models.mobilenet_v2(weights=None)
            
            # 修改分类层为指定类别数
            num_features = self.model.classifier[1].in_features
            self.model.classifier[1] = torch.nn.Linear(num_features, self.num_classes)
            
            # 加载权重
            state_dict = torch.load(
                model_path, 
                map_location=self.device,
                weights_only=True  # 安全加载
            )
            self.model.load_state_dict(state_dict, strict=False)
            
            # 设置评估模式并转移到设备
            self.model.to(self.device)
            self.model.eval()
            
            self.model_path = model_path
            logger.info("模型加载成功")
            return True
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            self.model = None
            raise RuntimeError(f"模型加载失败: {str(e)}")
    
    def preprocess_image(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray, BinaryIO]
    ) -> torch.Tensor:
        """
        预处理输入图像
        
        Args:
            image_input: 图像输入，支持：
                        - 文件路径 (str/Path)
                        - PIL Image对象
                        - numpy数组
                        - 文件流
                        
        Returns:
            torch.Tensor: 预处理后的图像张量 [1, C, H, W]
            
        Raises:
            ValueError: 图像格式不支持
            RuntimeError: 预处理失败
        """
        try:
            # 根据不同输入类型加载图像
            if isinstance(image_input, (str, Path)):
                # 文件路径
                image = Image.open(image_input).convert('RGB')
            elif isinstance(image_input, Image.Image):
                # PIL Image对象
                image = image_input.convert('RGB')
            elif isinstance(image_input, np.ndarray):
                # numpy数组
                image = Image.fromarray(image_input).convert('RGB')
            elif hasattr(image_input, 'read'):
                # 文件流
                image = Image.open(image_input).convert('RGB')
            else:
                raise ValueError(f"不支持的图像输入类型: {type(image_input)}")
            
            # 应用预处理变换
            tensor = self.transform(image)
            
            # 添加batch维度
            tensor = tensor.unsqueeze(0)
            
            return tensor
            
        except Exception as e:
            logger.error(f"图像预处理失败: {str(e)}")
            raise RuntimeError(f"图像预处理失败: {str(e)}")
    
    def diagnose(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray, BinaryIO],
        return_probabilities: bool = True
    ) -> DiagnosisResult:
        """
        执行诊断推理
        
        Args:
            image_input: 输入图像（支持多种格式）
            return_probabilities: 是否返回各类别概率
            
        Returns:
            DiagnosisResult: 结构化诊断结果
        """
        import time
        
        start_time = time.time()
        
        # 检查模型是否已加载
        if self.model is None:
            return DiagnosisResult(
                conclusion="",
                conclusion_en="",
                confidence=0.0,
                confidence_percent=0.0,
                probabilities={},
                inference_time_ms=0.0,
                success=False,
                error_message="模型未加载，请先调用load_model()"
            )
        
        try:
            # 预处理图像
            input_tensor = self.preprocess_image(image_input)
            input_tensor = input_tensor.to(self.device)
            
            # 执行推理
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = F.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            # 获取各类别概率
            probs = probabilities.cpu().numpy()[0]
            pred_class = predicted.item()
            
            # 计算推理时间
            inference_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 构建概率字典
            prob_dict = {
                'normal': float(probs[0]),
                'pneumonia': float(probs[1]),
                'tuberculosis': float(probs[2])
            }
            
            # 获取诊断结论
            conclusion_en = self.CLASS_NAMES[pred_class]
            conclusion_cn = self.CLASS_NAMES_CN[conclusion_en]
            
            logger.info(
                f"诊断完成: {conclusion_cn} "
                f"(置信度: {confidence.item():.4f})"
            )
            
            return DiagnosisResult(
                conclusion=conclusion_cn,
                conclusion_en=conclusion_en,
                confidence=float(confidence.item()),
                confidence_percent=float(confidence.item()) * 100,
                probabilities=prob_dict,
                inference_time_ms=inference_time,
                success=True
            )
            
        except FileNotFoundError as e:
            logger.error(f"图像文件不存在: {str(e)}")
            return DiagnosisResult(
                conclusion="",
                conclusion_en="",
                confidence=0.0,
                confidence_percent=0.0,
                probabilities={},
                inference_time_ms=(time.time() - start_time) * 1000,
                success=False,
                error_message=f"图像文件不存在: {str(e)}"
            )
        except Exception as e:
            logger.error(f"诊断推理失败: {str(e)}")
            return DiagnosisResult(
                conclusion="",
                conclusion_en="",
                confidence=0.0,
                confidence_percent=0.0,
                probabilities={},
                inference_time_ms=(time.time() - start_time) * 1000,
                success=False,
                error_message=f"诊断推理失败: {str(e)}"
            )
    
    def diagnose_batch(
        self,
        image_paths: list
    ) -> list[DiagnosisResult]:
        """
        批量诊断
        
        Args:
            image_paths: 图像路径列表
            
        Returns:
            list[DiagnosisResult]: 诊断结果列表
        """
        results = []
        for path in image_paths:
            result = self.diagnose(path)
            results.append(result)
        return results
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            'model_path': self.model_path,
            'device': str(self.device),
            'num_classes': self.num_classes,
            'image_size': self.image_size,
            'classes': list(self.CLASS_NAMES_CN.values()),
            'loaded': self.model is not None
        }


# =============================================================================
# 便捷使用函数
# =============================================================================

def diagnose_xray(
    image_path: str,
    model_path: str = None
) -> DiagnosisResult:
    """
    便捷的胸部X光诊断函数
    
    一次性完成模型加载和诊断
    
    Args:
        image_path: X光影像文件路径
        model_path: 模型权重路径（默认使用项目内置模型）
        
    Returns:
        DiagnosisResult: 诊断结果
        
    Example:
        >>> result = diagnose_xray("patient_chest_xray.jpg")
        >>> print(result)
        诊断结论: 正常 (置信度: 85.3%)
          - 正常概率: 85.3%
          - 肺炎概率: 10.2%
          - 肺结核概率: 4.5%
    """
    # 自动查找默认模型路径
    if model_path is None:
        base_dir = Path(__file__).parent
        model_path = base_dir / 'weights' / 'best_model_full_mem.pth'
        if not model_path.exists():
            raise FileNotFoundError(
                "未找到默认模型文件，请提供模型路径"
            )
        model_path = str(model_path)
    
    # 创建诊断器并执行诊断
    diagnoser = ChestXrayDiagnoser(model_path=model_path)
    result = diagnoser.diagnose(image_path)
    
    return result


# =============================================================================
# 测试代码
# =============================================================================

if __name__ == '__main__':
    # 示例：测试诊断功能
    print("=" * 60)
    print("胸影智诊V2.0 - 胸部X光诊断推理模块")
    print("=" * 60)
    
    # 创建测试图像
    test_image_path = "test_xray_sample.jpg"
    
    try:
        # 创建随机测试图像
        import numpy as np
        test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        Image.fromarray(test_img).save(test_image_path)
        print(f"\n已创建测试图像: {test_image_path}")
        
        # 使用便捷函数进行诊断
        print("\n正在执行诊断...")
        result = diagnose_xray(test_image_path)
        
        if result.success:
            print("\n" + "-" * 40)
            print("诊断结果:")
            print("-" * 40)
            print(result)
            print("-" * 40)
            print(f"推理耗时: {result.inference_time_ms:.2f} ms")
        else:
            print(f"\n诊断失败: {result.error_message}")
        
        # 清理测试文件
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print(f"\n已清理测试文件: {test_image_path}")
            
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
