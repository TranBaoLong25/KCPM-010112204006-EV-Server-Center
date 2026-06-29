import json
from datetime import datetime
from unittest.mock import patch

import pytest

from models.booking_model import Booking


@pytest.mark.blackbox
def test_create_booking_api_success(client, user_token):
    with patch("services.booking_service.BookingService._verify_user") as mock_verify_user, patch(
        "services.booking_service.BookingService._notify_booking_created"
    ) as mock_notify:
        mock_verify_user.return_value = ({"username": "apiuser"}, None)
        mock_notify.return_value = (True, "Notification skipped")

        payload = {
            "service_type": "Bảo dưỡng ắc quy",
            "technician_id": 2,
            "station_id": 3,
            "start_time": "2026-07-01T08:00:00",
            "end_time": "2026-07-01T09:00:00"
        }

        response = client.post(
            "/api/bookings/items",
            json=payload,
            headers={"Authorization": f"Bearer {user_token}"}
        )

    body = response.get_json()

    assert response.status_code == 201
    assert body["message"] == "Đặt lịch thành công!"
    assert body["booking"]["user_id"] == 1
    assert body["booking"]["status"] == "confirmed"


@pytest.mark.blackbox
def test_create_booking_missing_service_type(client, user_token):
    response = client.post(
        "/api/bookings/items",
        json={
            "technician_id": 2,
            "station_id": 3,
            "start_time": "2026-07-01T08:00:00",
            "end_time": "2026-07-01T09:00:00"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


@pytest.mark.blackbox
def test_create_booking_invalid_time(client, user_token):
    with patch("services.booking_service.BookingService._verify_user") as mock_verify_user:
        mock_verify_user.return_value = ({"username": "apiuser"}, None)

        response = client.post(
            "/api/bookings/items",
            json={
                "service_type": "Bảo dưỡng",
                "technician_id": 2,
                "station_id": 3,
                "start_time": "2026-07-01T10:00:00",
                "end_time": "2026-07-01T09:00:00"
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )

    assert response.status_code == 400
    assert "error" in response.get_json()


@pytest.mark.blackbox
def test_get_booking_not_found(client, admin_token):
    response = client.get(
        "/api/bookings/items/999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Không tìm thấy lịch đặt."


@pytest.mark.blackbox
def test_get_service_centers_empty(client):
    response = client.get("/api/bookings/centers")

    assert response.status_code == 200
    assert response.get_json() == []


@pytest.mark.blackbox
def test_create_service_center_admin_success(client, admin_token):
    payload = {
        "name": "Trung tâm EV 1",
        "address": "123 Đường Test",
        "phone": "0123456789"
    }

    response = client.post(
        "/api/bookings/centers",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    body = response.get_json()

    assert response.status_code == 201
    assert body["center"]["name"] == "Trung tâm EV 1"


@pytest.mark.blackbox
def test_internal_get_all_bookings_unauthorized(client):
    response = client.get("/internal/bookings/all")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized internal request"


@pytest.mark.blackbox
def test_internal_get_all_bookings_success(client):
    from app import db

    with patch("services.booking_service.BookingService._verify_user") as mock_verify:
        mock_verify.return_value = ({"username": "apiuser"}, None)
        from models.booking_model import Booking

        with client.application.app_context():
            booking = Booking(
                user_id=1,
                customer_name="apiuser",
                service_type="Bảo dưỡng",
                technician_id=2,
                station_id=3,
                start_time="2026-07-01T08:00:00",
                end_time="2026-07-01T09:00:00",
                status="confirmed"
            )
            booking.start_time = datetime.fromisoformat("2026-07-01T08:00:00")
            booking.end_time = datetime.fromisoformat("2026-07-01T09:00:00")
            db.session.add(booking)
            db.session.commit()

        response = client.get(
            "/internal/bookings/all",
            headers={"X-Internal-Token": "test-internal-token"}
        )

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
