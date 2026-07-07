from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from functools import wraps
from services.payment_service import PaymentService as service

# --- Decorators (Copying Admin Required from other services) ---
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                if claims.get("role") == "admin":
                    return fn(*args, **kwargs)
                else:
                    return jsonify(error="Admins only!"), 403
            except Exception:
                return jsonify(error="Token invalid or missing."), 401
        return decorator
    return wrapper
# --- End Decorators ---

def internal_token_required(fn):
    """Chỉ cho phép service nội bộ (Finance) gọi qua X-Internal-Token."""
    @wraps(fn)
    def decorator(*args, **kwargs):
        token = request.headers.get("X-Internal-Token")
        expected = current_app.config.get("INTERNAL_SERVICE_TOKEN")
        if not expected:
            return jsonify({"error": "Internal service token is not configured."}), 503
        if not token or token != expected:
            return jsonify({"error": "Unauthorized internal request"}), 401
        return fn(*args, **kwargs)
    return decorator

# Định nghĩa Blueprint
payment_bp = Blueprint("payment", __name__, url_prefix="/api/payments")

# 1. POST /api/payments/create (Tạo giao dịch thanh toán - Chỉ Finance Service)
@payment_bp.route("/create", methods=["POST"])
@internal_token_required
def create_payment_request_route():
    # Lấy data (invoice_id, method, user_id, amount)
    data = request.json
    invoice_id = data.get("invoice_id")
    method = data.get("method")
    user_id = data.get("user_id")
    amount = data.get("amount") # ✅ Đã thêm: Lấy amount từ Finance Service

    # ✅ Đã sửa: Thêm kiểm tra amount
    if not invoice_id or not method or not user_id or amount is None:
        return jsonify({"error": "Missing required fields (invoice_id, method, user_id, amount)"}), 400

    # Gọi logic nghiệp vụ
    # ✅ Đã sửa: Truyền amount vào hàm service
    transaction_data, error = service.create_payment_request(invoice_id, method, user_id, amount)
    
    if error:
        return jsonify({"error": error}), 400

    return jsonify(transaction_data), 201

# 2. POST /api/payments/webhook (Mock PG Webhook - Dùng để mô phỏng thành công)
@payment_bp.route("/webhook", methods=["POST"])
@internal_token_required
def handle_pg_webhook_route():
    data = request.json
    pg_transaction_id = data.get("pg_transaction_id")
    status = data.get("status")
    
    if not pg_transaction_id or not status:
        return jsonify({"error": "Missing required fields (pg_transaction_id, status)"}), 400
        
    try:
        transaction, error = service.handle_pg_webhook(pg_transaction_id, status)
    except Exception as e:
        current_app.logger.exception("Webhook handler error")
        return jsonify({"error": f"Lỗi xử lý webhook: {str(e)}"}), 500

    if error:
        # Idempotent: đã success trước đó vẫn trả 200
        if transaction and "đã được xử lý thành công" in error:
            return jsonify({"message": error, "transaction": transaction.to_dict()}), 200
        return jsonify({"error": error}), 400

    return jsonify({"message": "Webhook processed successfully"}), 200

# 3. GET /api/payments/history/my (Lịch sử của User)
@payment_bp.route("/history/my", methods=["GET"])
@jwt_required()
def get_my_payment_history_route():
    user_id = get_jwt_identity()
    history = service.get_history_by_user(user_id)
    return jsonify([t.to_dict() for t in history]), 200

# 4. GET /api/payments/history/all (Lịch sử của Admin)
@payment_bp.route("/history/all", methods=["GET"])
@jwt_required()
@admin_required()
def get_all_payment_history_route():
    history = service.get_all_history()
    return jsonify([t.to_dict() for t in history]), 200