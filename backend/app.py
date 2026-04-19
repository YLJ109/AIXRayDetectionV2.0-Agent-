"""Flask应用入口 - 胸影智诊V3.0"""
import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import get_config
from extensions import db, cors, socketio, limiter
from api import all_blueprints


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    config_class = get_config()
    app.config.from_object(config_class)

    # 确保数据目录存在
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app)
    limiter.init_app(app)

    # 注册蓝图
    for bp in all_blueprints:
        app.register_blueprint(bp)

    # 静态文件服务（上传的图片、热力图等）
    upload_folder = app.config['UPLOAD_FOLDER']

    @app.route('/static/images/<path:filename>')
    def serve_image(filename):
        return send_from_directory(os.path.join(upload_folder, 'images'), filename)

    @app.route('/static/heatmaps/<path:filename>')
    def serve_heatmap(filename):
        return send_from_directory(os.path.join(upload_folder, 'heatmaps'), filename)

    @app.route('/static/reports/<path:filename>')
    def serve_report(filename):
        return send_from_directory(os.path.join(upload_folder, 'reports'), filename)

    # 健康检查
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        return {'code': 200, 'message': 'ok', 'data': {'status': 'healthy'}}

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(e):
        return {'code': 404, 'message': '资源不存在'}, 404

    @app.errorhandler(500)
    def internal_error(e):
        return {'code': 500, 'message': '服务器内部错误'}, 500

    # 应用启动后加载AI模型
    with app.app_context():
        from services.ai_service import load_model
        try:
            load_model()
        except Exception as e:
            print(f"[启动] AI模型加载失败: {e}")
            print("[启动] 系统将以无模型模式启动，诊断功能不可用")

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("  胸影智诊V3.0 - AI智能辅助诊断系统")
    print("  访问地址: http://localhost:5000")
    print("=" * 50)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
