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
