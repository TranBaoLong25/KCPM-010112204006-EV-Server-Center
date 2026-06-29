import os
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["INTERNAL_SERVICE_TOKEN"] = "test-internal-token"
os.environ["USER_SERVICE_URL"] = "http://localhost"
os.environ["NOTIFICATION_SERVICE_URL"] = "http://localhost"

from app import create_app, db


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["INTERNAL_SERVICE_TOKEN"] = "test-internal-token"
    app.config["USER_SERVICE_URL"] = "http://localhost"

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
def user_token(app):
    from flask_jwt_extended import create_access_token
    with app.app_context():
        return create_access_token(identity=1, additional_claims={"role": "user"})


@pytest.fixture
def admin_token(app):
    from flask_jwt_extended import create_access_token
    with app.app_context():
        return create_access_token(identity=1, additional_claims={"role": "admin"})
