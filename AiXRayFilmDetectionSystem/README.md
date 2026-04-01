# 胸影智诊V2.0 - 企业级医疗AI胸部X光智能辅助诊断系统

> 基于深度学习 MobileNetV2 的胸部X光智能辅助诊断系统，覆盖正常、肺炎、肺结核三类诊断场景，提供AI诊断、Grad-CAM热力图、患者管理、诊断报告生成等企业级功能。

## 系统架构

```
AiXRayFilmDetectionSystem/
├── backend/                          # Flask 后端
│   ├── api/                          # API路由（auth/diagnosis/patient/user/system）
│   ├── core/                         # 核心配置（config/extensions）
│   ├── models/                       # 数据模型（SQLAlchemy ORM）
│   ├── services/                     # 业务服务（AI模型/诊断/患者/用户）
│   ├── utils/                        # 工具类（审计日志/图像预处理/通用工具）
│   ├── weights/                      # 模型权重（best_model_full_mem.pth）
│   ├── static/                       # 静态文件（运行时自动创建）
│   ├── app.py                        # Flask应用入口
│   ├── init_database.py              # 数据库初始化脚本
│   └── requirements.txt              # Python依赖
├── frontend/                         # Vue3 前端
│   ├── src/
│   │   ├── api/                      # Axios接口封装
│   │   ├── components/               # 可复用组件（Layout）
│   │   ├── router/                   # 路由配置（含权限守卫）
│   │   ├── stores/                   # Pinia状态管理
│   │   ├── styles/                   # 全局样式
│   │   └── views/                    # 页面视图（6个页面）
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Flask | 2.3.3 |
| 数据库 | SQLAlchemy + SQLite（可扩展MySQL） | 2.0.23 |
| 认证授权 | Flask-JWT-Extended | 4.5.3 |
| AI框架 | PyTorch + torchvision | 2.1.0 |
| 图像处理 | OpenCV + Pillow | 4.8.1 / 10.1.0 |
| 前端框架 | Vue 3 | 3.3.4 |
| UI组件 | Element Plus | 2.4.0 |
| 状态管理 | Pinia | 2.1.6 |
| 图表可视化 | ECharts + vue-echarts | 5.4.3 |
| 构建工具 | Vite | 4.4.9 |
| 报告生成 | 阿里云通义千问（qwen-turbo） | - |

## 核心功能

1. **AI诊断中心** - 影像上传、MobileNetV2三分类推理、Grad-CAM热力图
2. **诊断报告** - 通义千问AI自动生成专业诊断报告，医生审核机制
3. **患者管理** - 档案CRUD、病史记录、诊断历史关联
4. **数据看板** - 诊断量统计、病种分布、趋势图表、模型监控
5. **用户权限** - JWT认证、RBAC角色控制（管理员/医生）
6. **审计安全** - 全操作日志、API限流、软删除

## 快速开始

### 环境要求
- Python 3.9+ / Node.js 16+
- CUDA（可选，GPU加速推理）

### 后端部署

```bash
cd AiXRayFilmDetectionSystem/backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python init_database.py        # 初始化数据库
python app.py                  # 启动 http://localhost:5000
```

### 前端部署

```bash
cd AiXRayFilmDetectionSystem/frontend
npm install
npm run dev                    # 启动 http://localhost:5173
npm run build                  # 生产构建
```

### 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 医生 | doctor | doctor123 |

## 生产部署

```bash
# 后端
gunicorn -w 4 -b 0.0.0.0:5000 "backend.app:create_app()"
# 前端构建后 nginx 托管 dist/ 目录
```

## 安全合规

- AI诊断结论标注"仅供临床医生参考"
- JWT Token 8小时有效期 + API限流
- 全操作审计日志，支持追溯
- 软删除机制，数据可恢复
