import builtins
from datetime import datetime
from unittest.mock import patch

import pytest

from services.booking_service import BookingService
from models.booking_model import Booking


@pytest.mark.whitebox
def test_create_booking_missing_required_fields(app):
    booking, error = BookingService.create_booking({
        "service_type": "Bảo dưỡng",
        "technician_id": 2,
        "station_id": 3,
        "start_time": "2026-07-01T08:00:00",
        "end_time": "2026-07-01T09:00:00"
    })

    assert booking is None
    assert error == "Thiếu thông tin đặt lịch bắt buộc."


@pytest.mark.whitebox
def test_create_booking_invalid_time_range(app):
    with app.app_context():
        booking, error = BookingService.create_booking({
            "user_id": 1,
            "service_type": "Bảo dưỡng",
            "technician_id": 2,
            "station_id": 3,
            "start_time": "2026-07-01T10:00:00",
            "end_time": "2026-07-01T09:00:00"
        })

    assert booking is None
    assert error is not None
    assert "Thời gian" in error or "Error" in error


@pytest.mark.whitebox
@patch("services.booking_service.BookingService._verify_user")
def test_create_booking_time_overlap(mock_verify_user, app):
    mock_verify_user.return_value = ({"username": "tester"}, None)

    with app.app_context():
        existing = Booking(
            user_id=1,
            customer_name="tester",
            service_type="Bảo dưỡng",
            technician_id=2,
            station_id=3,
            start_time=datetime.fromisoformat("2026-07-01T08:00:00"),
            end_time=datetime.fromisoformat("2026-07-01T09:00:00"),
            status="confirmed"
        )
        from app import db
        db.session.add(existing)
        db.session.commit()

    booking, error = BookingService.create_booking({
        "user_id": 1,
        "service_type": "Sửa chữa",
        "technician_id": 2,
        "station_id": 3,
        "start_time": "2026-07-01T08:30:00",
        "end_time": "2026-07-01T09:30:00"
    })

    assert booking is None
    assert error == "Thời gian này đã có lịch hẹn trùng."


@pytest.mark.whitebox
@patch("services.booking_service.BookingService._verify_user")
def test_create_booking_center_not_found(mock_verify_user, app):
    mock_verify_user.return_value = ({"username": "tester"}, None)

    booking, error = BookingService.create_booking({
        "user_id": 1,
        "service_type": "Sửa chữa",
        "technician_id": 2,
        "station_id": 3,
        "center_id": 9999,
        "start_time": "2026-07-01T08:00:00",
        "end_time": "2026-07-01T09:00:00"
    })

    assert booking is None
    assert error == "Trung tâm dịch vụ không tồn tại."


@pytest.mark.whitebox
@patch("services.booking_service.BookingService._verify_user")
@patch("services.booking_service.BookingService._notify_booking_created")
def test_create_booking_success_internal(mock_notify, mock_verify_user, app):
    mock_verify_user.return_value = ({"username": "tester"}, None)
    mock_notify.return_value = (True, "Notification skipped")

    booking, error = BookingService.create_booking({
        "user_id": 1,
        "service_type": "Sửa chữa",
        "technician_id": 2,
        "station_id": 3,
        "start_time": "2026-07-01T08:00:00",
        "end_time": "2026-07-01T09:00:00"
    })

    assert error is None
    assert booking is not None
    assert booking.status == "confirmed"
    assert booking.customer_name == "tester"


@pytest.mark.whitebox
def test_is_time_available_returns_false_when_overlap(app):
    with app.app_context():
        existing = Booking(
            user_id=1,
            customer_name="tester",
            service_type="Bảo dưỡng",
            technician_id=2,
            station_id=3,
            start_time=datetime.fromisoformat("2026-07-01T08:00:00"),
            end_time=datetime.fromisoformat("2026-07-01T09:00:00"),
            status="confirmed"
        )
        from app import db
        db.session.add(existing)
        db.session.commit()

        available = BookingService.is_time_available(
            technician_id=2,
            station_id=3,
            start_time="2026-07-01T08:30:00",
            end_time="2026-07-01T09:30:00"
        )

    assert available is False


@pytest.mark.whitebox
def test_is_time_available_returns_true_when_no_overlap(app):
    with app.app_context():
        existing = Booking(
            user_id=1,
            customer_name="tester",
            service_type="Bảo dưỡng",
            technician_id=2,
            station_id=3,
            start_time=datetime.fromisoformat("2026-07-01T08:00:00"),
            end_time=datetime.fromisoformat("2026-07-01T09:00:00"),
            status="confirmed"
        )
        from app import db
        db.session.add(existing)
        db.session.commit()

        available = BookingService.is_time_available(
            technician_id=2,
            station_id=3,
            start_time="2026-07-01T09:00:00",
            end_time="2026-07-01T10:00:00"
        )

    assert available is True


@pytest.mark.whitebox
@patch("services.booking_service.BookingService._verify_user")
def test_create_booking_invalid_time_format(mock_verify_user, app):
    mock_verify_user.return_value = ({"username": "tester"}, None)

    with app.app_context():
        booking, error = BookingService.create_booking({
            "user_id": 1,
            "service_type": "Sửa chữa",
            "technician_id": 2,
            "station_id": 3,
            "start_time": "not-a-date",
            "end_time": "2026-07-01T09:00:00"
        })

    assert booking is None
    assert error == "Định dạng thời gian không hợp lệ."


@pytest.mark.whitebox
@patch("services.booking_service.BookingService._verify_user")
def test_create_booking_rejects_zero_length_interval(mock_verify_user, app):
    mock_verify_user.return_value = ({"username": "tester"}, None)

    with app.app_context():
        booking, error = BookingService.create_booking({
            "user_id": 1,
            "service_type": "Sửa chữa",
            "technician_id": 2,
            "station_id": 3,
            "start_time": "2026-07-01T08:00:00",
            "end_time": "2026-07-01T08:00:00"
        })

    assert booking is None
    assert error == "Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc."


@pytest.mark.whitebox
@patch("services.booking_service.BookingService._verify_user")
def test_create_booking_accepts_one_minute_interval(mock_verify_user, app):
    mock_verify_user.return_value = ({"username": "tester"}, None)

    with app.app_context():
        booking, error = BookingService.create_booking({
            "user_id": 1,
            "service_type": "Sửa chữa",
            "technician_id": 2,
            "station_id": 3,
            "start_time": "2026-07-01T08:00:00",
            "end_time": "2026-07-01T08:01:00"
        })

    assert error is None
    assert booking is not None
    assert booking.end_time == datetime.fromisoformat("2026-07-01T08:01:00")


@pytest.mark.whitebox
@patch("services.booking_service.BookingService._verify_user")
def test_create_booking_rejects_blank_service_type(mock_verify_user, app):
    mock_verify_user.return_value = ({"username": "tester"}, None)

    with app.app_context():
        booking, error = BookingService.create_booking({
            "user_id": 1,
            "service_type": "   ",
            "technician_id": 2,
            "station_id": 3,
            "start_time": "2026-07-01T08:00:00",
            "end_time": "2026-07-01T09:00:00"
        })

    assert booking is None
    assert error == "Thiếu thông tin đặt lịch bắt buộc."


@pytest.mark.whitebox
def test_notify_booking_created_calls_helper_with_expected_payload(app):
    booking = Booking(
        user_id=1,
        customer_name="tester",
        service_type="Sửa chữa",
        technician_id=2,
        station_id=3,
        start_time=datetime.fromisoformat("2026-07-01T08:00:00"),
        end_time=datetime.fromisoformat("2026-07-01T09:00:00"),
        status="confirmed"
    )

    with patch("helpers.notification_helper.NotificationHelper.send_notification") as mock_send:
        mock_send.return_value = (True, "Notification sent")
        with app.app_context():
            result = BookingService._notify_booking_created(booking)

    assert result == (True, "Notification sent")
    mock_send.assert_called_once()
    args, kwargs = mock_send.call_args
    assert kwargs["title"] == "✅ Đặt lịch thành công!"
    assert kwargs["priority"] == "high"
    assert kwargs["related_entity_type"] == "booking"


@pytest.mark.whitebox
def test_notify_booking_created_returns_skipped_when_import_fails(app):
    booking = Booking(
        user_id=1,
        customer_name="tester",
        service_type="Sửa chữa",
        technician_id=2,
        station_id=3,
        start_time=datetime.fromisoformat("2026-07-01T08:00:00"),
        end_time=datetime.fromisoformat("2026-07-01T09:00:00"),
        status="confirmed"
    )

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "helpers.notification_helper":
            raise ImportError("boom")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        with app.app_context():
            result = BookingService._notify_booking_created(booking)

    assert result == (True, "Notification skipped")


@pytest.mark.whitebox
@patch("services.booking_service.BookingService._verify_user")
def test_update_booking_status_success(mock_verify_user, app):
    mock_verify_user.return_value = ({"username": "tester"}, None)

    with app.app_context():
        booking, _ = BookingService.create_booking({
            "user_id": 1,
            "service_type": "Sửa chữa",
            "technician_id": 2,
            "station_id": 3,
            "start_time": "2026-07-01T08:00:00",
            "end_time": "2026-07-01T09:00:00"
        })

        updated_booking, error = BookingService.update_booking_status(booking.id, "completed")

    assert error is None
    assert updated_booking is not None
    assert updated_booking.status == "completed"


@pytest.mark.whitebox
@patch("services.booking_service.BookingService._verify_user")
def test_delete_booking_success(mock_verify_user, app):
    mock_verify_user.return_value = ({"username": "tester"}, None)

    with app.app_context():
        booking, _ = BookingService.create_booking({
            "user_id": 1,
            "service_type": "Sửa chữa",
            "technician_id": 2,
            "station_id": 3,
            "start_time": "2026-07-01T08:00:00",
            "end_time": "2026-07-01T09:00:00"
        })

        deleted, message = BookingService.delete_booking(booking.id)
        remaining = BookingService.get_booking_by_id(booking.id)

    assert deleted is True
    assert message == "Xóa lịch đặt thành công."
    assert remaining is None


@pytest.mark.whitebox
@patch("services.booking_service.BookingService._verify_user")
def test_get_bookings_by_user_returns_descending_order(mock_verify_user, app):
    mock_verify_user.return_value = ({"username": "tester"}, None)

    with app.app_context():
        first, _ = BookingService.create_booking({
            "user_id": 1,
            "service_type": "Sửa chữa",
            "technician_id": 2,
            "station_id": 3,
            "start_time": "2026-07-01T08:00:00",
            "end_time": "2026-07-01T09:00:00"
        })
        second, _ = BookingService.create_booking({
            "user_id": 1,
            "service_type": "Bảo dưỡng",
            "technician_id": 2,
            "station_id": 3,
            "start_time": "2026-07-01T10:00:00",
            "end_time": "2026-07-01T11:00:00"
        })

        bookings = BookingService.get_bookings_by_user(1)

    assert len(bookings) == 2
    assert bookings[0].id == second.id
    assert bookings[1].id == first.id
