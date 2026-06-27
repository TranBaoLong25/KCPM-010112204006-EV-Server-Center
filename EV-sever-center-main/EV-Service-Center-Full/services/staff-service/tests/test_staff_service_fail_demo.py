from app import db
from models.staff_model import StaffAssignment


def test_duplicate_email_fail_demo(client, auth_header, sample_staff):
    response = client.post(
        "/api/staff/",
        headers=auth_header,
        json={
            "full_name": "Duplicate Staff",
            "email": "staff01@evcenter.com",
            "role": "technician"
        }
    )

    # Thực tế phải là 400, nhưng cố tình kỳ vọng 201 để tạo FAIL
    assert response.status_code == 201


def test_update_staff_not_found_fail_demo(client, auth_header):
    response = client.put(
        "/api/staff/99999",
        headers=auth_header,
        json={
            "full_name": "Not Found"
        }
    )

    # Thực tế phải là 404, nhưng cố tình kỳ vọng 200 để tạo FAIL
    assert response.status_code == 200


def test_delete_staff_not_found_fail_demo(client, auth_header):
    response = client.delete(
        "/api/staff/99999",
        headers=auth_header
    )

    # Thực tế phải là 404, nhưng cố tình kỳ vọng 200 để tạo FAIL
    assert response.status_code == 200


def test_create_shift_staff_not_found_fail_demo(client, auth_header):
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

    # Thực tế phải là 404, nhưng cố tình kỳ vọng 201 để tạo FAIL
    assert response.status_code == 201


def test_create_assignment_duplicate_task_fail_demo(client, auth_header, sample_staff):
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

    # Thực tế phải là 400, nhưng cố tình kỳ vọng 201 để tạo FAIL
    assert response.status_code == 201