# File: services/payment-service/tests/conftest.py

import os
import sys
import pytest

# Thêm thư mục chứa service vào path để import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

@pytest.fixture(scope='session')
def app():
    """Tạo và cấu hình Flask app cho kiểm thử"""
    # Thiết lập các biến môi trường cần thiết trước khi tạo app
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
    os.environ['INTERNAL_SERVICE_TOKEN'] = 'test_internal_token'
    os.environ['FINANCE_SERVICE_URL'] = 'http://finance-service'
    os.environ['BOOKING_SERVICE_URL'] = 'http://booking-service'
    os.environ['MOMO_QR_CODE_URL'] = 'https://momo.vn/qr'

    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'INTERNAL_SERVICE_TOKEN': 'test_internal_token',
        'FINANCE_SERVICE_URL': 'http://finance-service',
        'BOOKING_SERVICE_URL': 'http://booking-service',
        'MOMO_QR_CODE_URL': 'https://momo.vn/qr'
    })

    return app

@pytest.fixture(scope='function')
def db_session(app):
    """Khởi tạo database tạm thời SQLite in-memory và dọn dẹp sau mỗi test case"""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Tạo client test của Flask để giả lập gọi API nếu cần"""
    return app.test_client()
