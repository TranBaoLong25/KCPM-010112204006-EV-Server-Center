@assignment_bp.route("/", methods=["POST"])
@jwt_required()
def create_assignment():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "Body không được rỗng"}), 400

        required = ["staff_id", "maintenance_task_id"]
        if not all(field in data for field in required):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        try:
            staff_id = int(data["staff_id"])
            maintenance_task_id = int(data["maintenance_task_id"])
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "error": "staff_id và maintenance_task_id phải là số nguyên"
            }), 400

        if staff_id <= 0:
            return jsonify({"success": False, "error": "staff_id phải lớn hơn 0"}), 400

        if maintenance_task_id <= 0:
            return jsonify({"success": False, "error": "maintenance_task_id phải lớn hơn 0"}), 400

        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({"success": False, "error": "Staff not found"}), 404

        if staff.status not in ["active"]:
            return jsonify({"success": False, "error": "Staff is not available"}), 400

        existing = StaffAssignment.query.filter_by(
            maintenance_task_id=maintenance_task_id,
            status="assigned"
        ).first()

        if existing:
            return jsonify({"success": False, "error": "Task already assigned"}), 400

        assignment = StaffAssignment(
            staff_id=staff_id,
            maintenance_task_id=maintenance_task_id,
            assigned_by=current_user_id,
            priority=data.get("priority", "medium"),
            estimated_duration_minutes=data.get("estimated_duration_minutes"),
            notes=data.get("notes"),
            status="assigned"
        )

        db.session.add(assignment)

        staff.status = "busy"

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Assignment created successfully",
            "assignment": assignment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500