# 胸影智诊 V3.0 (AIX-Ray)

<p align="center">
  <img src="ProjectImage/登录界面.png" alt="登录界面" width="800"/>
</p>

**胸部X光AI智能辅助诊断系统** — 基于深度学习的医学影像智能诊断平台，集成 ONNX 加速推理、大语言模型报告生成、Grad-CAM 热力图可视化、批量诊断、智能分诊与 AI 医学咨询等核心功能。

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [系统截图](#系统截图)
- [模块说明](#模块说明)
- [数据库设计](#数据库设计)
- [API 接口文档](#api-接口文档)
- [快速开始](#快速开始)
- [部署指南](#部署指南)
- [项目结构](#项目结构)
- [配置说明](#配置说明)
- [默认账号](#默认账号)
- [开发说明](#开发说明)

---

## 项目简介

胸影智诊 V3.0 是一套面向医疗机构的全栈 AI 辅助诊断系统，专注于 **胸部 X 光影像** 的智能分析。系统基于 **DenseNet-121 (CheXNet)** 深度学习模型，支持对 **14 种胸部疾病** 进行概率预测，并结合大语言模型（LLM）自动生成专业放射学诊断报告。

### 核心能力

| 能力 | 说明 |
|------|------|
| **AI 疾病检测** | 基于 DenseNet-121 的 14 种胸部疾病多标签分类 |
| **ONNX 加速推理** | 推理速度比原生 PyTorch 快 2-5 倍，支持 GPU/CPU/DirectML |
| **Grad-CAM 热力图** | 可视化 AI 关注区域，辅助医生理解模型判断依据 |
| **LLM 报告生成** | 调用大模型（通义千问等）生成专业放射学诊断报告 |
| **批量诊断** | 多图并行预处理 + 批量推理，支持数十张影像一次性处理 |
| **智能分诊** | 基于症状和生命体征的急诊分诊评估 |
| **AI 医学咨询** | 流式对话的 AI 医学助手，支持多角色切换 |
| **诊断审批** | 医生审核 AI 诊断结果的审批工作流 |

### 支持检测的 14 种胸部疾病

| 英文名称 | 中文名称 | 英文名称 | 中文名称 |
|----------|----------|----------|----------|
| Atelectasis | 肺不张 | Consolidation | 实变 |
| Cardiomegaly | 心脏肥大 | Edema | 水肿 |
| Effusion | 胸腔积液 | Emphysema | 肺气肿 |
| Infiltration | 浸润 | Fibrosis | 纤维化 |
| Mass | 肿块 | Pleural_Thickening | 胸膜增厚 |
| Nodule | 结节 | Hernia | 疝 |
| Pneumonia | 肺炎 | — | — |
| Pneumothorax | 气胸 | — | — |

---

## 功能特性

### 业务端功能

#### 1. 数据看板
- 诊断统计概览（今日/本周/本月诊断量）
- 疾病分布图表（ECharts 饼图 + 柱状图）
- 用户活跃度统计
- 待审批数量提醒
- 系统运行状态监控

#### 2. 诊断中心
- 上传胸部 X 光影像（PNG/JPG/JPEG）
- 自动识别患者信息（从文件名解析：`P编号-姓名-性别-年龄-症状-序号`）
- AI 实时推理，展示 14 种疾病检测概率
- Grad-CAM 热力图叠加显示
- LLM 一键生成专业诊断报告
- PDF 报告导出下载

#### 3. 批量诊断
- 支持一次选择多张影像
- 每张图片独立显示患者卡片
- 并行批量推理（ThreadPoolExecutor 多线程预处理）
- 实时进度条反馈
- 逐张生成热力图和诊断报告
- 支持中途停止检测
- 结果区域统一查看所有检测结果

#### 4. 智能分诊
- 症状多选（咳嗽、胸痛、呼吸困难等 15+ 种常见症状）
- 严重程度分级（轻微 / 中度 / 严重 / 危急）
- 生命体征录入（体温、心率、血压、血氧、呼吸频率）
- AI 分诊评估结果（推荐科室 + 紧急程度 + 分诊依据）
- 分诊记录历史查询

#### 5. AI 咨询
- 流式对话界面（SSE 实时打字效果）
- 多角色切换：放射科专家 / 呼吸科专家 / 胸外科专家 / 急诊科专家 / 全科顾问
- 会话历史管理（新建/切换/删除会话）
- Markdown 格式渲染回复内容

#### 6. 诊断历史
- 所有诊断记录列表
- 按时间/患者/状态筛选
- 查看详细检测结果和报告
- 报告 PDF 在线预览/下载

#### 7. 诊断审批
- 待审批 / 已审批 / 已驳回 列表
- 查看 AI 检测详情 + 热力图
- 医生审核操作（通过 / 驳回 + 备注）
- 审批状态流转追踪

### 管理端功能

#### 8. 系统概览
- 系统整体运行数据大盘
- 用户/患者/诊断统计
- 模型状态监控

#### 9. 用户管理
- 用户 CRUD 操作
- 角色分配（管理员 / 医生 / 护士）
- 状态启用/禁用
- 密码重置

#### 10. 患者管理
- 患者 CRUD 操作
- 既往史/过敏史管理
- 关联诊断记录查看

#### 11. 权重文件管理
- 模型权重文件上传（.pth/.pt/.onnx）
- 权重文件列表管理
- 切换当前激活权重
- 模型版本管理

#### 12. 大模型 API 管理
- 多 LLM 配置管理
- API Key 加密存储（AES 对称加密）
- 支持 OpenAI 兼容接口（通义千问 / DeepSeek / OpenAI 等）
- 默认配置 / 优先级设置
- temperature / max_tokens 参数自定义

#### 13. 审计日志
- 全量操作日志记录（29+ 种操作类型）
- 中文标签化展示
- 按操作类型 / 时间范围筛选
- 操作人 / IP / 详情完整记录
- 日志自动清理（可配置保留天数）

#### 14. 系统设置
- 系统名称配置
- 疾病检测阈值调整
- 文件上传大小限制
- 会话超时时间
- 审计日志保留策略
- 批量处理并发数

### 通用特性

- **深色/浅色主题切换** — 全局主题系统，用户偏好持久化
- **响应式侧边栏** — 可折叠导航栏
- **JWT 身份认证** — Token 令牌认证，30 天有效期
- **RBAC 权限控制** — 基于角色的页面级权限
- **路由守卫** — 未登录自动跳转，无权限拦截
- **全局错误处理** — 统一错误提示和网络异常处理

---

## 系统截图

### 登录界面
<p align="center">
  <img src="ProjectImage/登录界面.png" alt="登录界面" width="800"/>
</p>

### 数据看板
<p align="center">
  <img src="ProjectImage/数据看板.png" alt="数据看板" width="800"/>
</p>

### 诊断中心 - 空状态 & 检测结果 & 生成报告
<p align="center">
  <img src="ProjectImage/诊断中心-空.png" alt="诊断中心-空" width="380"/>
  <img src="ProjectImage/诊断结果-检测结果.png" alt="诊断结果-检测结果" width="380"/>
  <img src="ProjectImage/诊断中心-生成报告.png" alt="诊断中心-生成报告" width="380"/>
</p>

### 批量诊断 - 选择影像 & 检测结果
<p align="center">
  <img src="ProjectImage/批量诊断-空.png" alt="批量诊断-空" width="380"/>
  <img src="ProjectImage/批量诊断-选择影像.png" alt="批量诊断-选择影像" width="380"/>
  <img src="ProjectImage/批量诊断-检测结果与生成报告.png" alt="批量诊断-检测结果与生成报告" width="380"/>
</p>

### 智能分诊
<p align="center">
  <img src="ProjectImage/智能分诊-空.png" alt="智能分诊-空" width="380"/>
  <img src="ProjectImage/智能分诊-分诊评估.png" alt="智能分诊-分诊评估" width="380"/>
  <img src="ProjectImage/智能分诊-症状详情.png" alt="智能分诊-症状详情" width="380"/>
</p>

### AI 咨询
<p align="center">
  <img src="ProjectImage/AI咨询-空.png" alt="AI咨询-空" width="380"/>
  <img src="ProjectImage/AI咨询-AI回复.png" alt="AI咨询-AI回复" width="380"/>
</p>

### 诊断审批 & 历史诊断
<p align="center">
  <img src="ProjectImage/诊断审批.png" alt="诊断审批" width="500"/>
  <img src="ProjectImage/历史诊断.png" alt="历史诊断" width="500"/>
</p>

### 深色模式
<p align="center">
  <img src="ProjectImage/深色模式.png" alt="深色模式" width="500"/>
</p>

### 后台管理
<p align="center">
  <img src="ProjectImage/后台管理-系统概览.png" alt="后台管理-系统概览" width="380"/>
  <img src="ProjectImage/后台管理-用户管理.png" alt="后台管理-用户管理" width="380"/>
  <img src="ProjectImage/后台管理-患者管理.png" alt="后台管理-患者管理" width="380"/>
</p>
<p align="center">
  <img src="ProjectImage/后台管理-权重文件管理.png" alt="后台管理-权重文件管理" width="380"/>
  <img src="ProjectImage/后台管理-大模型API管理.png" alt="后台管理-大模型API管理" width="380"/>
  <img src="ProjectImage/后台管理-审计日志.png" alt="后台管理-审计日志" width="380"/>
</p>
<p align="center">
  <img src="ProjectImage/后台管理-系统设置.png" alt="后台管理-系统设置" width="500"/>
</p>

---

## 技术架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      浏览器 (Browser)                        │
│  Vue 3 + TypeScript + Element Plus + ECharts + Pinia        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 业务端    │ │ 管理端    │ │ 登录页    │ │ 公共组件  │       │
│  │ MainLayout│ │AdminLayout│ │LoginPage │ │ API层     │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
└───────┼────────────┼────────────┼────────────┼───────────────┘
        │ HTTP/API   │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Flask 后端 (Port 5000)                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  API 层 (Blueprints)                 │    │
│  │ auth │ users │ patients │ diagnose │ reports        │    │
│  │ batch │ triage │ chat │ model_weights │ llm         │    │
│  │ llm_configs │ audit │ settings │ dashboard │ approvals│   │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │                    服务层 (Services)                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │    │
│  │  │ ai_service   │  │ llm_service  │  │report_svc │  │    │
│  │  │ ONNX推理引擎  │  │ 大模型调用    │  │PDF生成   │  │    │
│  │  │ Grad-CAM热力图│  │ 报告生成     │  │          │  │    │
│  │  │ 批量并行处理  │  │ 流式对话     │  │          │  │    │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │                    数据层 (Models)                     │    │
│  │ User │ Patient │ Diagnosis │ DiseaseProbability      │    │
│  │ Report │ BatchRecord │ ModelWeight │ LlmConfig       │    │
│  │ TriageRecord │ AiChatSession │ AiChatMessage         │    │
│  │ AuditLog │ SystemSetting │ UserPreference           │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐    │
│  │              SQLite (aixray.db)                       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    工具层 (Utils)                     │    │
│  │ auth (JWT) │ encryption (AES) │ validators          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │ ONNX 模型 │    │ PyTorch  │    │ 外部 LLM API │
  │best_model │    │ .pth 权重 │    │ 通义千问等   │
  │  .onnx    │    │  (GradCAM)│    │ OpenAI兼容   │
  └──────────┘    └──────────┘    └──────────────┘
```

### 技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **前端框架** | Vue 3 | ^3.5.32 | Composition API + `<script setup>` |
| **开发语言** | TypeScript | ~6.0.2 | 类型安全 |
| **构建工具** | Vite | ^8.0.4 | 极速 HMR / 构建 |
| **UI 组件库** | Element Plus | ^2.13.7 | 企业级 Vue 3 组件库 |
| **图标库** | @element-plus/icons-vue | ^2.3.2 | 内置 SVG 图标 |
| **状态管理** | Pinia | ^3.0.4 | Vue 3 官方推荐 |
| **路由** | Vue Router | ^4.6.4 | History 模式 |
| **HTTP 客户端** | Axios | ^1.15.0 | 请求/响应拦截器 |
| **图表库** | ECharts + vue-echarts | ^6.0.0 / ^8.0.1 | 数据可视化 |
| **CSS 预处理** | Sass | ^1.99.0 | CSS 变量主题系统 |
| **后端框架** | Flask | >=3.0.0 | Python Web 框架 |
| **ORM** | Flask-SQLAlchemy | >=3.1.1 | SQLite 数据库 |
| **AI 推理** | PyTorch | >=2.0.0 | DenseNet-121 模型 |
| **加速推理** | ONNX Runtime | >=1.18.0 | 2-5x 推理加速 |
| **GPU 加速** | onnxruntime-gpu / DirectML | — | CUDA / DirectX GPU |
| **视觉处理** | OpenCV + Pillow | >=4.9.0 / >=10.0.0 | 图像预处理 |
| **大模型** | OpenAI SDK | >=1.0.0 | 兼容多种 LLM |
| **报告生成** | ReportLab | >=4.0.0 | PDF 报告导出 |
| **实时通信** | Flask-SocketIO | >=5.3.6 | WebSocket 支持 |
| **限流** | Flask-Limiter | >=3.5.0 | API 频率限制 |
| **跨域** | Flask-CORS | >=4.0.0 | CORS 配置 |
| **加密** | cryptography | >=42.0.0 | AES API Key 加密 |
| **生产服务器** | Gunicorn + Gevent | >=21.0.0 | 高并发部署 |

---

## 模块说明

### 后端模块 (`backend/`)

```
backend/
├── app.py                  # Flask 应用工厂, 蓝图注册, 静态文件服务
├── config.py               # 配置管理 (开发/生产环境, JWT, DB, LLM)
├── extensions.py           # Flask 扩展初始化 (DB, CORS, SocketIO, Limiter)
├── init_db.py              # 数据库初始化脚本 (默认用户/患者/设置)
├── requirements.txt        # Python 依赖
│
├── api/                    # API 路由层 (15 个 Blueprint)
│   ├── auth.py             # 认证: 登录/登出/修改密码/Token刷新
│   ├── users.py            # 用户: CRUD/密码重置/偏好设置
│   ├── patients.py         # 患者: CRUD/关联查询
│   ├── diagnose.py         # 单张诊断: 上传/AI推理/报告生成
│   ├── reports.py          # 报告: 查询/PDF下载
│   ├── batch.py            # 批量诊断: 多图上传/异步处理/进度轮询
│   ├── triage.py           # 智能分诊: 症状分析/分诊评估/记录
│   ├── chat.py             # AI咨询: 会话管理/SSE流式对话
│   ├── model_weights.py    # 权重管理: 上传/列表/切换激活
│   ├── llm_configs.py      # LLM配置: CRUD/测试连接/加密存储
│   ├── llm.py              # LLM调用: 直接调用接口
│   ├── audit.py            # 审计日志: 记录/查询/清理
│   ├── settings.py         # 系统设置: 读写配置项
│   ├── dashboard.py        # 数据看板: 统计聚合接口
│   └── approvals.py        # 诊断审批: 审核/驳回/状态流转
│
├── models/                 # SQLAlchemy ORM 模型 (14 张表)
│   ├── user.py             # users 表
│   ├── patient.py          # patients 表
│   ├── diagnosis.py        # diagnoses + disease_probabilities 表
│   ├── report.py           # reports 表
│   ├── batch.py            # batch_records 表
│   ├── model_weight.py     # model_weights 表
│   ├── llm_config.py       # llm_configs 表
│   ├── triage.py           # triage_records 表
│   ├── chat.py             # ai_chat_sessions + ai_chat_messages 表
│   ├── audit.py            # audit_logs 表
│   └── settings.py         # system_settings + user_preferences + login_sessions
│
├── services/               # 业务服务层
│   ├── ai_service.py       # AI推理核心 (ONNX/PyTorch/Grad-CAM/批量处理)
│   ├── llm_service.py      # LLM服务 (报告生成/流式对话/分诊分析)
│   ├── report_service.py   # 报告组装服务
│   └── pdf_service.py      # PDF 生成服务
│
├── utils/                  # 工具函数
│   ├── auth.py             # JWT Token 生成/验证
│   ├── encryption.py       # AES 加密/解密 (API Key 安全存储)
│   └── validators.py       # 数据校验器
│
├── data/                   # SQLite 数据库目录
│   └── aixray.db           # SQLite 数据库文件
│
├── uploads/                # 用户上传文件
│   ├── images/             # 原始 X 光影像
│   ├── heatmaps/           # Grad-CAM 热力图
│   └── reports/            # 生成的 PDF 报告
│
├── weights/                # AI 模型权重文件
│   ├── best_model.onnx     # ONNX 格式模型 (主推)
│   └── model_*.pth         # PyTorch 格式权重 (Grad-CAM 用)
│
└── scripts/
    └── convert_to_onnx.py  # PyTorch → ONNX 模型转换脚本
```

### 前端模块 (`frontend/`)

```
frontend/
├── index.html              # HTML 入口
├── package.json            # NPM 依赖配置
├── vite.config.ts          # Vite 构建配置 (代理/别名/插件)
├── tsconfig.json           # TypeScript 配置
│
├── public/
│   └── favicon.svg         # 网站图标 (医疗/X光主题 SVG)
│
├── src/
│   ├── main.ts             # 应用入口 (Vue/Pinia/Router/ElementPlus 注册)
│   ├── App.vue             # 根组件 (router-view)
│   │
│   ├── router/
│   │   └── index.ts        # 路由配置 (业务端7页 + 管理端7页 + 守卫)
│   │
│   ├── stores/             # Pinia 状态管理
│   │   ├── auth.ts         # 认证状态 (用户信息/Token/角色)
│   │   ├── app.ts          # 应用状态 (侧边栏折叠/主题)
│   │   └── consultation.ts # 咨询会话状态
│   │
│   ├── api/                # API 服务层 (Axios 封装)
│   │   ├── index.ts        # Axios 实例 + 拦截器
│   │   ├── auth.ts         # 认证 API
│   │   ├── users.ts        # 用户 API
│   │   ├── patients.ts     # 患者 API
│   │   ├── diagnose.ts     # 诊断 API
│   │   ├── reports.ts      # 报告 API
│   │   ├── batch.ts        # 批量诊断 API
│   │   ├── triage.ts       # 分诊 API
│   │   ├── chat.ts         # AI咨询 API
│   │   ├── dashboard.ts    # 看板 API
│   │   ├── approvals.ts    # 审批 API
│   │   ├── model-weights.ts # 权重 API
│   │   ├── llm-configs.ts  # LLM配置 API
│   │   ├── llm.ts          # LLM调用 API
│   │   ├── audit.ts        # 审计日志 API
│   │   ├── settings.ts     # 设置 API
│   │   └── users.ts        # 用户偏好 API
│   │
│   ├── layouts/            # 布局组件
│   │   ├── MainLayout.vue  # 业务端布局 (侧边栏 + 顶栏 + 内容区)
│   │   └── AdminLayout.vue # 管理端布局 (侧边栏 + 顶栏 + 内容区)
│   │
│   ├── views/              # 页面组件
│   │   ├── login/LoginPage.vue       # 登录页
│   │   ├── dashboard/DashboardPage.vue # 数据看板
│   │   ├── diagnose/DiagnosePage.vue  # 诊断中心
│   │   ├── batch/BatchPage.vue        # 批量诊断
│   │   ├── triage/TriagePage.vue      # 智能分诊
│   │   ├── chat/ChatPage.vue          # AI 咨询
│   │   ├── history/HistoryPage.vue    # 诊断历史
│   │   ├── approval/ApprovalPage.vue  # 诊断审批
│   │   ├── admin/OverviewPage.vue     # 管理端-系统概览
│   │   ├── admin/UsersPage.vue        # 管理端-用户管理
│   │   ├── admin/PatientsPage.vue     # 管理端-患者管理
│   │   ├── admin/ModelsPage.vue       # 管理端-权重文件管理
│   │   ├── admin/LlmPage.vue          # 管理端-大模型API管理
│   │   ├── admin/AuditPage.vue        # 管理端-审计日志
│   │   └── admin/SettingsPage.vue     # 管理端-系统设置
│   │
│   ├── styles/
│   │   └── variables.css   # 全局 CSS 变量 (主题色/间距/圆角/阴影)
│   │
│   ├── components/         # 公共组件
│   └── utils/              # 工具函数
│
└── README.md               # 前端说明 (Vite 默认模板)
```

---

## 数据库设计

### ER 关系概览

```
users (用户)
  ├── 1:N → diagnoses (作为医生 doctor_id)
  ├── 1:N → diagnoses (作为技师 technician_id)
  ├── 1:N → chat_sessions (AI 咨询会话)
  ├── 1:N → audit_logs (审计日志)
  └── 1:1 → user_preferences (用户偏好)

patients (患者)
  ├── 1:N → diagnoses (诊断记录)
  └── 1:N → triage_records (分诊记录)

diagnoses (诊断记录)
  ├── N:1 → patients (患者)
  ├── N:1 → users (医生)
  ├── N:1 → users (技师)
  ├── N:1 → batch_records (批次)
  ├── 1:N → disease_probabilities (疾病概率)
  └── 1:N → reports (报告)

disease_probabilities (疾病概率)
  └── N:1 → diagnoses

reports (报告)
  └── N:1 → diagnoses

batch_records (批量记录)
  └── 1:N → diagnoses
```

### 核心表结构

#### `users` — 用户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| username | String(50) UNIQUE | 用户名 |
| password_hash | String(255) | 密码哈希 (werkzeug) |
| real_name | String(50) | 真实姓名 |
| role | String(20) | 角色: admin / doctor / nurse |
| department | String(50) | 科室 |
| license_number | String(50) | 执业证书号 |
| email / phone | String | 联系方式 |
| status | String(20) | 状态: active / disabled |
| last_login_at | DateTime | 最后登录时间 |
| created_at / updated_at | DateTime | 创建/更新时间 |

#### `patients` — 患者表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| patient_no | String(50) UNIQUE | 患者编号 (如 P20260315001) |
| name | String(50) | 姓名 |
| gender | String(10) | 性别: male / female |
| birth_date / age | Date / Integer | 出生日期 / 年龄 |
| id_card | String(18) | 身份证号 |
| phone / address | String | 联系电话 / 地址 |
| emergency_contact / phone | String | 紧急联系人 |
| blood_type | String(5) | 血型 |
| height / weight | Float | 身高(cm) / 体重(kg) |
| medical_history | Text (JSON) | 既往病史 |
| allergy_history | Text | 过敏史 |
| created_by | FK(users) | 创建人 |

#### `diagnoses` — 诊断记录表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| diagnosis_no | String(50) UNIQUE | 诊断编号 |
| patient_id | FK(patients) | 患者 |
| doctor_id | FK(users) | 诊断医生 |
| technician_id | FK(users) | 上传技师 |
| image_path | String(500) | 影像路径 |
| heatmap_path | String(500) | 热力图路径 |
| image_metadata | Text (JSON) | 影像元数据 |
| model_version | String(50) | 模型版本 |
| report_status | String(30) | 状态: pending_review / approved / rejected |
| diagnosis_type | String(20) | 类型: single / batch |
| batch_id | FK(batch_records) | 所属批次 |
| created_at / reviewed_at | DateTime | 创建/审核时间 |

#### `disease_probabilities` — 疾病概率表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| diagnosis_id | FK(diagnoses) | 诊断记录 |
| disease_code | String(30) | 疾病代码 (如 Pneumonia) |
| disease_name_zh | String(50) | 中文名称 (如 肺炎) |
| probability | Float | 检测概率 (0~1) |
| threshold_exceeded | Boolean | 是否超过阈值 |
| (diagnosis_id, disease_code) | UNIQUE | 联合唯一约束 |

#### 其他关键表

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `reports` | 诊断报告 | findings / impression / recommendations / ai_model_used / pdf_path |
| `batch_records` | 批量诊断记录 | total_count / processed_count / status / progress_json |
| `model_weights` | 模型权重 | filename / file_path / format / size / is_active |
| `llm_configs` | LLM 配置 | provider / model_name / api_endpoint / api_key_encrypted / default_params |
| `triage_records` | 分诊记录 | symptoms / severity / vital_signs / category / urgency |
| `ai_chat_sessions` | AI 会话 | title / persona / message_count |
| `ai_chat_messages` | AI 消息 | session_id / role / content |
| `audit_logs` | 审计日志 | action / resource_type / detail / ip_address |
| `system_settings` | 系统设置 | setting_key / setting_value / value_type |
| `user_preferences` | 用户偏好 | theme / language |

---

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:5000/api/v1`
- **认证方式**: Bearer Token (JWT)
- **Content-Type**: `application/json`
- **响应格式**: `{ code: 200, message: "ok", data: {...} }`

### 认证模块 (`/auth`)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/login` | 用户登录 (返回 JWT Token) |
| POST | `/auth/logout` | 用户登出 |
| POST | `/auth/password` | 修改密码 |
| GET | `/auth/me` | 获取当前用户信息 |

### 用户模块 (`/users`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/users` | 用户列表 (分页+搜索) |
| POST | `/users` | 创建用户 |
| PUT | `/users/:id` | 更新用户 |
| DELETE | `/users/:id` | 删除用户 |
| POST | `/users/:id/reset-password` | 重置密码 |
| PUT | `/users/preferences` | 更新个人偏好 |

### 患者模块 (`/patients`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/patients` | 患者列表 (分页+搜索) |
| POST | `/patients` | 创建患者 |
| PUT | `/patients/:id` | 更新患者 |
| DELETE | `/patients/:id` | 删除患者 |
| GET | `/patients/:id/diagnoses` | 患者的诊断记录 |

### 诊断模块 (`/diagnose`)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/diagnose/upload` | 上传影像并执行 AI 诊断 |
| POST | `/diagnose/:id/report` | 为诊断记录生成报告 |
| GET | `/diagnose/:id` | 获取诊断详情 |
| GET | `/diagnose` | 诊断记录列表 |

### 批量诊断模块 (`/batch`)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/batch/upload` | 批量上传影像 |
| POST | `/batch/diagnose` | 开始批量诊断 (异步) |
| GET | `/batch/progress/:batch_id` | 查询批量进度 |
| POST | `/batch/cancel/:batch_id` | 取消批量任务 |
| GET | `/batch/history` | 批量历史记录 |

### 智能分诊模块 (`/triage`)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/triage/analyze` | 执行分诊分析 |
| POST | `/triage/records` | 保存分诊记录 |
| GET | `/triage/records` | 分诊记录列表 |
| GET | `/triage/records/:id` | 分诊详情 |

### AI 咨询模块 (`/chat`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/chat/sessions` | 会话列表 |
| POST | `/chat/sessions` | 新建会话 |
| DELETE | `/chat/sessions/:id` | 删除会话 |
| GET | `/chat/sessions/:id/messages` | 消息历史 |
| POST | `/chat/send` | 发送消息 (SSE 流式返回) |

### 报告模块 (`/reports`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/reports` | 报告列表 |
| GET | `/reports/:id` | 报告详情 |
| GET | `/reports/:id/pdf` | 下载 PDF 报告 |

### 审批模块 (`/approvals`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/approvals` | 待审批列表 |
| POST | `/approvals/:id/approve` | 通过审批 |
| POST | `/approvals/:id/reject` | 驳回审批 |
| GET | `/approvals/history` | 审批历史 |

### 权重管理模块 (`/model-weights`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/model-weights` | 权重文件列表 |
| POST | `/model-weights/upload` | 上传权重文件 |
| POST | `/model-weights/:id/activate` | 切换激活权重 |
| DELETE | `/model-weights/:id` | 删除权重文件 |

### LLM 配置模块 (`/llm-configs`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/llm-configs` | LLM 配置列表 |
| POST | `/llm-configs` | 新建配置 |
| PUT | `/llm-configs/:id` | 更新配置 |
| DELETE | `/llm-configs/:id` | 删除配置 |
| POST | `/llm-configs/:id/test` | 测试连接 |
| POST | `/llm-configs/:id/set-default` | 设为默认 |

### 审计日志模块 (`/audit`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/audit/logs` | 日志列表 (分页+筛选) |
| GET | `/audit/actions` | 操作类型列表 |
| POST | `/audit/cleanup` | 清理过期日志 |

### 系统设置模块 (`/settings`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/settings` | 所有设置 |
| PUT | `/settings/:key` | 更新单个设置 |

### 数据看板模块 (`/dashboard`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/dashboard/stats` | 统计概览数据 |
| GET | `/dashboard/chart-data` | 图表数据 |

### 健康检查
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 健康检查 |

---

## 快速开始

### 环境要求

| 环境 | 要求 |
|------|------|
| **操作系统** | Windows 10+ / Linux (Ubuntu 20.04+) / macOS |
| **Python** | 3.9+ (推荐 3.10+) |
| **Node.js** | 18+ (推荐 20+) |
| **npm** | 9+ |
| **GPU** (可选) | NVIDIA CUDA 11.8+ 或 AMD DirectML |
| **内存** | 8GB+ (推荐 16GB) |
| **磁盘** | 5GB+ 可用空间 |

### 1. 克隆项目

```bash
git clone <repository-url>
cd AIX-RayIntelligentDiagnosisSystemV3.0
```

### 2. 后端环境搭建

```bash
# 进入后端目录
cd backend

# 创建虚拟环境 (推荐)
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 如果有 NVIDIA GPU，安装 GPU 版 ONNX Runtime:
pip install onnxruntime-gpu

# 如果是 AMD GPU 或 Windows DirectX:
pip install onnxruntime-directml

# CPU 推理 (默认已包含):
# pip install onnxruntime
```

### 3. 初始化数据库

```bash
cd backend
python init_db.py
```

这将创建 SQLite 数据库并插入默认数据：
- 1 名管理员账号
- 5 名医生账号
- 2 名护士账号
- 10 名示例患者
- 默认 LLM 配置
- 系统默认设置

### 4. 配置环境变量 (可选)

在项目根目录创建 `.env` 文件：

```env
# Flask 环境
FLASK_ENV=development

# JWT 密钥 (生产环境请修改!)
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# AI 推理设备: auto / cuda / cpu
AI_DEVICE=auto

# 大模型 API Key (阿里云通义千问)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# LLM 加密密钥
LLM_ENCRYPTION_KEY=your-encryption-key-32chars
```

### 5. 启动后端

```bash
cd backend
python app.py
```

后端将启动在 `http://localhost:5000`，控制台输出：

```
==================================================
  胸影智诊V3.0 - AI智能辅助诊断系统
  访问地址: http://localhost:5000
==================================================
[AI服务] GPU: NVIDIA RTX 4090 (24.0GB)
[AI服务] ✅ ONNX 模型加载成功
[AI服务] ONNX 引擎: DmlExecutionProvider
 * Running on http://0.0.0.0:5000
```

### 6. 前端环境搭建

```bash
# 新开终端，进入前端目录
cd frontend

# 安装依赖
npm install
```

### 7. 启动前端开发服务器

```bash
npm run dev
```

前端将启动在 `http://localhost:5173`，Vite 开发代理会自动转发 API 请求到后端。

### 8. 访问系统

打开浏览器访问：**http://localhost:5173**

使用默认账号登录即可体验全部功能。

---

## 部署指南

### 生产环境部署

#### 方案一：传统部署 (Gunicorn + Nginx)

**1. 构建前端**

```bash
cd frontend
npm run build
```

生成的静态文件在 `frontend/dist/` 目录。

**2. 配置 Nginx**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源 (图片/热力图/报告)
    location /static {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

**3. 启动后端 (Gunicorn + Gevent)**

```bash
cd backend
export FLASK_ENV=production
gunicorn \
    --bind 127.0.0.1:5000 \
    --worker-class gevent \
    --workers 4 \
    --worker-connections 1000 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    'app:create_app()'
```

**4. Systemd 服务 (可选)**

创建 `/etc/systemd/system/aixray.service`:

```ini
[Unit]
Description=AIX-Ray Intelligent Diagnosis System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/AIX-RayIntelligentDiagnosisSystemV3.0/backend
Environment=FLASK_ENV=production
Environment=PATH=/opt/AIX-RayIntelligentDiagnosisSystemV3.0/backend/venv/bin
ExecStart=/opt/AIX-RayIntelligentDiagnosisSystemV3.0/backend/venv/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --worker-class gevent \
    --workers 4 \
    --timeout 120 \
    'app:create_app'
Restart=always
Restart=sec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable aixray
sudo systemctl start aixray
sudo systemctl status aixray
```

#### 方案二：Docker 部署

**Dockerfile (后端)**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir onnxruntime  # or onnxruntime-gpu

# 复制代码
COPY . .

# 创建必要目录
RUN mkdir -p data uploads/images uploads/heatmaps uploads/reports weights

# 初始化数据库
RUN python init_db.py

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
     "--worker-class", "gevent", "--workers", "4", \
     "--timeout", "120", "'app:create_app()'"]
```

**Dockerfile (前端)**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: aixray-backend
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AI_DEVICE=auto
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
      - ./weights:/app/weights
    ports:
      - "5000:5000"
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: aixray-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

启动：

```bash
docker-compose up -d
```

---

## 项目结构

```
AIX-RayIntelligentDiagnosisSystemV3.0/
│
├── backend/                 # Python Flask 后端
│   ├── api/                 # 15 个 API 蓝图模块
│   ├── models/              # 14 个 ORM 数据模型
│   ├── services/            # 核心业务服务 (AI/LLM/报告)
│   ├── utils/               # 工具函数 (认证/加密/校验)
│   ├── data/                # SQLite 数据库
│   ├── uploads/             # 上传文件 (影像/热力图/报告)
│   ├── weights/             # AI 模型权重 (.onnx/.pth)
│   ├── scripts/             # 辅助脚本 (模型转换)
│   ├── app.py               # Flask 应用入口
│   ├── config.py            # 配置管理
│   ├── extensions.py        # Flask 扩展
│   ├── init_db.py           # 数据库初始化
│   └── requirements.txt     # Python 依赖
│
├── frontend/                # Vue 3 前端
│   ├── public/              # 静态资源 (favicon)
│   ├── src/
│   │   ├── api/             # 16 个 API 服务模块
│   │   ├── views/           # 15 个页面组件
│   │   ├── layouts/         # 2 个布局组件
│   │   ├── stores/          # 3 个 Pinia Store
│   │   ├── router/          # 路由配置
│   │   ├── styles/          # 全局样式变量
│   │   ├── components/      # 公共组件
│   │   ├── utils/           # 工具函数
│   │   ├── App.vue          # 根组件
│   │   └── main.ts          # 入口文件
│   ├── index.html           # HTML 入口
│   ├── package.json         # NPM 依赖
│   ├── vite.config.ts       # Vite 配置
│   └── tsconfig.json        # TS 配置
│
├── ProjectImage/            # 项目截图 (本文档引用)
│   ├── 登录界面.png
│   ├── 数据看板.png
│   ├── 诊断中心-*.png
│   ├── 批量诊断-*.png
│   ├── 智能分诊-*.png
│   ├── AI咨询-*.png
│   ├── 诊断审批.png
│   ├── 历史诊断.png
│   ├── 深色模式.png
│   └── 后台管理-*.png
│
├── batch_sample_images/     # 示例 X 光影像 (用于测试)
│
├── .env                     # 环境变量 (需自行创建)
└── README.md                # 本文档
```

---

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `FLASK_ENV` | development | 运行环境: development / production |
| `SECRET_KEY` | aixray-default-* | Flask Session 密钥 (**生产环境必须修改**) |
| `JWT_SECRET_KEY` | aixray-default-* | JWT Token 签名密钥 (**生产环境必须修改**) |
| `JWT_ACCESS_TOKEN_EXPIRES` | 2592000 | Token 有效期 (秒), 默认 30 天 |
| `OPENAI_API_KEY` | (空) | 大模型 API Key |
| `OPENAI_API_BASE` | 阿里云 DashScope | LLM API 地址 |
| `LLM_ENCRYPTION_KEY` | aixray-llm-* | API Key 加密密钥 |
| `AI_DEVICE` | auto | AI 推理设备: auto / cuda / cpu |
| `DISEASE_THRESHOLD` | 0.7 | 疾病检测阈值 |
| `AUDIT_RETENTION_DAYS` | 180 | 审计日志保留天数 |

### 系统设置 (通过管理后台动态配置)

| 设置键 | 默认值 | 说明 |
|--------|--------|------|
| `system_name` | 胸影智诊V3.0 | 系统名称 |
| `disease_threshold` | 0.7 | 疾病概率告警阈值 (0~1) |
| `max_upload_size` | 20 | 最大上传文件大小 (MB) |
| `session_timeout` | 12 | 会话超时时间 (小时) |
| `audit_retention_days` | 180 | 审计日志保留天数 |
| `batch_concurrency` | 2 | 批量处理并发数 |

---

## 默认账号

> **重要**: 以下为初始化脚本创建的默认账号，请在生产环境中**立即修改密码**！

| 角色 | 用户名 | 密码 | 姓名 | 科室 |
|------|--------|------|------|------|
| **管理员** | `admin` | `admin123` | 系统管理员 | 信息科 |
| 医生 | `doctor_wang` | `doctor123` | 王建国 | 放射科 |
| 医生 | `doctor_li` | `doctor123` | 李秀芳 | 放射科 |
| 医生 | `doctor_zhang` | `doctor123` | 张明远 | 呼吸内科 |
| 医生 | `doctor_chen` | `doctor123` | 陈思远 | 影像科 |
| 医生 | `doctor_liu` | `doctor123` | 刘婉清 | 胸外科 |
| 护士 | `nurse_sun` | `nurse123` | 孙小美 | 放射科 |
| 护士 | `nurse_zhao` | `nurse123` | 赵雅婷 | 呼吸内科 |

---

## 开发说明

### 开发命令

**后端:**
```bash
cd backend
# 激活虚拟环境后
python app.py              # 启动开发服务器 (debug 模式, 热重载)
python init_db.py          # 重新初始化数据库
```

**前端:**
```bash
cd frontend
npm run dev                # 启动开发服务器 (http://localhost:5173)
npm run build              # 构建生产版本
npm run preview            # 预览生产构建
```

### AI 模型相关

**PyTorch 转 ONNX (可选加速):**

```bash
cd backend
python scripts/convert_to_onnx.py
```

转换后的 `.onnx` 文件放入 `backend/weights/` 目录即可被自动加载。

**模型加载优先级:**
1. `weights/*.onnx` — ONNX 格式 (优先，速度快 2-5x)
2. `weights/*.pth` 或 `*.pt` — PyTorch 格式 (回退)
3. `ChestX-ray14/output/best_model.pth` — 默认路径

**GPU 推理支持:**
- **NVIDIA GPU**: 安装 `onnxruntime-gpu`，设置 `AI_DEVICE=cuda`
- **AMD/Windows GPU**: 安装 `onnxruntime-directml`，自动使用 DirectML
- **CPU 推理**: 默认支持，无需额外安装

### 前端开发规范

- 使用 `<script setup lang="ts">` 组合式 API
- Element Plus 组件按需自动导入 (unplugin-vue-components)
- API 统一在 `src/api/` 目录封装
- 路由配置在 `src/router/index.ts`，含权限守卫
- 全局 CSS 变量定义在 `src/styles/variables.css`
- 主题切换基于 CSS 变量 + Element Plus dark css-vars

### 后端开发规范

- Flask Blueprint 模式组织 API
- SQLAlchemy ORM 操作数据库
- JWT Token 认证 (Flask-Less 式自实现)
- API Key AES 加密存储
- 全局异常处理返回 JSON
- 审计日志自动记录关键操作

### 文件命名约定 (批量诊断)

批量诊断支持从文件名自动解析患者信息，格式如下：

```
P{编号}-{姓名}-{性别}-{年龄}-{症状}-{序号}.png
```

示例：
```
P20260315001-张伟-male-45-Cough-001.png
P20260315002-李娜-female-32-Routine-002.png
```

字段说明：
- `P` + 编号 = 患者编号
- 姓名 = 中文名
- 性别 = `male` / `female`
- 年龄 = 数字
- 症状 = `Cough`(咳嗽) / `ChestPain`(胸痛) / `Dyspnea`(呼吸困难) / `Fever`(发热) / `Routine`(常规体检) / `Wheeze`(喘息) / `Fatigue`(乏力) / `FollowUp`(复查)
- 序号 = 3 位数字

---

## 许可证

本项目仅供学习和研究使用。

---

<p align="center">
  <strong>胸影智诊 V3.0</strong> — 让 AI 赋能医学影像诊断
</p>
