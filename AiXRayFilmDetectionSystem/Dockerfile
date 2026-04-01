# ==================== 多阶段构建：前端 ====================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ==================== 生产镜像 ====================
FROM python:3.11-slim

LABEL maintainer="AiXRayDetectionV2.0"
LABEL description="胸影智诊V2.0 - 企业级医疗AI胸部X光智能辅助诊断系统"

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    nginx \
    supervisor \
    curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 Python 依赖
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制环境变量模板
COPY .env ./backend/.env

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# 复制 Nginx 配置
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY deploy/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# 创建必要目录
RUN mkdir -p /app/backend/static/uploads/images \
             /app/backend/static/heatmaps \
             /app/backend/static/reports \
             /app/backend/weights \
             /app/backend/data \
             /var/log/supervisor

# 暴露端口
EXPOSE 80

# 数据卷：模型权重、上传文件、数据库
VOLUME ["/app/backend/weights", "/app/backend/static", "/app/backend/data"]

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost/api/system/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
