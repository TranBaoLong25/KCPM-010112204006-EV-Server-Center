import os
import sys
from pathlib import Path

import pytest
from flask_jwt_extended import create_access_token

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["INTERNAL_SERVICE_TOKEN"] = "test-internal-token"
os.environ["USER_SERVICE_URL"] = "http://fake-user-service"
os.environ["MAINTENANCE_SERVICE_URL"] = "http://fake-maintenance-service"

from app import create_app, db
from models.staff_model import Staff


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret"

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_header(app):
    with app.app_context():
        token = create_access_token(identity="1")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }


@pytest.fixture
def sample_staff(app):
    staff = Staff(
        user_id=1,
        full_name="Nguyen Van A",
        email="staff01@evcenter.com",
        phone="0912345678",
        role="technician",
        specialization="general",
        status="active",
        department="Maintenance",
        employee_code="EMP0001"
    )

    db.session.add(staff)
    db.session.commit()

    return staff