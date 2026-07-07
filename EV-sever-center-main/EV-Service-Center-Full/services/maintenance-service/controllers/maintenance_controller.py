# File: services/maintenance-service/controllers/maintenance_controller.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from functools import wraps

from services.maintenance_service import MaintenanceService as service

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/api/maintenance")

# --- Decorators (Sao chép Admin Required) ---
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                print(f"🔍 JWT Claims: {claims}")  # Debug logging
                if claims.get("role") in ["admin",]:
                    return fn(*args, **kwargs)
                else:
                    print(f"❌ Role mismatch: {claims.get('role')} != admin")
                    return jsonify(error="Admins only!"), 403
            except Exception as e:
                print(f"❌ JWT Error: {str(e)}")  # Debug logging
                return jsonify(error="Token invalid or missing."), 401
        return decorator
    return wrapper

# --- Reusable Permission Check Helper ---
def _check_task_permission(task_id, current_user_id, claims, required_roles=None):
    """
    Kiểm tra quyền truy cập/thao tác trên Task: Admin, Customer Owner, Technician Owner.
    Trả về (task, is_authorized, is_admin, is_technician_owner)
    """
    task = service.get_task_by_id(task_id)
    if not task:
        return None, False, False, False

    is_admin = claims.get("role") == "admin"
    is_customer = str(task.user_id) == str(current_user_id)
    is_technician_owner = str(task.technician_id) == str(current_user_id)

    # Nếu không yêu cầu role cụ thể, check quyền truy cập cơ bản (Admin HOẶC Owner)
    if not required_roles:
        is_authorized = is_admin or is_customer or is_technician_owner
    # Nếu yêu cầu role cụ thể (ví dụ: chỉ KTV/Admin mới được add parts)
    elif "technician_or_admin" in required_roles:
        is_authorized = is_admin or is_technician_owner
    else:
        is_authorized = False

    return task, is_authorized, is_admin, is_technician_owner

# --- Routes ---

# 1. ADMIN: CREATE TASK (POST /api/maintenance/tasks)
@maintenance_bp.route("/tasks", methods=["POST"])
@admin_required()
def create_maintenance_task():
    data = request.json
    booking_id = data.get("booking_id")
    technician_id = data.get("technician_id")

    if not booking_id or not technician_id:
        return jsonify({"error": "Thiếu booking_id hoặc technician_id"}), 400
    
    try:
        booking_id = int(booking_id)
        technician_id = int(technician_id)
    except ValueError:
        return jsonify({"error": "booking_id và technician_id phải là số nguyên"}), 400
    
    task, error = service.create_task_from_booking(booking_id, technician_id)
    
    if error:
        status_code = 409 if "tồn tại" in error else 400
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": "Công việc bảo trì được tạo thành công!",
        "task": task.to_dict()
    }), 201

# 2. ADMIN: GET ALL TASKS (GET /api/maintenance/tasks)
@maintenance_bp.route("/tasks", methods=["GET"])
@admin_required()
def get_all_tasks_route():
    task_id_arg = request.args.get("id")
    if task_id_arg is not None:
        try:
            task_id = int(task_id_arg)
        except ValueError:
            return jsonify({"error": "Mã công việc phải là số nguyên"}), 400
        
        task = service.get_task_by_id(task_id)
        if not task:
            return jsonify({"error": "Không tìm thấy Công việc."}), 404
            
        return jsonify(task.to_dict()), 200

    tasks = service.get_all_tasks()
    return jsonify([t.to_dict() for t in tasks]), 200

# 3. USER: GET MY TASKS (GET /api/maintenance/my-tasks)
@maintenance_bp.route("/my-tasks", methods=["GET"])
@jwt_required()
def get_my_tasks_route():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")
    
    if role == "technician":
        # Yêu cầu service.get_tasks_by_technician(user_id) phải có trong service
        tasks = service.get_tasks_by_technician(user_id) 
    else:
        # Giả định user_id trong token là customer_id nếu không phải technician
        tasks = service.get_tasks_by_user(user_id)
        
    return jsonify([t.to_dict() for t in tasks]), 200

# 4. GET TASK BY ID (Admin hoặc User sở hữu)
@maintenance_bp.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task_details_route(task_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    task, is_authorized, _, _ = _check_task_permission(task_id, current_user_id, claims)
    
    if not task:
        return jsonify({"error": "Không tìm thấy Công việc."}), 404

    if not is_authorized:
        return jsonify(error="Unauthorized access to task"), 403

    return jsonify(task.to_dict()), 200

# 5. ADMIN/TECHNICIAN: UPDATE STATUS (PUT /api/maintenance/tasks/<id>/status)
@maintenance_bp.route("/tasks/<int:task_id>/status", methods=["PUT"])
@jwt_required()
def update_task_status_route(task_id):
    data = request.json
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "Missing 'status' field."}), 400

    current_user_id = get_jwt_identity()
    claims = get_jwt()

    task, is_authorized, is_admin, is_technician_owner = _check_task_permission(task_id, current_user_id, claims)
    
    if not task:
        return jsonify({"error": "Không tìm thấy công việc."}), 404

    # Cho phép Admin, Customer Owner, hoặc Technician Owner update status
    if not is_authorized:
        return jsonify({"error": "Bạn không có quyền cập nhật công việc này."}), 403

    task, error = service.update_task_status(task_id, new_status)
    if error:
        status_code = 404 if "Không tìm thấy" in error else 400
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": f"Cập nhật trạng thái công việc thành '{new_status}' thành công.",
        "task": task.to_dict()
    }), 200


# ============= Task Parts Endpoints =============

@maintenance_bp.route("/tasks/<int:task_id>/parts", methods=["POST"])
@jwt_required()
def add_part_to_task_route(task_id):
    """KTV thêm phụ tùng đã sử dụng vào task"""
    data = request.get_json()
    item_id = data.get("item_id")
    quantity = data.get("quantity", 1)

    if not item_id:
        return jsonify({"error": "item_id là bắt buộc"}), 400

    # Kiểm tra quyền: phải là Admin hoặc KTV được giao việc
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    task, is_authorized, is_admin, is_technician_owner = _check_task_permission(
        task_id, current_user_id, claims, required_roles=["technician_or_admin"]
    )

    if not task:
        return jsonify({"error": "Task không tồn tại"}), 404

    if not is_authorized:
        return jsonify({"error": "Bạn không có quyền thêm phụ tùng vào task này"}), 403

    part, error = service.add_part_to_task(task_id, item_id, quantity)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "Thêm phụ tùng thành công",
        "part": part.to_dict()
    }), 201


@maintenance_bp.route("/tasks/<int:task_id>/parts", methods=["GET"])
@jwt_required()
def get_task_parts_route(task_id):
    """Lấy danh sách phụ tùng của task"""
    # Không cần kiểm tra quyền quá nghiêm ngặt, chỉ cần đăng nhập. 
    # Nếu muốn strict hơn, nên dùng _check_task_permission như get_task_details_route
    parts = service.get_task_parts(task_id)
    return jsonify([p.to_dict() for p in parts]), 200


@maintenance_bp.route("/parts/<int:part_id>", methods=["DELETE"])
@jwt_required()
def remove_part_route(part_id):
    """Xóa phụ tùng khỏi task. Chỉ Admin hoặc KTV owner của task liên quan được phép."""
    # Logic kiểm tra quyền này nên nằm trong Service vì ta chỉ có part_id. 
    # Service cần query ngược lại task_id.
    
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("role") == "admin"

    success, error = service.remove_part_from_task(part_id, current_user_id, is_admin)
    if error:
        status_code = 403 if "quyền" in error else 404
        return jsonify({"error": error}), status_code

    return jsonify({"message": "Xóa phụ tùng thành công"}), 200


@maintenance_bp.route("/completed-tasks-with-parts", methods=["GET"])
@admin_required()
def get_completed_tasks_with_parts_route():
    """Admin lấy danh sách task completed với phụ tùng"""
    tasks = service.get_completed_tasks_with_parts()
    return jsonify(tasks), 200


@maintenance_bp.route("/bookings/<int:booking_id>/parts", methods=["GET"])
def get_booking_parts_route(booking_id):
    """Internal endpoint: Lấy danh sách phụ tùng theo booking_id (cho Finance Service)"""
    # Kiểm tra internal token
    internal_token = request.headers.get("X-Internal-Token")
    expected_token = current_app.config.get("INTERNAL_SERVICE_TOKEN")

    if not internal_token or internal_token != expected_token:
        return jsonify({"error": "Unauthorized"}), 401

    parts, error = service.get_task_parts_by_booking_id(booking_id)
    if error:
        return jsonify({"error": error}), 404

    return jsonify(parts), 200

# ============= Checklist Endpoints =============

@maintenance_bp.route("/tasks/<int:task_id>/checklist", methods=["POST"])
@jwt_required()
def add_checklist_item_route(task_id):
    """Thêm hạng mục kiểm tra vào checklist. Chỉ Admin hoặc KTV owner được phép."""
    data = request.get_json()
    item_name = data.get("item_name")
    status = data.get("status", "pending")
    note = data.get("note")

    if not item_name:
        return jsonify({"error": "item_name là bắt buộc"}), 400

    # Kiểm tra quyền: phải là Admin hoặc KTV được giao việc
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    # Dùng helper để check task và quyền
    task, is_authorized, is_admin, is_technician_owner = _check_task_permission(
        task_id, current_user_id, claims, required_roles=["technician_or_admin"]
    )

    if not task:
        return jsonify({"error": "Task không tồn tại"}), 404

    if not is_authorized:
        return jsonify({"error": "Bạn không có quyền thực hiện hành động này"}), 403

    item, error = service.add_checklist_item(task_id, item_name, status, note)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": "Thêm hạng mục kiểm tra thành công",
        "checklist_item": item.to_dict()
    }), 201

@maintenance_bp.route("/tasks/<int:task_id>/checklist", methods=["GET"])
@jwt_required()
def get_task_checklist_route(task_id):
    """Lấy checklist của task. Chỉ cần đăng nhập."""
    # Tương tự như get_task_parts, không cần kiểm tra quyền quá nghiêm ngặt
    checklist = service.get_task_checklist(task_id)
    return jsonify([item.to_dict() for item in checklist]), 200

@maintenance_bp.route("/checklist/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_checklist_item_route(item_id):
    """Cập nhật hạng mục kiểm tra. Chỉ Admin hoặc KTV owner của task liên quan được phép."""
    data = request.get_json()
    status = data.get("status")
    note = data.get("note")

    # Kiểm tra quyền: Logic này nên nằm trong Service vì ta chỉ có item_id.
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("role") == "admin"
    
    item, error = service.update_checklist_item(item_id, status, note, current_user_id, is_admin)
    
    if error:
        status_code = 403 if "quyền" in error else 404
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": "Cập nhật hạng mục kiểm tra thành công",
        "checklist_item": item.to_dict()
    }), 200

@maintenance_bp.route("/checklist/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_checklist_item_route(item_id):
    """Xóa hạng mục kiểm tra. Chỉ Admin hoặc KTV owner của task liên quan được phép."""
    # Logic kiểm tra quyền này nên nằm trong Service vì ta chỉ có item_id.
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    is_admin = claims.get("role") == "admin"
    
    success, error = service.remove_checklist_item(item_id, current_user_id, is_admin)
    
    if error:
        status_code = 403 if "quyền" in error else 404
        return jsonify({"error": error}), status_code

    return jsonify({"message": "Xóa hạng mục kiểm tra thành công"}), 200