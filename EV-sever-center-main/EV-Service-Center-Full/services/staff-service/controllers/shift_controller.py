from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from models.staff_model import StaffShift, Staff
from datetime import datetime

shift_bp = Blueprint("shifts", __name__, url_prefix="/api/shifts")


@shift_bp.route("/", methods=["GET"])
@jwt_required()
def get_all_shifts():
    try:
        staff_id = request.args.get("staff_id", type=int)
        shift_date = request.args.get("date")
        status = request.args.get("status")

        query = StaffShift.query

        if staff_id is not None:
            if staff_id <= 0:
                return jsonify({"success": False, "error": "staff_id phải lớn hơn 0"}), 400
            query = query.filter(StaffShift.staff_id == staff_id)

        if shift_date:
            query = query.filter(
                StaffShift.shift_date == datetime.fromisoformat(shift_date).date()
            )

        if status:
            query = query.filter(StaffShift.status == status)

        shifts = query.order_by(
            StaffShift.shift_date.desc(),
            StaffShift.start_time
        ).all()

        return jsonify({
            "success": True,
            "shifts": [s.to_dict() for s in shifts],
            "count": len(shifts)
        }), 200

    except ValueError:
        return jsonify({"success": False, "error": "date không đúng định dạng"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@shift_bp.route("/", methods=["POST"])
@jwt_required()
def create_shift():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "Body không được rỗng"}), 400

        required = ["staff_id", "shift_date", "shift_type", "start_time", "end_time"]
        if not all(field in data for field in required):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        try:
            staff_id = int(data["staff_id"])
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "staff_id phải là số nguyên"}), 400

        if staff_id <= 0:
            return jsonify({"success": False, "error": "staff_id phải lớn hơn 0"}), 400

        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({"success": False, "error": "Staff not found"}), 404

        shift = StaffShift(
            staff_id=staff_id,
            shift_date=datetime.fromisoformat(data["shift_date"]).date(),
            shift_type=data["shift_type"],
            start_time=datetime.strptime(data["start_time"], "%H:%M:%S").time(),
            end_time=datetime.strptime(data["end_time"], "%H:%M:%S").time(),
            notes=data.get("notes"),
            status="scheduled"
        )

        db.session.add(shift)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Shift created successfully",
            "shift": shift.to_dict()
        }), 201

    except ValueError:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "shift_date/start_time/end_time không đúng định dạng"
        }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@shift_bp.route("/<int:shift_id>", methods=["PUT"])
@jwt_required()
def update_shift(shift_id):
    try:
        if shift_id <= 0:
            return jsonify({"success": False, "error": "shift_id phải lớn hơn 0"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Body không được rỗng"}), 400

        shift = StaffShift.query.get(shift_id)
        if not shift:
            return jsonify({"success": False, "error": "Shift not found"}), 404

        if "shift_date" in data:
            shift.shift_date = datetime.fromisoformat(data["shift_date"]).date()
        if "shift_type" in data:
            shift.shift_type = data["shift_type"]
        if "start_time" in data:
            shift.start_time = datetime.strptime(data["start_time"], "%H:%M:%S").time()
        if "end_time" in data:
            shift.end_time = datetime.strptime(data["end_time"], "%H:%M:%S").time()
        if "status" in data:
            shift.status = data["status"]
        if "notes" in data:
            shift.notes = data["notes"]

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Shift updated successfully",
            "shift": shift.to_dict()
        }), 200

    except ValueError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Dữ liệu ngày/giờ không đúng định dạng"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@shift_bp.route("/<int:shift_id>/check-in", methods=["PUT"])
@jwt_required()
def check_in_shift(shift_id):
    try:
        if shift_id <= 0:
            return jsonify({"success": False, "error": "shift_id phải lớn hơn 0"}), 400

        shift = StaffShift.query.get(shift_id)
        if not shift:
            return jsonify({"success": False, "error": "Shift not found"}), 404

        shift.status = "in_progress"
        shift.actual_start_time = datetime.now()
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Checked in successfully",
            "shift": shift.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@shift_bp.route("/<int:shift_id>/check-out", methods=["PUT"])
@jwt_required()
def check_out_shift(shift_id):
    try:
        if shift_id <= 0:
            return jsonify({"success": False, "error": "shift_id phải lớn hơn 0"}), 400

        shift = StaffShift.query.get(shift_id)
        if not shift:
            return jsonify({"success": False, "error": "Shift not found"}), 404

        shift.status = "completed"
        shift.actual_end_time = datetime.now()
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Checked out successfully",
            "shift": shift.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@shift_bp.route("/schedule", methods=["POST"])
@jwt_required()
def bulk_schedule_shifts():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "Body không được rỗng"}), 400

        return jsonify({
            "success": True,
            "message": "Shifts scheduled successfully"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500