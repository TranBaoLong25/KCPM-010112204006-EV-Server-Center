import pytest
from unittest.mock import patch
from services.maintenance_service import MaintenanceService
from app import db
from models.maintenance_model import (
    MaintenanceTask,
    TaskPart,
    MaintenanceChecklist
)


# ==========================================================
# TC01 - Update Task Status thành công
# ==========================================================
def test_update_task_status_success(app_context):
    task = MaintenanceTask(
        booking_id=1,
        user_id=100,
        vehicle_vin="VIN001",
        description="Oil Change",
        technician_id=200,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    updated_task, error = MaintenanceService.update_task_status(
        task.task_id, "completed"
    )
    assert error is None
    assert updated_task.status == "completed"


# ==========================================================
# TC02 - Task không tồn tại
# White-box: đi vào nhánh if not task
# ==========================================================
def test_update_task_status_task_not_found(app_context):
    updated_task, error = MaintenanceService.update_task_status(
        999999, "completed"
    )
    assert updated_task is None
    assert error == "Không tìm thấy Công việc bảo trì."


# ==========================================================
# TC03 - Status không hợp lệ
# White-box: đi vào nhánh if new_status not in valid_statuses
# ==========================================================
def test_update_task_status_invalid_status(app_context):
    task = MaintenanceTask(
        booking_id=2,
        user_id=101,
        vehicle_vin="VIN002",
        description="Brake Check",
        technician_id=201,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    updated_task, error = MaintenanceService.update_task_status(
        task.task_id, "abc"
    )
    assert updated_task is None
    assert "không hợp lệ" in error


# ==========================================================
# TC04 - Database Commit Exception
# White-box: đi vào nhánh except
# ==========================================================
def test_update_task_status_commit_exception(app_context):
    task = MaintenanceTask(
        booking_id=3,
        user_id=102,
        vehicle_vin="VIN003",
        description="Battery Check",
        technician_id=202,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    with patch("app.db.session.commit") as mock_commit:
        mock_commit.side_effect = Exception("Database Error")
        updated_task, error = MaintenanceService.update_task_status(
            task.task_id, "completed"
        )
        assert updated_task is None
        assert "Lỗi khi cập nhật trạng thái" in error


# ==========================================================
# CREATE TASK FROM BOOKING
# ==========================================================
def test_create_task_success(app_context):
    mock_booking = {
        "user_id": 100,
        "service_type": "Maintenance"
    }
    mock_user = {
        "username": "test_user"
    }
    with patch(
        "services.maintenance_service.MaintenanceService._get_booking_details"
    ) as mock_booking_api, patch(
        "services.maintenance_service.MaintenanceService._get_user_profile"
    ) as mock_user_api:
        mock_booking_api.return_value = (mock_booking, None)
        mock_user_api.return_value = (mock_user, None)
        task, error = MaintenanceService.create_task_from_booking(
            booking_id=1,
            technician_id=200
        )
        assert error is None
        assert task is not None
        assert task.booking_id == 1
        assert task.user_id == 100
        assert task.status == "pending"


def test_create_task_duplicate(app_context):
    task = MaintenanceTask(
        booking_id=1,
        user_id=100,
        vehicle_vin="VIN001",
        description="Maintenance",
        technician_id=200,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    result, error = MaintenanceService.create_task_from_booking(
        booking_id=1,
        technician_id=200
    )
    assert result is None
    assert "đã được phân công" in error


def test_create_task_booking_error(app_context):
    with patch(
        "services.maintenance_service.MaintenanceService._get_booking_details"
    ) as mock_booking:
        mock_booking.return_value = (None, "Booking Error")
        task, error = MaintenanceService.create_task_from_booking(
            booking_id=1,
            technician_id=200
        )
        assert task is None
        assert "Lỗi khi lấy Booking" in error


def test_create_task_db_exception(app_context):
    mock_booking = {
        "user_id": 100,
        "service_type": "Maintenance"
    }
    mock_user = {
        "username": "tester"
    }
    with patch(
        "services.maintenance_service.MaintenanceService._get_booking_details"
    ) as mock_booking_api, patch(
        "services.maintenance_service.MaintenanceService._get_user_profile"
    ) as mock_user_api, patch(
        "app.db.session.commit"
    ) as mock_commit:
        mock_booking_api.return_value = (mock_booking, None)
        mock_user_api.return_value = (mock_user, None)
        mock_commit.side_effect = Exception("Database Error")
        task, error = MaintenanceService.create_task_from_booking(
            booking_id=1,
            technician_id=200
        )
        assert task is None
        assert "Lỗi khi tạo công việc bảo trì" in error


# ==========================================================
# ADD PART TO TASK
# ==========================================================
def test_add_part_task_not_found(app_context):
    """TC09 - Task không tồn tại"""
    part, error = MaintenanceService.add_part_to_task(
        task_id=9999,
        item_id=1,
        quantity=1
    )
    assert part is None
    assert error == "Task không tồn tại"


def test_add_part_inventory_error(app_context):
    """TC10 - Inventory Service trả lỗi"""
    task = MaintenanceTask(
        booking_id=10,
        user_id=100,
        vehicle_vin="VIN010",
        description="Maintenance",
        technician_id=200,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    with patch(
        "services.maintenance_service.MaintenanceService._check_inventory_stock"
    ) as mock_inventory:
        mock_inventory.return_value = (None, "Inventory Error")
        part, error = MaintenanceService.add_part_to_task(
            task.task_id, item_id=1, quantity=2
        )
        assert part is None
        assert error == "Lỗi kiểm tra kho: Inventory Error"


def test_add_part_not_found_in_inventory(app_context):
    """TC11 - Không tìm thấy phụ tùng"""
    task = MaintenanceTask(
        booking_id=11,
        user_id=101,
        vehicle_vin="VIN011",
        description="Maintenance",
        technician_id=201,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    with patch(
        "services.maintenance_service.MaintenanceService._check_inventory_stock"
    ) as mock_inventory:
        mock_inventory.return_value = (None, None)
        part, error = MaintenanceService.add_part_to_task(
            task.task_id, item_id=99, quantity=1
        )
        assert part is None
        assert error == "Phụ tùng không tồn tại trong kho"


def test_add_part_out_of_stock(app_context):
    """TC12 - Vượt quá tồn kho"""
    task = MaintenanceTask(
        booking_id=12,
        user_id=102,
        vehicle_vin="VIN012",
        description="Maintenance",
        technician_id=202,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    with patch(
        "services.maintenance_service.MaintenanceService._check_inventory_stock"
    ) as mock_inventory:
        mock_inventory.return_value = ({"quantity": 5}, None)
        part, error = MaintenanceService.add_part_to_task(
            task.task_id, item_id=2, quantity=10
        )
        assert part is None
        assert "Số lượng vượt quá tồn kho" in error


def test_add_part_success(app_context):
    """TC13 - Thêm phụ tùng mới thành công"""
    task = MaintenanceTask(
        booking_id=13,
        user_id=103,
        vehicle_vin="VIN013",
        description="Maintenance",
        technician_id=203,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    with patch(
        "services.maintenance_service.MaintenanceService._check_inventory_stock"
    ) as mock_inventory:
        mock_inventory.return_value = ({"quantity": 100}, None)
        part, error = MaintenanceService.add_part_to_task(
            task.task_id, item_id=5, quantity=3
        )
        assert error is None
        assert part is not None
        assert part.task_id == task.task_id
        assert part.item_id == 5
        assert part.quantity == 3


def test_add_existing_part_success(app_context):
    """TC14 - Cập nhật số lượng phụ tùng đã tồn tại"""
    task = MaintenanceTask(
        booking_id=14,
        user_id=104,
        vehicle_vin="VIN014",
        description="Maintenance",
        technician_id=204,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    existing_part = TaskPart(
        task_id=task.task_id,
        item_id=7,
        quantity=2
    )
    db.session.add(existing_part)
    db.session.commit()
    with patch(
        "services.maintenance_service.MaintenanceService._check_inventory_stock"
    ) as mock_inventory:
        mock_inventory.return_value = ({"quantity": 20}, None)
        part, error = MaintenanceService.add_part_to_task(
            task.task_id, item_id=7, quantity=3
        )
        assert error is None
        assert part is not None
        assert part.quantity == 5


# ==========================================================
# CHECKLIST
# ==========================================================
def test_add_checklist_item_success(app_context):
    """TC15 - Thêm checklist thành công"""
    task = MaintenanceTask(
        booking_id=20,
        user_id=200,
        vehicle_vin="VIN020",
        description="Maintenance",
        technician_id=300,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    item, error = MaintenanceService.add_checklist_item(
        task.task_id, "Brake", "pending", "Initial check"
    )
    assert error is None
    assert item is not None
    assert item.task_id == task.task_id
    assert item.item_name == "Brake"
    assert item.status == "pending"


def test_add_checklist_item_task_not_found(app_context):
    """TC16 - Task không tồn tại"""
    item, error = MaintenanceService.add_checklist_item(
        99999, "Brake", "pending"
    )
    assert item is None
    assert error == "Task không tồn tại"


def test_update_checklist_success(app_context):
    """TC17 - Cập nhật checklist thành công"""
    task = MaintenanceTask(
        booking_id=21,
        user_id=201,
        vehicle_vin="VIN021",
        description="Maintenance",
        technician_id=301,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    item, _ = MaintenanceService.add_checklist_item(
        task.task_id, "Battery", "pending"
    )
    updated, error = MaintenanceService.update_checklist_item(
        item.id, status="completed", note="OK", current_user_id=301
    )
    assert error is None
    assert updated.status == "completed"
    assert updated.note == "OK"


def test_update_checklist_not_found(app_context):
    """TC18 - Checklist không tồn tại"""
    item, error = MaintenanceService.update_checklist_item(
        99999, status="completed"
    )
    assert item is None
    assert error == "Hạng mục kiểm tra không tồn tại"


def test_update_checklist_permission_denied(app_context):
    """TC19 - Technician không có quyền"""
    task = MaintenanceTask(
        booking_id=22,
        user_id=202,
        vehicle_vin="VIN022",
        description="Maintenance",
        technician_id=500,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    item, _ = MaintenanceService.add_checklist_item(
        task.task_id, "Engine", "pending"
    )
    updated, error = MaintenanceService.update_checklist_item(
        item.id, status="completed", current_user_id=999
    )
    assert updated is None
    assert error == "Bạn không có quyền cập nhật checklist này"


def test_remove_checklist_success(app_context):
    """TC20 - Xóa checklist thành công"""
    task = MaintenanceTask(
        booking_id=23,
        user_id=203,
        vehicle_vin="VIN023",
        description="Maintenance",
        technician_id=303,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    item, _ = MaintenanceService.add_checklist_item(
        task.task_id, "Cooling System", "pending"
    )
    result, error = MaintenanceService.remove_checklist_item(item.id)
    assert result is True
    assert error is None


def test_remove_checklist_not_found(app_context):
    """TC21 - Checklist không tồn tại"""
    result, error = MaintenanceService.remove_checklist_item(99999)
    assert result is None
    assert error == "Hạng mục kiểm tra không tồn tại"


# ==========================================================
# FAIL DEMO
# ==========================================================
def test_fail_update_task_status_db_error(app_context):
    """Demo nhánh except của update_task_status"""
    task = MaintenanceTask(
        booking_id=100,
        user_id=100,
        vehicle_vin="VINFAIL01",
        description="Demo",
        technician_id=1,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    with patch("app.db.session.commit") as mock_commit:
        mock_commit.side_effect = Exception("Database Error")
        updated, error = MaintenanceService.update_task_status(
            task.task_id, "completed"
        )
        assert updated is None
        assert "Lỗi khi cập nhật trạng thái" in error


def test_fail_create_task_booking_service(app_context):
    """Demo Booking Service lỗi"""
    with patch(
        "services.maintenance_service.MaintenanceService._get_booking_details"
    ) as booking_api:
        booking_api.return_value = (None, "Booking Error")
        task, error = MaintenanceService.create_task_from_booking(
            booking_id=999,
            technician_id=1
        )
        assert task is None
        assert error is not None


def test_fail_add_part_inventory_error(app_context):
    """Demo Inventory Service lỗi"""
    task = MaintenanceTask(
        booking_id=101,
        user_id=101,
        vehicle_vin="VINFAIL02",
        description="Demo",
        technician_id=2,
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    with patch(
        "services.maintenance_service.MaintenanceService._check_inventory_stock"
    ) as inventory_api:
        inventory_api.return_value = (None, "Inventory Error")
        part, error = MaintenanceService.add_part_to_task(
            task.task_id, item_id=1, quantity=5
        )
        assert part is None
        assert error is not None