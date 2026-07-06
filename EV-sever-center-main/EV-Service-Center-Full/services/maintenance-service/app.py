# File: services/maintenance-service/app.py
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()

# Khởi tạo Extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager() 

def create_app():
    """Tạo và cấu hình Flask app chính cho Maintenance Service"""
    app = Flask(__name__)
    CORS(app)

    # ===== CẤU HÌNH (Lấy từ .env) =====
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Disable CSRF for JWT

    # FIX: Làm sạch INTERNAL_SERVICE_TOKEN
    internal_token = os.getenv("INTERNAL_SERVICE_TOKEN")
    if internal_token:
        app.config["INTERNAL_SERVICE_TOKEN"] = internal_token.strip()

    app.config["BOOKING_SERVICE_URL"] = os.getenv("BOOKING_SERVICE_URL")
    app.config["USER_SERVICE_URL"] = os.getenv("USER_SERVICE_URL")
    app.config["INVENTORY_SERVICE_URL"] = os.getenv("INVENTORY_SERVICE_URL")
    
    # ===== KHỞI TẠO EXTENSIONS =====
    db.init_app(app)
    jwt.init_app(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({
            "error": "Token invalid or missing.",
            "message": error_string
        }), 401
    # Cấu hình migration riêng cho Maintenance Service
    migrate.init_app(app, db, directory='migrations', version_table='alembic_version_maintenance')

    # ===== IMPORT MODELS & TẠO TABLES =====
    with app.app_context():
        from models.maintenance_model import MaintenanceTask 
        db.create_all()

    # ===== ĐĂNG KÝ BLUEPRINTS (Controllers) =====
    from controllers.maintenance_controller import maintenance_bp
    from controllers.internal_controller import internal_bp

    app.register_blueprint(maintenance_bp)
    app.register_blueprint(internal_bp)

    @app.before_request
    def pre_validate_request():
        from flask import request
        import re

        # 1. GET & POST /api/maintenance/tasks
        if request.path == "/api/maintenance/tasks":
            if request.method == "GET":
                task_id_arg = request.args.get("id")
                if task_id_arg is not None:
                    try:
                        tid = int(task_id_arg)
                        if tid <= 0:
                            return jsonify({"error": "Không tìm thấy Công việc."}), 404
                    except ValueError:
                        return jsonify({"error": "Mã công việc phải là số nguyên"}), 400
            elif request.method == "POST":
                data = request.get_json(silent=True) or {}
                booking_id = data.get("booking_id")
                technician_id = data.get("technician_id")
                if booking_id is None or technician_id is None:
                    return jsonify({"error": "Thiếu booking_id hoặc technician_id"}), 400
                try:
                    b_id = int(booking_id)
                    t_id = int(technician_id)
                    if b_id <= 0 or t_id <= 0:
                        return jsonify({"error": "ID phải lớn hơn 0"}), 400
                except ValueError:
                    return jsonify({"error": "booking_id và technician_id phải là số nguyên"}), 400

        # 2. Check path parameters for task_id, item_id, part_id
        # Match tasks/<id>/status...
        match_status = re.match(r"^/api/maintenance/tasks/(-?\d+)/status$", request.path)
        if match_status:
            if request.method == "PUT":
                task_id = int(match_status.group(1))
                if task_id <= 0:
                    return jsonify({"error": "Không tìm thấy công việc."}), 404
                
                data = request.get_json(silent=True) or {}
                new_status = data.get("status")
                if not new_status:
                    return jsonify({"error": "Missing 'status' field."}), 400
                
                valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
                if new_status not in valid_statuses:
                    return jsonify({"error": "Trạng thái không hợp lệ"}), 400

        # Match tasks/<id>...
        match_task = re.match(r"^/api/maintenance/tasks/(-?\d+)(/.*)?$", request.path)
        if match_task:
            task_id = int(match_task.group(1))
            if task_id <= 0:
                return jsonify({"error": "Không tìm thấy công việc."}), 404

        # Match parts/<id>...
        match_part = re.match(r"^/api/maintenance/parts/(-?\d+)(/.*)?$", request.path)
        if match_part:
            part_id = int(match_part.group(1))
            if part_id <= 0:
                return jsonify({"error": "Không tìm thấy phụ tùng."}), 404

        # Match checklist/<id>...
        match_checklist = re.match(r"^/api/maintenance/checklist/(-?\d+)(/.*)?$", request.path)
        if match_checklist:
            item_id = int(match_checklist.group(1))
            if item_id <= 0:
                return jsonify({"error": "Không tìm thấy mục kiểm tra."}), 404

    # ===== HEALTH CHECK =====
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "Maintenance Service is running!"}), 200

    return app