from app import db
from models.staff_model import Staff, StaffShift, StaffAssignment, StaffCertificate


class FakeUserServiceResponse:
    def __init__(self, status_code=201):
        self.status_code = status_code

    def json(self):
        return {
            "user": {
                "id": 100,
                "username": "newstaff"
            }
        }


def test_create_staff_success(client, auth_header, monkeypatch):
    from controllers import staff_controller

    monkeypatch.setattr(
        staff_controller.requests,
        "post",
        lambda *args, **kwargs: FakeUserServiceResponse(201)
    )

    response = client.post(
        "/api/staff/",
        headers=auth_header,
        json={
            "full_name": "Tran Van B",
            "email": "newstaff@evcenter.com",
            "phone": "0987654321",
            "role": "technician",
            "specialization": "general",
            "status": "active",
            "department": "Maintenance"
        }
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["success"] is True
    assert data["staff"]["email"] == "newstaff@evcenter.com"


def test_create_staff_missing_required_fields(client, auth_header):
    response = client.post(
        "/api/staff/",
        headers=auth_header,
        json={
            "email": "missingname@evcenter.com",
            "role": "technician"
        }
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["success"] is False
    assert data["error"] == "Missing required fields"


def test_create_staff_duplicate_email(client, auth_header, sample_staff):
    response = client.post(
        "/api/staff/",
        headers=auth_header,
        json={
            "full_name": "Duplicate Staff",
            "email": "staff01@evcenter.com",
            "role": "technician"
        }
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["success"] is False
    assert data["error"] == "Email already exists"


def test_get_staff_detail_success(client, auth_header, sample_staff):
    response = client.get(
        f"/api/staff/{sample_staff.id}",
        headers=auth_header
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["staff"]["id"] == sample_staff.id


def test_get_staff_detail_not_found(client, auth_header):
    response = client.get(
        "/api/staff/99999",
        headers=auth_header
    )

    data = response.get_json()

    assert response.status_code == 404
    assert data["success"] is False
    assert data["error"] == "Staff not found"


def test_update_staff_success(client, auth_header, sample_staff):
    response = client.put(
        f"/api/staff/{sample_staff.id}",
        headers=auth_header,
        json={
            "full_name": "Nguyen Van A Updated",
            "phone": "0999999999",
            "status": "busy"
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["staff"]["full_name"] == "Nguyen Van A Updated"
    assert data["staff"]["status"] == "busy"


def test_update_staff_not_found(client, auth_header):
    response = client.put(
        "/api/staff/99999",
        headers=auth_header,
        json={
            "full_name": "Not Found"
        }
    )

    data = response.get_json()

    assert response.status_code == 404
    assert data["success"] is False
    assert data["error"] == "Staff not found"


def test_delete_staff_success(client, auth_header, sample_staff):
    response = client.delete(
        f"/api/staff/{sample_staff.id}",
        headers=auth_header
    )

    data = response.get_json()
    staff = Staff.query.get(sample_staff.id)

    assert response.status_code == 200
    assert data["success"] is True
    assert staff.status == "resigned"


def test_delete_staff_not_found(client, auth_header):
    response = client.delete(
        "/api/staff/99999",
        headers=auth_header
    )

    data = response.get_json()

    assert response.status_code == 404
    assert data["success"] is False
    assert data["error"] == "Staff not found"


def test_create_shift_success(client, auth_header, sample_staff):
    response = client.post(
        "/api/shifts/",
        headers=auth_header,
        json={
            "staff_id": sample_staff.id,
            "shift_date": "2026-06-01",
            "shift_type": "morning",
            "start_time": "08:00:00",
            "end_time": "12:00:00"
        }
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["success"] is True
    assert data["shift"]["staff_id"] == sample_staff.id
    assert data["shift"]["shift_type"] == "morning"


def test_create_shift_staff_not_found(client, auth_header):
    response = client.post(
        "/api/shifts/",
        headers=auth_header,
        json={
            "staff_id": 99999,
            "shift_date": "2026-06-01",
            "shift_type": "morning",
            "start_time": "08:00:00",
            "end_time": "12:00:00"
        }
    )

    data = response.get_json()

    assert response.status_code == 404
    assert data["success"] is False
    assert data["error"] == "Staff not found"


def test_create_assignment_success(client, auth_header, sample_staff):
    response = client.post(
        "/api/assignments/",
        headers=auth_header,
        json={
            "staff_id": sample_staff.id,
            "maintenance_task_id": 101,
            "priority": "high",
            "estimated_duration_minutes": 120,
            "notes": "Giao việc kiểm tra pin"
        }
    )

    data = response.get_json()
    staff = Staff.query.get(sample_staff.id)

    assert response.status_code == 201
    assert data["success"] is True
    assert data["assignment"]["staff_id"] == sample_staff.id
    assert staff.status == "busy"


def test_create_assignment_staff_not_found(client, auth_header):
    response = client.post(
        "/api/assignments/",
        headers=auth_header,
        json={
            "staff_id": 99999,
            "maintenance_task_id": 101,
            "priority": "high"
        }
    )

    data = response.get_json()

    assert response.status_code == 404
    assert data["success"] is False
    assert data["error"] == "Staff not found"


def test_create_assignment_duplicate_task(client, auth_header, sample_staff):
    assignment = StaffAssignment(
        staff_id=sample_staff.id,
        maintenance_task_id=101,
        status="assigned",
        priority="medium"
    )

    db.session.add(assignment)
    db.session.commit()

    response = client.post(
        "/api/assignments/",
        headers=auth_header,
        json={
            "staff_id": sample_staff.id,
            "maintenance_task_id": 101,
            "priority": "high"
        }
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["success"] is False
    assert data["error"] == "Task already assigned"


def test_create_certificate_success(client, auth_header, sample_staff):
    response = client.post(
        "/api/certificates/",
        headers=auth_header,
        json={
            "staff_id": sample_staff.id,
            "certificate_name": "EV Battery Specialist",
            "certificate_type": "ev_certification",
            "issued_date": "2026-01-01",
            "expiry_date": "2027-01-01",
            "issuing_organization": "VinFast Academy",
            "certificate_number": "CERT001"
        }
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["success"] is True
    assert data["certificate"]["staff_id"] == sample_staff.id
    assert data["certificate"]["certificate_name"] == "EV Battery Specialist"


def test_create_certificate_staff_not_found(client, auth_header):
    response = client.post(
        "/api/certificates/",
        headers=auth_header,
        json={
            "staff_id": 99999,
            "certificate_name": "EV Battery Specialist",
            "certificate_type": "ev_certification"
        }
    )

    data = response.get_json()

    assert response.status_code == 404
    assert data["success"] is False
    assert data["error"] == "Staff not found"