import json
from datetime import datetime

import pytest
from services.notification_service import NotificationService
from models.notification_model import Notification


def build_payload(**overrides):
    payload = {
        "user_id": 1,
        "title": "Xác nhận đặt lịch",
        "message": "Xe điện của bạn đã được lên lịch thành công.",
        "notification_type": "booking_status",
        "channel": "email",
        "priority": "medium"
    }
    payload.update(overrides)
    return payload


@pytest.mark.blackbox
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


@pytest.mark.blackbox
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


@pytest.mark.blackbox
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


@pytest.mark.blackbox
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


@pytest.mark.blackbox
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


@pytest.mark.whitebox
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


@pytest.mark.whitebox
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


@pytest.mark.whitebox
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


@pytest.mark.whitebox
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


@pytest.mark.blackbox
def test_create_notification_with_metadata_and_related_entity(app):
    data = build_payload(
        metadata={"booking_id": 101, "source": "booking"},
        related_entity_type="booking",
        related_entity_id=101,
    )

    notification, error = NotificationService.create_notification(data)

    assert error is None
    assert notification is not None
    assert notification.extra_data is not None
    assert "booking_id" in notification.extra_data
    assert notification.related_entity_type == "booking"
    assert notification.related_entity_id == 101


@pytest.mark.blackbox
def test_create_notification_uses_defaults_for_optional_fields(app):
    data = build_payload(
        notification_type=None,
        channel=None,
        priority=None,
    )

    notification, error = NotificationService.create_notification(data)

    assert error is None
    assert notification is not None
    assert notification.notification_type == "system"
    assert notification.channel == "in_app"
    assert notification.priority == "medium"


@pytest.mark.whitebox
@pytest.mark.parametrize(
    "title,message",
    [
        ("   ", "hello"),
        ("hello", "   "),
        ("   ", "   "),
    ],
)
def test_create_notification_rejects_blank_or_whitespace_title_and_message(app, title, message):
    data = build_payload(title=title, message=message)

    notification, error = NotificationService.create_notification(data)

    assert notification is None
    assert error is not None
    assert "Error creating notification" in error


@pytest.mark.whitebox
def test_create_notification_rejects_invalid_priority(app):
    data = build_payload(priority="critical")

    notification, error = NotificationService.create_notification(data)

    assert notification is None
    assert error is not None
    assert "invalid priority" in error.lower()


@pytest.mark.blackbox
def test_get_user_notifications_returns_latest_first_and_filters_unread(app):
    first = build_payload(user_id=7, title="First", message="First message")
    second = build_payload(user_id=7, title="Second", message="Second message")
    third = build_payload(user_id=7, title="Third", message="Third message")

    first_notification, _ = NotificationService.create_notification(first)
    second_notification, _ = NotificationService.create_notification(second)
    third_notification, _ = NotificationService.create_notification(third)

    notification, error = NotificationService.mark_as_read(first_notification.id, 7)
    assert error is None
    assert notification.status == "read"

    unread_notifications = NotificationService.get_user_notifications(7, unread_only=True)
    assert [n.id for n in unread_notifications] == [second_notification.id, third_notification.id]

    all_notifications = NotificationService.get_user_notifications(7)
    assert all_notifications[0].id == third_notification.id
    assert all_notifications[1].id == second_notification.id
    assert all_notifications[2].id == first_notification.id


@pytest.mark.blackbox
def test_mark_as_read_returns_not_found_for_other_user(app):
    notification, _ = NotificationService.create_notification(build_payload(user_id=20))

    result, error = NotificationService.mark_as_read(notification.id, 99)

    assert result is None
    assert error == "Notification not found"


@pytest.mark.blackbox
def test_mark_all_as_read_updates_all_unread_notifications(app):
    for idx in range(3):
        NotificationService.create_notification(build_payload(user_id=8, title=f"Notif {idx}", message=f"Message {idx}"))

    success, message = NotificationService.mark_all_as_read(8)
    notifications = NotificationService.get_user_notifications(8)

    assert success is True
    assert message == "All notifications marked as read"
    assert all(n.status == "read" for n in notifications)
    assert all(n.read_at is not None for n in notifications)


@pytest.mark.blackbox
def test_delete_notification_removes_owned_notification(app):
    notification, _ = NotificationService.create_notification(build_payload(user_id=9))

    success, message = NotificationService.delete_notification(notification.id, 9)
    deleted = Notification.query.get(notification.id)

    assert success is True
    assert message == "Notification deleted successfully"
    assert deleted is None


@pytest.mark.blackbox
def test_delete_notification_fails_for_other_user(app):
    notification, _ = NotificationService.create_notification(build_payload(user_id=10))

    success, message = NotificationService.delete_notification(notification.id, 11)

    assert success is False
    assert message == "Notification not found"


@pytest.mark.blackbox
def test_get_notification_stats_counts_read_and_unread(app):
    NotificationService.create_notification(build_payload(user_id=11, title="A", message="A"))
    second, _ = NotificationService.create_notification(build_payload(user_id=11, title="B", message="B"))
    third, _ = NotificationService.create_notification(build_payload(user_id=11, title="C", message="C"))

    NotificationService.mark_as_read(second.id, 11)

    stats = NotificationService.get_notification_stats(11)

    assert stats["total"] == 3
    assert stats["unread"] == 2
    assert stats["read"] == 1


@pytest.mark.blackbox
def test_internal_create_notification_rejects_missing_required_fields(client):
    response = client.post(
        "/internal/notifications/create",
        data=json.dumps({"title": "No user id"}),
        content_type="application/json",
        headers={"X-Internal-Token": "test-internal-token"},
    )

    assert response.status_code == 400
    assert "Missing required fields" in response.get_json()["error"]


@pytest.mark.blackbox
def test_internal_create_notification_rejects_invalid_token(client):
    response = client.post(
        "/internal/notifications/create",
        data=json.dumps(build_payload()),
        content_type="application/json",
        headers={"X-Internal-Token": "wrong-token"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized internal request"
