# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 数据库迁移脚本
自动检测并添加缺失的列，解决 'no such column' 异常
安全增量迁移，不破坏现有数据

使用方法:
    python backend/migrate_db.py
"""
import os
import sys
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# 数据库路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DB_DIR, 'aixray_dev.db')


def get_table_columns(cursor, table_name):
    """获取表的列名列表"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def column_exists(cursor, table_name, column_name):
    """检查列是否存在"""
    return column_name in get_table_columns(cursor, table_name)


def safe_add_column(cursor, table_name, column_name, column_type, default=None):
    """安全地添加新列（如果不存在）"""
    if column_exists(cursor, table_name, column_name):
        logger.info(f"  [跳过] {table_name}.{column_name} 已存在")
        return False

    sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
    if default is not None:
        sql += f" DEFAULT {default}"
    
    try:
        cursor.execute(sql)
        logger.info(f"  [新增] {table_name}.{column_name} ({column_type})")
        return True
    except Exception as e:
        logger.error(f"  [失败] {table_name}.{column_name}: {str(e)}")
        return False


def run_migrations():
    """执行所有数据库迁移"""
    if not os.path.exists(DB_PATH):
        logger.warning(f"数据库文件不存在: {DB_PATH}")
        logger.info("将使用 db.create_all() 创建新表，无需迁移")
        return True

    logger.info(f"数据库路径: {DB_PATH}")
    logger.info("=" * 50)

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.cursor()

        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"当前数据库表: {tables}")

        total_changes = 0

        # ========== diagnosis_records 表迁移 ==========
        if 'diagnosis_records' in tables:
            logger.info("\n--- 迁移 diagnosis_records ---")
            
            if safe_add_column(cursor, 'diagnosis_records', 'inference_time', 'REAL', default=0.0):
                total_changes += 1

        # ========== system_configs 表迁移 ==========
        if 'system_configs' in tables:
            logger.info("\n--- 迁移 system_configs ---")
            
            if safe_add_column(cursor, 'system_configs', 'group_name', 'VARCHAR(50)', default="'general'"):
                total_changes += 1

        # ========== llm_providers 表迁移 ==========
        if 'llm_providers' in tables:
            logger.info("\n--- 迁移 llm_providers ---")
            
            if safe_add_column(cursor, 'llm_providers', 'priority', 'INTEGER', default=0):
                total_changes += 1
            if safe_add_column(cursor, 'llm_providers', 'last_used_at', 'DATETIME'):
                total_changes += 1
            if safe_add_column(cursor, 'llm_providers', 'total_calls', 'INTEGER', default=0):
                total_changes += 1
            if safe_add_column(cursor, 'llm_providers', 'last_error', 'TEXT'):
                total_changes += 1

        conn.commit()
        conn.close()

        logger.info("\n" + "=" * 50)
        if total_changes > 0:
            logger.info(f"迁移完成，共执行 {total_changes} 项变更")
        else:
            logger.info("数据库已是最新版本，无需迁移")

        return True

    except Exception as e:
        logger.error(f"迁移失败: {str(e)}")
        return False


def init_model_config_defaults(conn):
    """初始化模型参数默认配置到 system_configs 表"""
    logger.info("\n--- 初始化模型默认配置 ---")
    cursor = conn.cursor()

    # 默认模型参数配置
    defaults = [
        {
            'key': 'model_confidence_threshold',
            'value': '0.5',
            'type': 'number',
            'description': 'AI诊断置信度阈值(0-1)，低于此值的诊断标记为低置信度',
            'group': 'model'
        },
        {
            'key': 'model_image_size',
            'value': '224',
            'type': 'number',
            'description': '模型输入图像尺寸(像素)',
            'group': 'model'
        },
        {
            'key': 'model_heatmap_size',
            'value': '1024',
            'type': 'number',
            'description': 'Grad-CAM热力图生成尺寸(像素)',
            'group': 'model'
        },
        {
            'key': 'model_gradcam_alpha',
            'value': '0.4',
            'type': 'number',
            'description': 'Grad-CAM原图叠加透明度(0-1)',
            'group': 'model'
        },
        {
            'key': 'model_gradcam_beta',
            'value': '0.6',
            'type': 'number',
            'description': 'Grad-CAM热力图叠加透明度(0-1)',
            'group': 'model'
        },
    ]

    inserted = 0
    for cfg in defaults:
        try:
            cursor.execute(
                "SELECT id FROM system_configs WHERE config_key = ? AND is_deleted = 0",
                (cfg['key'],)
            )
            if cursor.fetchone():
                logger.info(f"  [跳过] {cfg['key']} 已存在")
                continue

            cursor.execute(
                """INSERT INTO system_configs (config_key, config_value, config_type, description, group_name, is_deleted)
                   VALUES (?, ?, ?, ?, ?, 0)""",
                (cfg['key'], cfg['value'], cfg['type'], cfg['description'], cfg['group'])
            )
            logger.info(f"  [新增] {cfg['key']} = {cfg['value']}")
            inserted += 1
        except Exception as e:
            logger.error(f"  [失败] {cfg['key']}: {str(e)}")

    return inserted


if __name__ == '__main__':
    print("=" * 50)
    print("胸影智诊V2.0 - 数据库迁移工具")
    print("=" * 50)

    success = run_migrations()

    if success and os.path.exists(DB_PATH):
        # 迁移后初始化默认配置
        try:
            conn = sqlite3.connect(DB_PATH)
            init_model_config_defaults(conn)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"初始化默认配置失败: {str(e)}")

    sys.exit(0 if success else 1)
