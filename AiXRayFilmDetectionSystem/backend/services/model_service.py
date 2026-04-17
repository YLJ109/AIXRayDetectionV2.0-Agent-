# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - AI模型服务（核心ML配置）
负责 MobileNetV2 模型加载、推理
支持 PyTorch 和 ONNX 两种推理模式
仅保留网络结构定义、模型超参数设置及权重初始化参数
"""
import os
import time
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image

logger = logging.getLogger(__name__)

# 尝试导入 ONNX Runtime
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
    logger.info("ONNX Runtime 可用")
except ImportError:
    ONNX_AVAILABLE = False
    logger.info("ONNX Runtime 不可用，将使用 PyTorch 推理")

# 诊断类别映射
CLASS_NAMES = {0: 'normal', 1: 'pneumonia', 2: 'tuberculosis'}
CLASS_NAMES_CN = {'normal': '正常', 'pneumonia': '肺炎', 'tuberculosis': '肺结核'}

# ============================================================================
# 核心 ML 参数默认值（网络结构、超参数、权重初始化 + 热力图参数）
# ============================================================================
DEFAULT_PARAMS = {
    'confidence_threshold': 0.5,   # 推理置信度阈值
    'image_size': 224,             # 模型输入尺寸
    'num_classes': 3,              # 分类数量
    'dropout_rate': 0.2,           # Dropout 比例
    'pretrained': False,           # 是否使用预训练权重（初始化时）
    # 热力图参数
    'heatmap_size': 1024,          # 热力图输出尺寸
    'gradcam_alpha': 0.4,          # 热力图叠加透明度（原图权重）
    'gradcam_beta': 0.6,           # 热力图叠加透明度（热力图权重）
}

# 支持的图像输入尺寸
VALID_IMAGE_SIZES = [128, 224, 256, 299, 384, 512, 1024]

# 需要强制转换为 int 的参数
_INT_PARAMS = {'image_size', 'num_classes', 'heatmap_size'}


class ModelService:
    """
    AI模型服务单例 - 核心ML配置
    仅包含网络结构定义、模型超参数设置及权重初始化参数
    """

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

        # PyTorch 模型相关
        self.model = None
        self.device = None

        # ONNX 相关
        self.ort_session = None
        self.use_onnx = False

        # 预处理
        self.transform = None

        # 模型状态
        self.model_loaded = False
        self.current_weights_path = None

        # ====================================================================
        # 核心 ML 参数（网络结构、超参数、权重初始化、热力图）
        # ====================================================================
        self.confidence_threshold = DEFAULT_PARAMS['confidence_threshold']
        self.image_size = DEFAULT_PARAMS['image_size']
        self.target_size = DEFAULT_PARAMS['image_size']
        self.num_classes = DEFAULT_PARAMS['num_classes']
        self.dropout_rate = DEFAULT_PARAMS['dropout_rate']
        # 热力图参数
        self.heatmap_size = DEFAULT_PARAMS['heatmap_size']
        self.gradcam_alpha = DEFAULT_PARAMS['gradcam_alpha']
        self.gradcam_beta = DEFAULT_PARAMS['gradcam_beta']

    # ========================================================================
    # 参数持久化：从 system_configs 表加载/保存
    # ========================================================================

    def load_params_from_db(self):
        """从 system_configs 表加载模型核心参数配置"""
        try:
            from backend.models.all_models import SystemConfig
            from backend.core.extensions import db

            records = SystemConfig.query.filter(
                SystemConfig.config_key.like('model_%'),
                SystemConfig.is_deleted == False
            ).all()

            if not records:
                logger.info("模型参数配置为空，将使用默认值并初始化到数据库")
                self._init_default_configs_to_db()
                return

            param_map = {
                'model_confidence_threshold': 'confidence_threshold',
                'model_image_size': 'image_size',
                'model_num_classes': 'num_classes',
                'model_dropout_rate': 'dropout_rate',
                'model_heatmap_size': 'heatmap_size',
                'model_gradcam_alpha': 'gradcam_alpha',
                'model_gradcam_beta': 'gradcam_beta',
            }

            loaded = 0
            for rec in records:
                attr = param_map.get(rec.config_key)
                if not attr:
                    continue
                try:
                    raw_val = rec.config_value
                    # 整数参数强制转为 int，避免 float 传给 transforms.Resize 等报错
                    if attr in _INT_PARAMS:
                        val = int(float(raw_val))
                    else:
                        val = float(raw_val)
                    setattr(self, attr, val)
                    loaded += 1
                except (ValueError, TypeError):
                    logger.warning(f"参数值无效: {rec.config_key}={rec.config_value}")

            # 同步 image_size 到 target_size
            self.target_size = self.image_size

            logger.info(f"从数据库加载模型参数成功 ({loaded} 项)")

        except Exception as e:
            logger.warning(f"从数据库加载参数失败，使用默认值: {str(e)}")

    def _init_default_configs_to_db(self):
        """将默认参数写入 system_configs 表"""
        try:
            from backend.models.all_models import SystemConfig
            from backend.core.extensions import db

            key_attr_map = {
                'model_confidence_threshold': ('confidence_threshold', 'number',
                    'AI诊断置信度阈值(0-1)，低于此值的诊断标记为低置信度'),
                'model_image_size': ('image_size', 'number',
                    '模型输入图像尺寸(像素)'),
                'model_num_classes': ('num_classes', 'number',
                    '模型分类数量'),
                'model_dropout_rate': ('dropout_rate', 'number',
                    'Dropout比例(0-1)'),
                'model_heatmap_size': ('heatmap_size', 'number',
                    'Grad-CAM热力图输出尺寸(像素)'),
                'model_gradcam_alpha': ('gradcam_alpha', 'number',
                    'Grad-CAM叠加透明度-原图权重(0-1)'),
                'model_gradcam_beta': ('gradcam_beta', 'number',
                    'Grad-CAM叠加透明度-热力图权重(0-1)'),
            }

            for key, (attr, ctype, desc) in key_attr_map.items():
                exists = SystemConfig.query.filter_by(config_key=key, is_deleted=False).first()
                if exists:
                    continue
                cfg = SystemConfig(
                    config_key=key,
                    config_value=str(DEFAULT_PARAMS[attr]),
                    config_type=ctype,
                    description=desc,
                    group_name='model'
                )
                db.session.add(cfg)

            db.session.commit()
            logger.info("模型默认参数配置初始化完成")

        except Exception as e:
            logger.error(f"初始化默认参数配置失败: {str(e)}")

    def save_params_to_db(self):
        """将当前参数保存到 system_configs 表"""
        try:
            from backend.models.all_models import SystemConfig
            from backend.core.extensions import db

            key_attr_map = {
                'model_confidence_threshold': 'confidence_threshold',
                'model_image_size': 'image_size',
                'model_num_classes': 'num_classes',
                'model_dropout_rate': 'dropout_rate',
                'model_heatmap_size': 'heatmap_size',
                'model_gradcam_alpha': 'gradcam_alpha',
                'model_gradcam_beta': 'gradcam_beta',
            }

            updated = 0
            for key, attr in key_attr_map.items():
                rec = SystemConfig.query.filter_by(config_key=key, is_deleted=False).first()
                if rec:
                    new_val = str(getattr(self, attr))
                    if rec.config_value != new_val:
                        rec.config_value = new_val
                        updated += 1
                else:
                    rec = SystemConfig(
                        config_key=key,
                        config_value=str(getattr(self, attr)),
                        config_type='number',
                        description=f'{attr} 参数',
                        group_name='model'
                    )
                    db.session.add(rec)
                    updated += 1

            if updated > 0:
                db.session.commit()

            logger.info(f"模型参数保存到数据库完成 ({updated} 项变更)")
            return updated

        except Exception as e:
            logger.error(f"保存参数到数据库失败: {str(e)}")
            raise

    def reset_params(self):
        """重置所有模型参数为默认值"""
        self.confidence_threshold = DEFAULT_PARAMS['confidence_threshold']
        self.image_size = DEFAULT_PARAMS['image_size']
        self.target_size = DEFAULT_PARAMS['image_size']
        self.num_classes = DEFAULT_PARAMS['num_classes']
        self.dropout_rate = DEFAULT_PARAMS['dropout_rate']
        self.heatmap_size = DEFAULT_PARAMS['heatmap_size']
        self.gradcam_alpha = DEFAULT_PARAMS['gradcam_alpha']
        self.gradcam_beta = DEFAULT_PARAMS['gradcam_beta']

        if self.model_loaded:
            self._init_transform()

        self.save_params_to_db()
        logger.info("模型参数已重置为默认值")

    def get_params_dict(self):
        """获取当前所有可配置参数的字典"""
        return {
            'confidence_threshold': self.confidence_threshold,
            'image_size': self.image_size,
            'num_classes': self.num_classes,
            'dropout_rate': self.dropout_rate,
            'heatmap_size': self.heatmap_size,
            'gradcam_alpha': self.gradcam_alpha,
            'gradcam_beta': self.gradcam_beta,
        }

    def get_default_params(self):
        """获取默认参数字典"""
        return dict(DEFAULT_PARAMS)

    # ========================================================================
    # 模型加载（网络结构定义 + 权重初始化）
    # ========================================================================

    def load_model(self, weights_path=None, use_onnx=False):
        """
        加载模型（支持 PyTorch .pth 和 ONNX .onnx）
        网络结构: MobileNetV2
        超参数: num_classes=3, dropout=0.2
        """
        self.model_loaded = False
        self.model = None
        self.ort_session = None

        try:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"使用设备: {self.device}")

            if weights_path is None:
                weights_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'weights', 'best_model_full_mem.pth'
                )

            logger.info(f"尝试加载权重文件: {weights_path} (存在: {os.path.exists(weights_path)})")

            if not os.path.exists(weights_path):
                logger.warning(f"权重文件不存在: {weights_path}，使用随机初始化权重")
                self._init_pytorch_model()
                self._init_transform()
                self.current_weights_path = None
                self.model_loaded = True
                logger.info("随机初始化模型加载完成（推理结果无实际意义）")
                return True

            if weights_path.endswith('.onnx') and use_onnx and ONNX_AVAILABLE:
                self._load_onnx_model(weights_path)
            else:
                self._load_pytorch_model(weights_path)

            self._init_transform()
            self.model_loaded = True
            logger.info(f"AI模型加载完成 (模式: {'ONNX' if self.use_onnx else 'PyTorch'}, 权重: {weights_path})")
            return True

        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}，回退到随机初始化模型")
            # 即使权重加载失败，也创建一个随机模型以保持系统可用
            try:
                self._init_pytorch_model()
                self._init_transform()
                self.current_weights_path = None
                self.model_loaded = True
                logger.warning("已回退到随机初始化模型（推理结果无实际意义，请检查权重文件）")
                return True
            except Exception as fallback_err:
                logger.critical(f"随机初始化模型也失败: {str(fallback_err)}")
                self.model_loaded = False
                return False

    def _init_pytorch_model(self):
        """
        初始化 PyTorch 模型网络结构
        网络结构: MobileNetV2
        修改分类层: nn.Linear(num_features, num_classes)
        添加 Dropout: nn.Dropout(dropout_rate)
        """
        self.model = models.mobilenet_v2(weights=None)
        num_features = self.model.classifier[1].in_features
        
        # 定义分类器结构（含Dropout）
        self.model.classifier = nn.Sequential(
            nn.Dropout(self.dropout_rate),
            nn.Linear(num_features, self.num_classes)
        )
        
        self.model.to(self.device)
        self.model.eval()
        self.use_onnx = False
        logger.info(f"PyTorch 模型结构初始化完成 (num_classes={self.num_classes}, dropout={self.dropout_rate})")

    def _load_pytorch_model(self, weights_path):
        """
        加载 PyTorch 模型权重
        权重初始化: 从 checkpoint 加载 state_dict
        """
        logger.info(f"加载 PyTorch 模型: {weights_path}")
        self._init_pytorch_model()

        checkpoint = torch.load(weights_path, map_location=self.device, weights_only=False)
        if 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint, strict=False)

        self.model.to(self.device)
        self.model.eval()
        self.use_onnx = False
        self.current_weights_path = weights_path
        logger.info("PyTorch 模型权重加载成功")

    def _load_onnx_model(self, weights_path):
        """加载 ONNX 模型"""
        logger.info(f"加载 ONNX 模型: {weights_path}")
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']

        self.ort_session = ort.InferenceSession(
            weights_path, sess_options=sess_options, providers=providers
        )
        self.use_onnx = True
        self.current_weights_path = weights_path
        logger.info(f"ONNX 模型加载成功 (Provider: {self.ort_session.get_providers()[0]})")

    def _init_transform(self):
        """
        初始化图像预处理变换
        预处理流程: Grayscale -> Resize -> CenterCrop -> ToTensor -> Normalize
        """
        size = int(self.target_size)
        self.transform = transforms.Compose([
            transforms.Grayscale(num_output_channels=1),
            transforms.Resize(size + 32),
            transforms.CenterCrop(size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485], std=[0.229])
        ])

    # ========================================================================
    # 推理
    # ========================================================================

    def preprocess_image(self, image_input):
        """预处理图像为模型输入张量"""
        if isinstance(image_input, str):
            image = Image.open(image_input).convert('RGB')
        elif isinstance(image_input, np.ndarray):
            image = Image.fromarray(image_input).convert('RGB')
        elif isinstance(image_input, Image.Image):
            image = image_input.convert('RGB')
        else:
            raise ValueError(f"不支持的图像输入类型: {type(image_input)}")

        input_tensor = self.transform(image)
        input_tensor = input_tensor.repeat(3, 1, 1)
        return input_tensor.unsqueeze(0), image

    def predict(self, image_input):
        """
        执行AI诊断推理
        在调用前会自动检查并初始化模型
        """
        # 自动检查并初始化模型
        if not self.model_loaded:
            logger.warning("模型未加载，尝试自动初始化...")
            if not self.load_model():
                raise RuntimeError("模型自动初始化失败，请检查权重文件路径和日志")
            logger.info("模型自动初始化成功")

        start_time = time.time()
        try:
            input_tensor, original_image = self.preprocess_image(image_input)

            if self.use_onnx and self.ort_session:
                outputs = self._predict_onnx(input_tensor)
            else:
                outputs = self._predict_pytorch(input_tensor)

            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            probs = probabilities.cpu().numpy()[0]
            inference_time = (time.time() - start_time) * 1000

            result = {
                'result': CLASS_NAMES[predicted.item()],
                'result_cn': CLASS_NAMES_CN[CLASS_NAMES[predicted.item()]],
                'confidence': round(float(confidence.item()), 4),
                'probabilities': {
                    'normal': round(float(probs[0]), 4),
                    'pneumonia': round(float(probs[1]), 4),
                    'tuberculosis': round(float(probs[2]), 4)
                },
                'inference_time': round(inference_time, 1)
            }
            logger.info(
                f"诊断完成: {result['result_cn']} "
                f"(置信度: {result['confidence']:.2%}, 耗时: {result['inference_time']:.1f}ms)"
            )
            return result
        except Exception as e:
            logger.error(f"诊断推理失败: {str(e)}")
            raise RuntimeError(f"诊断推理失败: {str(e)}")

    def _predict_pytorch(self, input_tensor):
        input_tensor = input_tensor.to(self.device)
        with torch.no_grad():
            return self.model(input_tensor)

    def _predict_onnx(self, input_tensor):
        ort_inputs = {self.ort_session.get_inputs()[0].name: input_tensor.numpy()}
        ort_outputs = self.ort_session.run(None, ort_inputs)
        return torch.tensor(ort_outputs[0])

    # ========================================================================
    # 参数更新（带校验）- 仅核心ML参数
    # ========================================================================

    def update_params(self, **kwargs):
        """
        更新推理参数（带严格校验）
        仅支持核心ML参数: confidence_threshold, image_size, num_classes, dropout_rate
        """
        changed = False
        errors = []

        # confidence_threshold: 0.0 - 1.0
        if 'confidence_threshold' in kwargs:
            val = kwargs['confidence_threshold']
            try:
                val = float(val)
                if not (0.0 <= val <= 1.0):
                    errors.append('confidence_threshold 必须在 0.0-1.0 之间')
                else:
                    self.confidence_threshold = val
                    changed = True
            except (ValueError, TypeError):
                errors.append('confidence_threshold 必须为数字')

        # image_size: 限定值
        if 'image_size' in kwargs:
            val = kwargs['image_size']
            try:
                val = int(val)
                if val not in VALID_IMAGE_SIZES:
                    errors.append(f'image_size 必须为: {VALID_IMAGE_SIZES}')
                elif val != self.image_size:
                    self.image_size = val
                    self.target_size = val
                    if self.model_loaded:
                        self._init_transform()
                    changed = True
            except (ValueError, TypeError):
                errors.append('image_size 必须为整数')

        # num_classes: 正整数
        if 'num_classes' in kwargs:
            val = kwargs['num_classes']
            try:
                val = int(val)
                if val < 2:
                    errors.append('num_classes 必须大于等于 2')
                elif val != self.num_classes:
                    self.num_classes = val
                    changed = True
            except (ValueError, TypeError):
                errors.append('num_classes 必须为整数')

        # dropout_rate: 0.0 - 1.0
        if 'dropout_rate' in kwargs:
            val = kwargs['dropout_rate']
            try:
                val = float(val)
                if not (0.0 <= val <= 1.0):
                    errors.append('dropout_rate 必须在 0.0-1.0 之间')
                else:
                    self.dropout_rate = val
                    changed = True
            except (ValueError, TypeError):
                errors.append('dropout_rate 必须为数字')

        # heatmap_size: 正整数
        if 'heatmap_size' in kwargs:
            val = kwargs['heatmap_size']
            try:
                val = int(float(val))
                if val < 64:
                    errors.append('heatmap_size 必须大于等于 64')
                else:
                    self.heatmap_size = val
                    changed = True
            except (ValueError, TypeError):
                errors.append('heatmap_size 必须为整数')

        # gradcam_alpha: 0.0 - 1.0
        if 'gradcam_alpha' in kwargs:
            val = kwargs['gradcam_alpha']
            try:
                val = float(val)
                if not (0.0 <= val <= 1.0):
                    errors.append('gradcam_alpha 必须在 0.0-1.0 之间')
                else:
                    self.gradcam_alpha = val
                    changed = True
            except (ValueError, TypeError):
                errors.append('gradcam_alpha 必须为数字')

        # gradcam_beta: 0.0 - 1.0
        if 'gradcam_beta' in kwargs:
            val = kwargs['gradcam_beta']
            try:
                val = float(val)
                if not (0.0 <= val <= 1.0):
                    errors.append('gradcam_beta 必须在 0.0-1.0 之间')
                else:
                    self.gradcam_beta = val
                    changed = True
            except (ValueError, TypeError):
                errors.append('gradcam_beta 必须为数字')

        if errors:
            raise ValueError('; '.join(errors))

        return changed

    # ========================================================================
    # Grad-CAM 热力图生成
    # ========================================================================

    def generate_gradcam(self, image_input, target_layer_name=None):
        """
        生成 Grad-CAM 热力图
        :param image_input: 图像路径、numpy数组或PIL Image
        :param target_layer_name: 目标卷积层名称，默认使用最后一个卷积层
        :return: numpy数组 (H, W, 3) BGR格式的热力图叠加图
        """
        if not self.model_loaded or not self.model:
            raise RuntimeError("模型未加载，无法生成Grad-CAM热力图")

        if self.use_onnx:
            logger.warning("ONNX模式不支持Grad-CAM，使用简单热力图替代")
            return self._generate_heatmap_simple(image_input)

        import cv2

        try:
            # 预处理图像
            input_tensor, original_image = self.preprocess_image(image_input)
            input_tensor = input_tensor.to(self.device)
            input_tensor.requires_grad_(True)

            # 获取目标层（默认最后一个 features 层）
            if target_layer_name is None:
                target_layer = None
                for module in self.model.features.modules():
                    if isinstance(module, nn.Conv2d):
                        target_layer = module
                if target_layer is None:
                    raise RuntimeError("未找到卷积层，无法生成Grad-CAM")
            else:
                target_layer = dict(self.model.named_modules()).get(target_layer_name)
                if target_layer is None:
                    raise RuntimeError(f"未找到层: {target_layer_name}")

            # 前向传播
            activations = []
            gradients = []

            def forward_hook(module, input, output):
                activations.append(output.detach())

            def backward_hook(module, grad_input, grad_output):
                gradients.append(grad_output[0].detach())

            handle_f = target_layer.register_forward_hook(forward_hook)
            handle_b = target_layer.register_full_backward_hook(backward_hook)

            try:
                outputs = self.model(input_tensor)
                pred_class = outputs.argmax(dim=1).item()
                outputs[0][pred_class].backward()

                # 计算 Grad-CAM
                act = activations[0]
                grad = gradients[0]
                weights = grad.mean(dim=(2, 3), keepdim=True)
                cam = (weights * act).sum(dim=1, keepdim=True)
                cam = F.relu(cam)
                cam = cam.squeeze().cpu().numpy()

                # 归一化
                cam = cam - cam.min()
                if cam.max() > 0:
                    cam = cam / cam.max()

                # 调整热力图大小
                orig_pil = Image.fromarray(
                    np.array(original_image.resize((int(self.target_size), int(self.target_size))))
                )
                cam = cv2.resize(cam, (int(self.target_size), int(self.target_size)))

                # 应用颜色映射
                heatmap = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)

                # 叠加到原始图像
                original_np = np.array(orig_pil)
                original_bgr = cv2.cvtColor(original_np, cv2.COLOR_RGB2BGR)
                superimposed = cv2.addWeighted(
                    original_bgr, self.gradcam_alpha, heatmap, self.gradcam_beta, 0
                )
                superimposed = cv2.cvtColor(superimposed, cv2.COLOR_BGR2RGB)

                # 调整到输出尺寸
                if self.heatmap_size and self.heatmap_size > 0:
                    superimposed = cv2.resize(
                        superimposed,
                        (int(self.heatmap_size), int(self.heatmap_size))
                    )

                return superimposed
            finally:
                handle_f.remove()
                handle_b.remove()

        except Exception as e:
            logger.error(f"Grad-CAM生成失败: {str(e)}，使用简单热力图替代")
            return self._generate_heatmap_simple(image_input)

    def _generate_heatmap_simple(self, image_input):
        """
        简单热力图生成（Grad-CAM失败时的备用方案）
        基于模型预测概率分布生成彩色热力图
        """
        import cv2

        if isinstance(image_input, str):
            image = Image.open(image_input).convert('RGB')
        elif isinstance(image_input, np.ndarray):
            image = Image.fromarray(image_input).convert('RGB')
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            raise ValueError(f"不支持的图像输入类型: {type(image_input)}")

        try:
            # 推理获取概率
            result = self.predict(image_input)
            probs = list(result['probabilities'].values())

            # 基于概率创建渐变热力图
            h, w = image.size[1], image.size[0]
            gradient = np.zeros((h, w, 3), dtype=np.uint8)

            # 根据诊断结果设置不同颜色
            result_type = result['result']
            if result_type == 'normal':
                color = (16, 185, 129)   # 绿色
            elif result_type == 'pneumonia':
                color = (245, 158, 11)   # 橙色
            else:
                color = (139, 92, 246)   # 紫色

            confidence = result['confidence']
            gradient[:] = tuple(int(c * confidence) for c in color)

            # 叠加到原始图像
            original_np = np.array(image)
            original_bgr = cv2.cvtColor(original_np, cv2.COLOR_RGB2BGR)
            overlay = cv2.addWeighted(
                original_bgr, self.gradcam_alpha, gradient, self.gradcam_beta, 0
            )
            overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

            if self.heatmap_size and self.heatmap_size > 0:
                overlay = cv2.resize(overlay, (int(self.heatmap_size), int(self.heatmap_size)))

            return overlay
        except Exception as e:
            logger.error(f"简单热力图生成失败: {str(e)}")
            raise

    @staticmethod
    def save_heatmap(heatmap_img, save_path):
        """
        保存热力图到文件
        :param heatmap_img: numpy数组 (H, W, 3) RGB格式
        :param save_path: 保存路径
        """
        import cv2
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        heatmap_bgr = cv2.cvtColor(heatmap_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(save_path, heatmap_bgr)
        logger.info(f"热力图已保存: {save_path}")

    # ========================================================================
    # 模型状态 / 列表 / 切换
    # ========================================================================

    def get_model_status(self):
        """获取当前模型状态信息"""
        import torch.cuda
        gpu_available = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if gpu_available else None
        gpu_memory = round(torch.cuda.get_device_properties(0).total_mem / (1024**3), 2) if gpu_available else None

        return {
            'model_loaded': self.model_loaded,
            'current_model': os.path.basename(self.current_weights_path) if self.current_weights_path else '',
            'device': str(self.device) if self.device else 'N/A',
            'inference_mode': 'ONNX' if self.use_onnx else 'PyTorch',
            'onnx_available': ONNX_AVAILABLE,
            'architecture': 'MobileNetV2 (3-class)',
            'classes': ['normal', 'pneumonia', 'tuberculosis'],
            'gpu_available': gpu_available,
            'gpu_name': gpu_name,
            'gpu_memory_gb': gpu_memory,
            # 核心 ML 参数
            'params': self.get_params_dict(),
            'default_params': self.get_default_params(),
        }

    def list_available_models(self):
        """扫描 weights 目录，列出所有可用的模型文件"""
        weights_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'weights'
        )
        supported_ext = ('.pth', '.pt', '.onnx', '.pkl', '.bin')
        models = []

        if os.path.isdir(weights_dir):
            for f in os.listdir(weights_dir):
                if f.lower().endswith(supported_ext):
                    fpath = os.path.join(weights_dir, f)
                    models.append({
                        'filename': f,
                        'path': fpath,
                        'size_mb': round(os.path.getsize(fpath) / (1024 * 1024), 2),
                        'format': f.rsplit('.', 1)[-1].lower(),
                        'is_active': (fpath == self.current_weights_path)
                    })
        return models

    def reload_model(self, weights_path=None, use_onnx=False):
        """重新加载模型"""
        self.model_loaded = False
        self.model = None
        self.ort_session = None

        try:
            import torch.cuda
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

        return self.load_model(weights_path=weights_path, use_onnx=use_onnx)


# 全局模型服务实例
model_service = ModelService()
