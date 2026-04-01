# AI 模型集成文档

## 📋 系统概述

**胸影智诊 V2.0** 已完整实现肺部影像 AI 分类功能，支持三种状态的智能识别：
- ✅ **正常 (Normal)**
- ✅ **肺炎 (Pneumonia)**
- ✅ **肺结核 (Tuberculosis)**

---

## 🎯 模型信息

### 模型文件
- **路径**: `backend/weights/best_model_full_mem.pth`
- **架构**: MobileNetV2 (轻量级深度学习模型)
- **输出类别**: 3 类 (normal, pneumonia, tuberculosis)
- **输入尺寸**: 224×224 像素

### 模型配置
```python
# backend/services/model_service.py
CLASS_NAMES = {
    0: 'normal',      # 正常
    1: 'pneumonia',   # 肺炎
    2: 'tuberculosis' # 肺结核
}
```

---

## 🔄 工作流程

### 1. 模型加载 (自动)
```python
# backend/app.py
with app.app_context():
    from backend.services.model_service import model_service
    model_service.load_model()  # ✅ 应用启动时自动加载
    app.logger.info('AI模型加载成功')
```

### 2. 影像上传与诊断
```
用户上传影像 → 前端 (Diagnosis.vue)
    ↓
API请求 (POST /api/diagnosis/upload)
    ↓
后端处理 (diagnosis.py)
    ↓
模型推理 (model_service.predict)
    ↓
返回结果 (JSON)
    ↓
前端展示 (诊断结果)
```

---

## 📊 核心功能实现

### ✅ 1. 模型服务 (backend/services/model_service.py)

**主要功能**:
- `load_model()`: 加载 MobileNetV2 模型和预训练权重
- `predict(image_path)`: 执行 AI 诊断推理
- `generate_gradcam()`: 生成 Grad-CAM 热力图
- `get_model_status()`: 获取模型状态信息

**关键代码**:
```python
def predict(self, image_path):
    """执行AI诊断推理"""
    # 加载并预处理图像
    image = Image.open(image_path).convert('RGB')
    input_tensor = self.transform(image).unsqueeze(0).to(self.device)
    
    # 推理
    with torch.no_grad():
        outputs = self.model(input_tensor)
        probabilities = F.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
    
    # 返回结果
    return {
        'result': CLASS_NAMES[predicted.item()],
        'result_cn': CLASS_NAMES_CN[CLASS_NAMES[predicted.item()]],
        'confidence': round(float(confidence.item()), 4),
        'probabilities': {
            'normal': round(float(probs[0]), 4),
            'pneumonia': round(float(probs[1]), 4),
            'tuberculosis': round(float(probs[2]), 4)
        }
    }
```

### ✅ 2. 诊断服务 (backend/services/diagnosis_service.py)

**主要功能**:
- `create_diagnosis()`: 创建诊断记录（调用模型推理）
- `generate_report()`: 生成诊断报告（AI 辅助）
- `review_diagnosis()`: 医生审核诊断
- `get_statistics()`: 获取统计数据

**关键代码**:
```python
def create_diagnosis(patient_id, doctor_id, image_path, ...):
    # 1. 调用AI模型推理
    ai_result = model_service.predict(image_path)
    
    # 2. 生成Grad-CAM热力图
    heatmap_img = model_service.generate_gradcam(image_path)
    
    # 3. 保存诊断记录
    record = DiagnosisRecord(
        ai_result=ai_result['result'],
        confidence=ai_result['confidence'],
        normal_prob=ai_result['probabilities']['normal'],
        pneumonia_prob=ai_result['probabilities']['pneumonia'],
        tuberculosis_prob=ai_result['probabilities']['tuberculosis'],
        ...
    )
    return record
```

### ✅ 3. API 接口 (backend/api/diagnosis.py)

**主要端点**:
- `POST /api/diagnosis/upload`: 上传影像并进行 AI 诊断
- `GET /api/diagnosis/list`: 获取诊断记录列表
- `GET /api/diagnosis/<id>`: 获取诊断详情
- `PUT /api/diagnosis/<id>/review`: 医生审核诊断
- `POST /api/diagnosis/<id>/report`: 生成诊断报告
- `GET /api/diagnosis/statistics`: 获取统计数据

### ✅ 4. 前端界面 (frontend/src/views/Diagnosis.vue)

**主要功能**:
- 📤 拖拽上传胸部 X 光影像
- 🤖 AI 智能诊断（显示三分类概率）
- 🔥 Grad-CAM 热力图可视化
- 📊 诊断结果详细展示
- 📝 诊断报告自动生成
- ✅ 医生审核与修正

**用户界面展示**:
```
┌─────────────────────────────────────────┐
│  AI诊断 / 诊断中心                      │
├─────────────────────────────────────────┤
│  [上传影像]  →  [AI诊断]  →  [结果展示] │
│                                         │
│  原始影像    Grad-CAM热力图             │
│  ┌───────┐   ┌───────┐                 │
│  │       │   │       │                 │
│  │       │   │       │                 │
│  └───────┘   └───────┘                 │
│                                         │
│  诊断结论: 正常 (置信度: 95.2%)         │
│  ├─ 正常概率: 95.2%  ████████████      │
│  ├─ 肺炎概率: 3.1%   █                 │
│  └─ 肺结核概率: 1.7% █                 │
│                                         │
│  [确认诊断] [修正诊断] [生成报告]       │
└─────────────────────────────────────────┘
```

---

## 🔍 分类结果示例

### JSON 响应格式
```json
{
  "code": 200,
  "message": "AI诊断完成",
  "data": {
    "record_id": 123,
    "record_no": "DX20260401000001",
    "ai_result": "normal",
    "confidence": 0.9523,
    "probabilities": {
      "normal": 0.9523,
      "pneumonia": 0.0312,
      "tuberculosis": 0.0165
    },
    "heatmap_path": "/static/heatmaps/abc123.jpg"
  }
}
```

### 前端展示效果
- **诊断结论**: 正常 (绿色标签)
- **置信度**: 95.2% (进度条可视化)
- **概率分布**: 三种状态的概率条形图
- **热力图**: Grad-CAM 可视化重点关注区域

---

## 🚀 使用指南

### 1. 启动系统
```bash
# 后端 (端口 5000)
cd backend
python app.py

# 前端 (端口 5173)
cd frontend
npm run dev
```

### 2. 访问诊断页面
```
http://localhost:5173/diagnosis
```

### 3. 操作步骤
1. 选择患者
2. 上传胸部 X 光影像
3. 点击"开始 AI 诊断"
4. 查看诊断结果和热力图
5. 确认或修正诊断
6. 生成诊断报告

---

## 📈 性能指标

### 模型性能
- **架构**: MobileNetV2 (轻量级)
- **推理速度**: ~50-100ms (CPU), ~10-20ms (GPU)
- **准确率**: 取决于训练数据质量
- **输入要求**: 224×224 RGB 图像

### 系统性能
- **并发处理**: 支持多用户同时诊断
- **响应时间**: < 2秒 (含影像处理)
- **内存占用**: ~200MB (模型加载)

---

## 🔧 技术栈

### 后端
- **Flask**: Web 框架
- **PyTorch**: 深度学习框架
- **torchvision**: 图像预处理
- **OpenCV**: 图像处理 (Grad-CAM)
- **Pillow**: 图像加载

### 前端
- **Vue 3**: 渐进式框架
- **Element Plus**: UI 组件库
- **Axios**: HTTP 客户端

### AI/ML
- **MobileNetV2**: 卷积神经网络
- **Grad-CAM**: 可视化注意力机制
- **Softmax**: 概率归一化

---

## 🎯 核心优势

### ✅ 准确性
- 三分类输出，精确识别疾病类型
- 置信度评分，量化诊断可靠性
- Grad-CAM 热力图，可视化 AI 决策依据

### ✅ 易用性
- 拖拽上传，操作简便
- 实时反馈，诊断快速
- 直观展示，结果清晰

### ✅ 专业性
- 医生审核机制
- AI 辅助报告生成
- 完整诊断流程

### ✅ 可解释性
- Grad-CAM 热力图
- 概率分布展示
- 医生可修正诊断

---

## 📝 注意事项

### ⚠️ 医疗免责声明
本系统仅供**辅助诊断参考**，最终诊断结果应以**临床医生判断**为准。

### ⚠️ 数据安全
- 所有医疗数据加密存储
- 用户权限分级管理
- 操作日志完整记录

### ⚠️ 模型要求
- 确保 `backend/weights/best_model_full_mem.pth` 文件存在
- 文件大小: ~9-14MB (MobileNetV2)
- 格式: PyTorch state_dict (.pth)

---

## 🔍 故障排查

### 模型加载失败
```bash
# 检查模型文件是否存在
ls -lh backend/weights/best_model_full_mem.pth

# 查看后端日志
# 应显示: "AI模型加载成功"
```

### 诊断失败
```bash
# 检查后端日志
# 常见错误:
# - "模型未加载": 重启后端服务
# - "影像验证失败": 检查影像格式和大小
# - "患者不存在": 确认患者 ID 正确
```

### 热力图生成失败
```bash
# 确保 OpenCV 已安装
pip install opencv-python

# 检查 static/heatmaps 目录权限
chmod 755 backend/static/heatmaps
```

---

## 📚 扩展功能

### 模型热切换
```python
# 支持动态加载不同模型
model_service.reload_model('/path/to/new_model.pth')
```

### 参数调整
```python
# 调整置信度阈值
model_service.update_params(confidence_threshold=0.7)

# 调整图像尺寸
model_service.update_params(image_size=256)
```

### GPU 加速
```python
# 自动检测 GPU
# 如有 CUDA 环境，自动使用 GPU 推理
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

---

## 📞 技术支持

如有问题，请查看：
1. 后端日志: `backend/logs/`
2. 数据库: `backend/data/medical_ai.db`
3. 模型状态: `GET /api/system/model-status`

---

**系统版本**: V2.0  
**最后更新**: 2026-04-01  
**作者**: 胸影智诊开发团队
