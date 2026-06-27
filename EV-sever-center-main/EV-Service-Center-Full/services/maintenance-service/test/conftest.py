import os
import sys
import pytest

# Thêm thư mục maintenance-service vào PYTHONPATH
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from flask import Flask
from app import db
from models.maintenance_model import (
    MaintenanceTask,
    TaskPart,
    MaintenanceChecklist,
)


@pytest.fixture(scope="session")
def app():
    app = Flask(__name__)

    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture()
def sample_task(app_context):
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

    return task