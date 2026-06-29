import json

from services.notification_service import NotificationService
from models.notification_model import Notification


def test_create_notification_valid(app):
    data = {
        "user_id": 1,
        "title": "Xác nhận đặt lịch",
        "message": "Xe điện của bạn đã được lên lịch thành công.",
        "notification_type": "booking_status",
        "channel": "email",
        "priority": "medium"
    }

    notification, error = NotificationService.create_notification(data)

    assert error is None
    assert notification is not None
    assert notification.user_id == 1
    assert notification.title == "Xác nhận đặt lịch"
    assert notification.status == "sent"
    assert Notification.query.count() == 1


def test_create_notification_missing_user_id(app):
    data = {
        "title": "Thông báo",
        "message": "Nội dung thông báo.",
        "notification_type": "system",
        "channel": "in_app",
        "priority": "low"
    }

    notification, error = NotificationService.create_notification(data)

    assert notification is None
    assert error is not None
    assert "Missing required fields" in error


def test_create_notification_invalid_scheduled_at(app):
    data = {
        "user_id": 1,
        "title": "Nhắc lịch bảo dưỡng",
        "message": "Vui lòng mang xe đến trung tâm vào ngày hẹn.",
        "notification_type": "reminder",
        "channel": "email",
        "priority": "high",
        "scheduled_at": "2026/07/01 09:00"
    }

    notification, error = NotificationService.create_notification(data)

    assert notification is None
    assert error is not None
    assert "Error creating notification" in error


def test_internal_create_notification_endpoint_success(client):
    payload = {
        "user_id": 2,
        "title": "OTP bảo mật",
        "message": "Mã OTP của bạn là 123456.",
        "notification_type": "system",
        "channel": "email",
        "priority": "medium"
    }

    response = client.post(
        "/internal/notifications/create",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-Internal-Token": "test-internal-token"}
    )

    body = response.get_json()

    assert response.status_code == 201
    assert body["message"] == "Notification created successfully"
    assert body["notification"]["user_id"] == 2


def test_internal_create_notification_endpoint_unauthorized(client):
    payload = {
        "user_id": 2,
        "title": "OTP bảo mật",
        "message": "Mã OTP của bạn là 123456.",
        "notification_type": "system",
        "channel": "email",
        "priority": "medium"
    }

    response = client.post(
        "/internal/notifications/create",
        data=json.dumps(payload),
        content_type="application/json"
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized internal request"


def test_create_notification_title_too_long(app):
    data = {
        "user_id": 1,
        "title": "A" * 256,
        "message": "Nội dung thông báo quá dài.",
        "notification_type": "system",
        "channel": "email",
        "priority": "medium"
    }

    notification, error = NotificationService.create_notification(data)

    assert notification is None
    assert error is not None
    assert "Error creating notification" in error


def test_create_notification_invalid_notification_type(app):
    data = {
        "user_id": 1,
        "title": "Thông báo không hợp lệ",
        "message": "Loại thông báo không tồn tại.",
        "notification_type": "invalid_type",
        "channel": "email",
        "priority": "medium"
    }

    notification, error = NotificationService.create_notification(data)

    assert notification is None
    assert error is not None
    assert "Error creating notification" in error


def test_create_notification_invalid_channel(app):
    data = {
        "user_id": 1,
        "title": "Thông báo kênh sai",
        "message": "Kênh thông báo không hợp lệ.",
        "notification_type": "system",
        "channel": "fax",
        "priority": "medium"
    }

    notification, error = NotificationService.create_notification(data)

    assert notification is None
    assert error is not None
    assert "Error creating notification" in error


def test_create_notification_scheduled_at_valid(app):
    data = {
        "user_id": 3,
        "title": "Lịch gửi thông báo",
        "message": "Thông báo sẽ được gửi theo lịch.",
        "notification_type": "reminder",
        "channel": "email",
        "priority": "high",
        "scheduled_at": "2026-07-01T09:00:00"
    }

    notification, error = NotificationService.create_notification(data)

    assert error is None
    assert notification is not None
    assert notification.status == "pending"
    assert notification.scheduled_at is not None
