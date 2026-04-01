# 🚀 快速启动指南

## 📋 前置要求

### 系统要求
- Python 3.8+
- Node.js 16+
- 操作系统: Windows / macOS / Linux

### 必需文件
- ✅ 模型文件: `backend/weights/best_model_full_mem.pth`

---

## 🔧 安装步骤

### 1️⃣ 后端安装

```bash
# 进入后端目录
cd AiXRayFilmDetectionSystem/backend

# 安装Python依赖
pip install -r requirements.txt

# 主要依赖包括:
# - Flask (Web框架)
# - PyTorch (深度学习)
# - torchvision (图像处理)
# - Pillow (图像加载)
# - OpenCV (Grad-CAM)
# - Flask-JWT-Extended (认证)
# - SQLAlchemy (数据库)
```

### 2️⃣ 前端安装

```bash
# 进入前端目录
cd AiXRayFilmDetectionSystem/frontend

# 安装Node.js依赖
npm install

# 主要依赖包括:
# - Vue 3 (前端框架)
# - Element Plus (UI组件)
# - Axios (HTTP客户端)
# - Vue Router (路由)
# - Pinia (状态管理)
```

---

## 🎯 启动系统

### 方式一: 完整启动 (推荐)

#### 1. 启动后端服务
```bash
cd backend
python app.py
```

**预期输出**:
```
2026-04-01 00:00:00 [INFO] backend.app: 数据库表创建/检查完成
2026-04-01 00:00:00 [INFO] backend.services.model_service: 使用设备: cpu
2026-04-01 00:00:00 [INFO] backend.services.model_service: 加载模型权重: D:\...\weights\best_model_full_mem.pth
2026-04-01 00:00:00 [INFO] backend.services.model_service: 模型权重加载成功
2026-04-01 00:00:00 [INFO] backend.services.model_service: AI模型加载完成
2026-04-01 00:00:00 [INFO] backend.app: AI模型加载成功
2026-04-01 00:00:00 [INFO] backend.app: [种子数据] 默认管理员账号创建成功 (用户名: admin, 密码: admin123)
 * Running on http://0.0.0.0:5000
```

#### 2. 启动前端服务 (新终端)
```bash
cd frontend
npm run dev
```

**预期输出**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

### 方式二: 仅测试模型

```bash
cd backend
python test_model.py
```

**预期输出**:
```
============================================================
🚀 胸影智诊V2.0 - AI模型测试套件
============================================================

============================================================
📦 测试 1: 模型加载
============================================================
✅ 模型文件存在: D:\...\weights\best_model_full_mem.pth
   文件大小: 13.48 MB
✅ 模型加载成功

📊 模型状态:
   设备: cpu
   架构: MobileNetV2 (3-class)
   类别: ['normal', 'pneumonia', 'tuberculosis']

... (更多测试结果)

🎉 所有测试通过! 模型功能正常
✨ 系统已准备好进行肺部影像诊断
```

---

## 🌐 访问系统

### 前端界面
```
http://localhost:5173
```

### 后端API
```
http://localhost:5000/api
```

---

## 👤 默认账号

### 管理员账号
```
用户名: admin
密码: admin123
```

### 医生账号 (5个)
```
doctor_wang  / doctor123  (王建国 - 放射科)
doctor_li    / doctor123  (李秀芳 - 放射科)
doctor_zhang / doctor123  (张明远 - 呼吸内科)
doctor_chen  / doctor123  (陈思远 - 影像科)
doctor_liu   / doctor123  (刘婉清 - 胸外科)
```

### 测试患者 (10个)
```
P20260315001 - 张伟 (男, 45岁)
P20260315002 - 李娜 (女, 32岁)
... (共10名测试患者)
```

---

## 📍 主要页面

| 页面 | 路径 | 功能 |
|------|------|------|
| 登录 | `/login` | 用户认证 |
| 主页 | `/dashboard` | 数据概览 |
| **AI诊断** | **`/diagnosis`** | **影像上传与AI诊断** ⭐ |
| 诊断历史 | `/history` | 查看历史记录 |
| 患者管理 | `/patients` | 患者信息管理 |
| 系统设置 | `/settings` | 系统配置 |

---

## 🎬 使用流程

### 1. 登录系统
```
访问 http://localhost:5173/login
使用账号: doctor_wang / doctor123
```

### 2. 进入诊断页面
```
左侧菜单 → AI诊断 → 诊断中心
或直接访问: http://localhost:5173/diagnosis
```

### 3. 上传影像并诊断
```
1. 选择患者 (下拉选择)
2. 填写症状描述 (可选)
3. 拖拽或点击上传胸部X光影像
   - 支持格式: PNG/JPG/JPEG/BMP/GIF/WEBP
   - 最大大小: 50MB
4. 点击 "开始AI诊断" 按钮
5. 等待诊断完成 (约1-2秒)
```

### 4. 查看诊断结果
```
✅ 诊断结论 (正常/肺炎/肺结核)
✅ 置信度评分
✅ 三分类概率分布
✅ Grad-CAM热力图
✅ 原始影像对比
```

### 5. 审核与报告
```
- 确认诊断: 认可AI诊断结果
- 修正诊断: 医生手动修正诊断
- 生成报告: AI辅助生成诊断报告
```

---

## 🧪 测试功能

### 测试影像上传
```bash
# 准备测试影像 (胸部X光片)
# 支持格式: .png, .jpg, .jpeg, .bmp, .gif, .webp

# 通过前端上传测试
http://localhost:5173/diagnosis
```

### 测试API接口
```bash
# 获取诊断列表
curl -X GET "http://localhost:5000/api/diagnosis/list?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取统计数据
curl -X GET "http://localhost:5000/api/diagnosis/statistics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ⚠️ 常见问题

### Q1: 模型加载失败
```bash
# 检查模型文件是否存在
ls -lh backend/weights/best_model_full_mem.pth

# 如果不存在，请将模型文件放置到正确位置
# 预期大小: 约9-14MB
```

### Q2: 后端启动失败
```bash
# 检查端口占用
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # macOS/Linux

# 检查Python依赖
pip list | grep Flask
pip list | grep torch
```

### Q3: 前端启动失败
```bash
# 检查端口占用
netstat -ano | findstr :5173  # Windows
lsof -i :5173                 # macOS/Linux

# 重新安装依赖
cd frontend
rm -rf node_modules
npm install
```

### Q4: 诊断失败
```bash
# 检查后端日志
# 常见错误:
# - "模型未加载" → 重启后端服务
# - "影像验证失败" → 检查影像格式和大小
# - "患者不存在" → 确认患者ID正确
```

### Q5: 热力图生成失败
```bash
# 安装OpenCV
pip install opencv-python

# 检查目录权限
chmod 755 backend/static/heatmaps  # macOS/Linux
```

---

## 🔍 性能优化

### GPU加速 (推荐)
```python
# 如果有NVIDIA GPU和CUDA环境
# 模型会自动使用GPU推理
# 推理速度可提升5-10倍

# 检查GPU是否可用
python -c "import torch; print(torch.cuda.is_available())"
```

### 模型优化
```python
# 调整图像尺寸 (可选)
# 较小尺寸 → 更快速度
# 较大尺寸 → 更高精度

model_service.update_params(image_size=192)  # 默认224
```

---

## 📊 系统监控

### 检查模型状态
```bash
GET http://localhost:5000/api/system/model-status

# 响应示例
{
  "model_loaded": true,
  "current_model": "best_model_full_mem.pth",
  "device": "cuda",
  "gpu_available": true,
  "gpu_name": "NVIDIA GeForce RTX 3060"
}
```

### 检查系统健康
```bash
GET http://localhost:5000/api/system/health

# 响应示例
{
  "status": "healthy",
  "database": "connected",
  "model": "loaded"
}
```

---

## 🎓 进阶使用

### 批量诊断
```python
# 批量处理影像
from backend.services.diagnosis_service import diagnosis_service

for image_path in image_list:
    record = diagnosis_service.create_diagnosis(
        patient_id=patient_id,
        doctor_id=doctor_id,
        image_path=image_path,
        ...
    )
```

### 模型热切换
```python
# 动态加载新模型
from backend.services.model_service import model_service

model_service.reload_model('/path/to/new_model.pth')
```

### 自定义参数
```python
# 调整置信度阈值
model_service.update_params(confidence_threshold=0.7)

# 调整图像尺寸
model_service.update_params(image_size=256)
```

---

## 📞 获取帮助

### 查看日志
```bash
# 后端日志
tail -f backend/logs/app.log

# 前端控制台
浏览器 F12 → Console
```

### 数据库查看
```bash
# SQLite数据库
sqlite3 backend/data/medical_ai.db

# 查看诊断记录
SELECT * FROM diagnosis_record LIMIT 10;
```

---

## 🎉 成功标志

当你看到以下信息时，说明系统已成功启动:

✅ 后端终端显示: `Running on http://0.0.0.0:5000`  
✅ 后端终端显示: `AI模型加载成功`  
✅ 前端终端显示: `Local: http://localhost:5173/`  
✅ 浏览器能正常访问登录页面  
✅ 使用 `doctor_wang/doctor123` 成功登录  
✅ 能进入"AI诊断"页面  
✅ 能上传影像并获得诊断结果  

---

**祝你使用愉快! 🎊**

如有问题，请查看:
- 📚 完整文档: `AI_MODEL_INTEGRATION.md`
- 🧪 测试脚本: `backend/test_model.py`
- 📝 API文档: 访问后端 `/api` 端点
