from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.inventory_service import InventoryService as service

inventory_bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")


# ✅ 1. CREATE ITEM
@inventory_bp.route("/items", methods=["POST"])
@jwt_required()
def create_item():
    data = request.get_json()
    required_fields = ["name", "part_number", "price"]

    if not data or not all(k in data for k in required_fields):
        return jsonify({
            "error": f"Missing required fields: {', '.join(required_fields)}"
        }), 400

    item, error = service.create_item(data)

    if error:
        return jsonify({"error": error}), 409

    return jsonify({
        "message": "Item created successfully",
        "item": item.to_dict()
    }), 201


# ✅ 2. GET ALL ITEMS
@inventory_bp.route("/items", methods=["GET"])
@jwt_required()
def get_all_items():
    center_id = request.args.get("center_id", type=int)

    items = service.get_all_items(center_id=center_id)
    return jsonify([item.to_dict() for item in items]), 200


# ✅ 3. GET LOW STOCK ITEMS
@inventory_bp.route("/low-stock", methods=["GET"])
@jwt_required()
def get_low_stock():
    center_id = request.args.get("center_id", type=int)

    if center_id is not None and center_id <= 0:
        return jsonify({
            "error": "center_id phải lớn hơn 0"
        }), 400

    items = service.get_low_stock_items(center_id=center_id)

    return jsonify(
        [item.to_dict() for item in items]
    ), 200

# ✅ 4. GET ITEM BY ID
@inventory_bp.route("/items/<int:item_id>", methods=["GET"])
@jwt_required()
def get_item(item_id):
    item = service.get_item_by_id(item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(item.to_dict()), 200


# ✅ 5. UPDATE ITEM
@inventory_bp.route("/items/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_item(item_id):
    data = request.get_json()

    item, error = service.update_item(item_id, data)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({
        "message": "Item updated successfully",
        "item": item.to_dict()
    }), 200


# ✅ 6. DELETE ITEM
@inventory_bp.route("/items/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_item_route(item_id):
    success, message = service.delete_item(item_id)

    if not success:
        return jsonify({"error": message}), 404

    return jsonify({"message": message}), 200


# ✅ 7. AI SUGGEST REPLACEMENT PARTS
@inventory_bp.route("/suggest-parts", methods=["POST"])
@jwt_required()
def suggest_replacement_parts():
    data = request.get_json()
    vehicle_model = data.get("vehicle_model") if data else None
    category = data.get("category") if data else None

    if not vehicle_model:
        return jsonify({"error": "vehicle_model is required"}), 400

    suggestions = service.suggest_parts(vehicle_model, category)
    return jsonify([item.to_dict() for item in suggestions]), 200


# ✅ 8. SEED DEMO DATA
@inventory_bp.route("/seed-ai-data", methods=["POST"])
@jwt_required()
def seed_ai_data():
    service.seed_demo_data()
    return jsonify({"message": "Đã nạp dữ liệu mẫu AI thành công!"}), 201