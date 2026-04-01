# 胸部X光诊断推理模块使用指南

## 概述

`chest_xray_diagnoser.py` 是一个独立的胸部X光AI诊断模块，用于加载预训练的PyTorch模型并生成结构化诊断结果。

## 核心功能

- ✅ 加载 `.pth` 格式预训练模型
- ✅ 支持多种图像输入格式（文件路径、PIL Image、numpy数组、文件流）
- ✅ 自动数据预处理（resize、灰度转换、归一化）
- ✅ 执行AI推理并返回结构化结果
- ✅ 完整的异常处理机制
- ✅ 支持批量诊断

---

## 快速开始

### 方式1：使用便捷函数（推荐）

```python
from chest_xray_diagnoser import diagnose_xray

# 一次性诊断（自动加载默认模型）
result = diagnose_xray("path/to/chest_xray.jpg")

if result.success:
    print(f"诊断结论: {result.conclusion}")
    print(f"置信度: {result.confidence_percent:.1f}%")
    print(f"正常概率: {result.probabilities['normal']*100:.1f}%")
    print(f"肺炎概率: {result.probabilities['pneumonia']*100:.1f}%")
    print(f"肺结核概率: {result.probabilities['tuberculosis']*100:.1f}%")
else:
    print(f"诊断失败: {result.error_message}")
```

### 方式2：使用诊断器类（适合批量诊断）

```python
from chest_xray_diagnoser import ChestXrayDiagnoser

# 初始化诊断器（加载模型）
diagnoser = ChestXrayDiagnoser(
    model_path="weights/best_model_full_mem.pth",
    device='cuda'  # 或 'cpu'，None为自动选择
)

# 诊断单张图像
result = diagnoser.diagnose("path/to/xray.jpg")

# 批量诊断
image_paths = ["xray1.jpg", "xray2.jpg", "xray3.jpg"]
results = diagnoser.diagnose_batch(image_paths)

# 获取模型信息
info = diagnoser.get_model_info()
print(info)
```

---

## API文档

### `diagnose_xray()` 便捷函数

**函数签名：**
```python
def diagnose_xray(
    image_path: str,
    model_path: str = None
) -> DiagnosisResult
```

**参数：**
- `image_path`: X光影像文件路径
- `model_path`: 模型权重路径（可选，默认使用项目内置模型）

**返回：**
- `DiagnosisResult`: 结构化诊断结果对象

---

### `ChestXrayDiagnoser` 诊断器类

#### 初始化参数

```python
ChestXrayDiagnoser(
    model_path: Optional[str] = None,      # 模型路径
    device: Optional[str] = None,           # 计算设备（'cuda'/'cpu'）
    num_classes: int = 3,                   # 分类数量
    image_size: int = 224                   # 输入图像尺寸
)
```

#### 主要方法

##### `load_model(model_path: str) -> bool`
加载预训练模型

```python
diagnoser = ChestXrayDiagnoser()
success = diagnoser.load_model("model.pth")
```

##### `diagnose(image_input) -> DiagnosisResult`
执行诊断推理

**支持的输入类型：**
- 文件路径：`"xray.jpg"`
- Path对象：`Path("xray.jpg")`
- PIL Image：`Image.open("xray.jpg")`
- numpy数组：`np.array([...])`
- 文件流：`open("xray.jpg", "rb")`

```python
# 文件路径
result = diagnoser.diagnose("xray.jpg")

# PIL Image
from PIL import Image
img = Image.open("xray.jpg")
result = diagnoser.diagnose(img)

# numpy数组
import numpy as np
arr = np.array(Image.open("xray.jpg"))
result = diagnoser.diagnose(arr)
```

##### `diagnose_batch(image_paths: list) -> list[DiagnosisResult]`
批量诊断多张图像

```python
results = diagnoser.diagnose_batch([
    "xray1.jpg",
    "xray2.jpg",
    "xray3.jpg"
])
```

##### `get_model_info() -> dict`
获取模型信息

```python
info = diagnoser.get_model_info()
# 返回: {
#     'model_path': 'weights/best_model_full_mem.pth',
#     'device': 'cuda',
#     'num_classes': 3,
#     'image_size': 224,
#     'classes': ['正常', '肺炎', '肺结核'],
#     'loaded': True
# }
```

---

### `DiagnosisResult` 结果数据类

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `conclusion` | str | 中文诊断结论（正常/肺炎/肺结核） |
| `conclusion_en` | str | 英文诊断结论 |
| `confidence` | float | 置信度（0-1） |
| `confidence_percent` | float | 置信度百分比（0-100） |
| `probabilities` | dict | 各类别概率字典 |
| `inference_time_ms` | float | 推理耗时（毫秒） |
| `success` | bool | 是否成功 |
| `error_message` | str | 错误信息 |

#### 方法

##### `to_dict() -> dict`
转换为字典格式

```python
result_dict = result.to_dict()
# 返回: {
#     'conclusion': '肺炎',
#     'conclusion_en': 'pneumonia',
#     'confidence': 0.856,
#     'confidence_percent': 85.6,
#     'probabilities': {
#         'normal': 0.102,
#         'pneumonia': 0.856,
#         'tuberculosis': 0.042
#     },
#     'inference_time_ms': 35.2,
#     'success': True,
#     'error_message': ''
# }
```

##### `__str__() -> str`
字符串表示

```python
print(result)
# 输出:
# 诊断结论: 肺炎 (置信度: 85.6%)
#   - 正常概率: 10.2%
#   - 肺炎概率: 85.6%
#   - 肺结核概率: 4.2%
```

---

## 完整使用示例

### 示例1：基础诊断

```python
from chest_xray_diagnoser import diagnose_xray

# 诊断单张X光片
result = diagnose_xray("patient_001_chest_xray.jpg")

if result.success:
    print("=" * 50)
    print("AI诊断报告")
    print("=" * 50)
    print(f"诊断结论: {result.conclusion}")
    print(f"置信度: {result.confidence_percent:.1f}%")
    print(f"推理耗时: {result.inference_time_ms:.2f}ms")
    print("\n概率分布:")
    for disease, prob in result.probabilities.items():
        print(f"  {disease}: {prob*100:.2f}%")
else:
    print(f"诊断失败: {result.error_message}")
```

### 示例2：批量诊断

```python
from chest_xray_diagnoser import ChestXrayDiagnoser
import json

# 初始化诊断器
diagnoser = ChestXrayDiagnoser(
    model_path="weights/best_model_full_mem.pth",
    device='cuda'  # 使用GPU加速
)

# 批量诊断
patient_files = [
    "patients/p001_xray.jpg",
    "patients/p002_xray.jpg",
    "patients/p003_xray.jpg"
]

results = diagnoser.diagnose_batch(patient_files)

# 导出结果为JSON
output_data = []
for i, result in enumerate(results):
    if result.success:
        output_data.append({
            'patient_file': patient_files[i],
            'diagnosis': result.to_dict()
        })

# 保存结果
with open('diagnosis_results.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"已完成 {len(output_data)} 例诊断")
```

### 示例3：集成到Web应用

```python
from flask import Flask, request, jsonify
from chest_xray_diagnoser import ChestXrayDiagnoser

app = Flask(__name__)

# 全局诊断器实例（启动时加载模型）
diagnoser = ChestXrayDiagnoser("weights/best_model_full_mem.pth")

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """诊断API端点"""
    if 'image' not in request.files:
        return jsonify({'error': '请上传图像文件'}), 400
    
    file = request.files['image']
    
    try:
        # 使用文件流直接诊断
        result = diagnoser.diagnose(file.stream)
        
        if result.success:
            return jsonify({
                'success': True,
                'data': result.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.error_message
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 示例4：处理实时数据流

```python
from chest_xray_diagnoser import ChestXrayDiagnoser
from PIL import Image
import io

# 初始化诊断器
diagnoser = ChestXrayDiagnoser("weights/best_model_full_mem.pth")

def process_dicom_stream(dicom_data: bytes) -> dict:
    """
    处理DICOM数据流
    
    Args:
        dicom_data: DICOM文件的字节数据
        
    Returns:
        dict: 诊断结果
    """
    try:
        # 假设已将DICOM转换为JPEG
        image = Image.open(io.BytesIO(dicom_data))
        
        # 执行诊断
        result = diagnoser.diagnose(image)
        
        return result.to_dict()
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

---

## 异常处理

模块内置完善的异常处理机制：

```python
from chest_xray_diagnoser import diagnose_xray

# 处理各种异常情况
result = diagnose_xray("invalid_path.jpg")

if not result.success:
    # 根据错误类型处理
    if "不存在" in result.error_message:
        print("文件路径错误")
    elif "预处理失败" in result.error_message:
        print("图像格式不支持")
    elif "模型" in result.error_message:
        print("模型加载问题")
    else:
        print(f"未知错误: {result.error_message}")
```

---

## 模型要求

### 支持的模型格式
- `.pth` (PyTorch state_dict)
- `.pt` (PyTorch模型)

### 模型架构要求
- 基于MobileNetV2
- 分类层输出维度为3（正常/肺炎/肺结核）
- 输入图像尺寸：224×224 RGB

### 默认模型
项目内置模型路径：`backend/weights/best_model_full_mem.pth`

---

## 性能优化建议

### 1. 使用GPU加速

```python
diagnoser = ChestXrayDiagnoser(
    model_path="model.pth",
    device='cuda'  # 使用NVIDIA GPU
)
```

### 2. 批量处理优化

```python
# 避免重复加载模型
diagnoser = ChestXrayDiagnoser("model.pth")

# 批量处理时使用diagnose_batch
results = diagnoser.diagnose_batch(image_list)
```

### 3. 异步处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def async_diagnose(diagnoser, image_path):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor, 
            diagnoser.diagnose, 
            image_path
        )
    return result

# 使用
result = await async_diagnose(diagnoser, "xray.jpg")
```

---

## 测试验证

运行测试脚本验证模块功能：

```bash
python chest_xray_diagnoser.py
```

**预期输出：**
```
============================================================
胸影智诊V2.0 - 胸部X光诊断推理模块
============================================================

已创建测试图像: test_xray_sample.jpg

正在执行诊断...
诊断器初始化 - 设备: cpu
正在加载模型: weights/best_model_full_mem.pth
模型加载成功
诊断完成: 肺炎 (置信度: 0.3364)

----------------------------------------
诊断结果:
----------------------------------------
诊断结论: 肺炎 (置信度: 33.6%)
  - 正常概率: 33.5%
  - 肺炎概率: 33.6%
  - 肺结核概率: 32.9%
----------------------------------------
推理耗时: 39.96 ms

已清理测试文件: test_xray_sample.jpg

============================================================
测试完成
============================================================
```

---

## 技术支持

如有问题，请联系开发团队或查看项目文档。

**版本：** 2.0.0  
**最后更新：** 2026-04-01
