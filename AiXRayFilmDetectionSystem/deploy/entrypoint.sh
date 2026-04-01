#!/bin/bash
set -e

echo "=========================================="
echo " 胸影智诊V2.0 - 启动脚本"
echo "=========================================="

# 切换到项目目录
cd /app

# 数据库初始化
echo "[1/4] 检查数据库..."
if [ ! -f backend/data/aixray_dev.db ]; then
    echo "  数据库不存在，执行初始化..."
    python -c "
import sys
sys.path.insert(0, '/app')
from backend.app import app
from backend.core.extensions import db
with app.app_context():
    db.create_all()
    print('  数据库表创建完成')
"
    python backend/init_database.py
else
    echo "  数据库已存在，跳过初始化"
fi

# 数据库迁移
echo "[2/4] 执行数据库迁移..."
python backend/migrate_db.py || true

# 确保目录存在
echo "[3/4] 检查运行时目录..."
mkdir -p backend/static/uploads/images
mkdir -p backend/static/heatmaps
mkdir -p backend/static/reports

# 启动 Supervisor
echo "[4/4] 启动服务..."
echo "  - Flask (Gunicorn) on 127.0.0.1:5000"
echo "  - Nginx on :80"
echo "=========================================="

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
