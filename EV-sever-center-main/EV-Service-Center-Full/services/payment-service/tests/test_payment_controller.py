# File: services/payment-service/tests/test_payment_controller.py

import os
import sys
import json
from unittest.mock import patch, MagicMock
import pytest
from flask_jwt_extended import create_access_token

# Đảm bảo import được các module của service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from models.payment_model import PaymentTransaction

# Helper function để sinh JWT token trong test
def get_auth_headers(app, identity, role="user"):
    with app.app_context():
        token = create_access_token(identity=str(identity), additional_claims={"role": role})
        return {"Authorization": f"Bearer {token}"}

# ----------------- PUBLIC / HEALTH CHECK ROUTES -----------------

def test_health_route(client):
    """Test API endpoint health check công khai"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "Payment Service is running!"}


# ----------------- INTERNAL CORE ROUTES (CREATE PAYMENT) -----------------

@patch('services.payment_service.PaymentService.create_payment_request')
def test_create_payment_route_success(mock_create_req, client):
    """Test API tạo thanh toán thành công (yêu cầu internal token)"""
    mock_create_req.return_value = ({"id": 1, "status": "pending", "amount": 50000.0}, None)
    
    headers = {"X-Internal-Token": "test_internal_token", "Content-Type": "application/json"}
    payload = {
        "invoice_id": 1,
        "method": "momo_qr",
        "user_id": 10,
        "amount": 50000.0
    }
    
    response = client.post("/api/payments/create", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json["status"] == "pending"
    assert response.json["amount"] == 50000.0
    mock_create_req.assert_called_once_with(1, "momo_qr", 10, 50000.0)


def test_create_payment_route_missing_fields(client):
    """Test API tạo thanh toán báo lỗi khi thiếu trường dữ liệu"""
    headers = {"X-Internal-Token": "test_internal_token", "Content-Type": "application/json"}
    payload = {
        "invoice_id": 1,
        "method": "momo_qr"
        # thiếu user_id và amount
    }
    
    response = client.post("/api/payments/create", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Missing required fields" in response.json["error"]


def test_create_payment_route_unauthorized(client):
    """Test API tạo thanh toán báo lỗi khi thiếu hoặc sai token nội bộ"""
    headers = {"X-Internal-Token": "wrong_token", "Content-Type": "application/json"}
    payload = {
        "invoice_id": 1,
        "method": "momo_qr",
        "user_id": 10,
        "amount": 50000.0
    }
    
    response = client.post("/api/payments/create", json=payload, headers=headers)
    assert response.status_code == 401
    assert "Unauthorized internal request" in response.json["error"]


@patch('services.payment_service.PaymentService.create_payment_request')
def test_create_payment_route_service_error(mock_create_req, client):
    """Test API tạo thanh toán báo lỗi khi logic nghiệp vụ trả về lỗi"""
    mock_create_req.return_value = (None, "Hóa đơn này đã được thanh toán.")
    
    headers = {"X-Internal-Token": "test_internal_token", "Content-Type": "application/json"}
    payload = {
        "invoice_id": 1,
        "method": "momo_qr",
        "user_id": 10,
        "amount": 50000.0
    }
    
    response = client.post("/api/payments/create", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.json["error"] == "Hóa đơn này đã được thanh toán."


# ----------------- WEBHOOK GATEWAY ROUTES -----------------

@patch('services.payment_service.PaymentService.handle_pg_webhook')
def test_webhook_route_success(mock_webhook, client):
    """Test xử lý webhook từ cổng thanh toán thành công"""
    mock_tx = MagicMock()
    mock_webhook.return_value = (mock_tx, None)
    
    payload = {
        "pg_transaction_id": "PG_12345",
        "status": "success"
    }
    
    response = client.post("/api/payments/webhook", json=payload)
    assert response.status_code == 200
    assert "Webhook processed successfully" in response.json["message"]


def test_webhook_route_missing_fields(client):
    """Test webhook báo lỗi khi thiếu thông số đầu vào"""
    payload = {
        "status": "success"
        # thiếu pg_transaction_id
    }
    
    response = client.post("/api/payments/webhook", json=payload)
    assert response.status_code == 400
    assert "Missing required fields" in response.json["error"]


@patch('services.payment_service.PaymentService.handle_pg_webhook')
def test_webhook_route_already_processed(mock_webhook, client):
    """Test webhook trả về 200 khi giao dịch đã xử lý trước đó (Idempotent)"""
    mock_tx = MagicMock()
    mock_tx.to_dict.return_value = {"id": 1, "status": "success"}
    mock_webhook.return_value = (mock_tx, "Giao dịch đã được xử lý thành công trước đó.")
    
    payload = {
        "pg_transaction_id": "PG_12345",
        "status": "success"
    }
    
    response = client.post("/api/payments/webhook", json=payload)
    assert response.status_code == 200
    assert "xử lý thành công trước đó" in response.json["message"]
    assert response.json["transaction"]["status"] == "success"


@patch('services.payment_service.PaymentService.handle_pg_webhook')
def test_webhook_route_error(mock_webhook, client):
    """Test webhook báo lỗi 400 khi trạng thái cập nhật bị lỗi logic"""
    mock_webhook.return_value = (None, "Trạng thái webhook không hợp lệ.")
    
    payload = {
        "pg_transaction_id": "PG_12345",
        "status": "invalid_status"
    }
    
    response = client.post("/api/payments/webhook", json=payload)
    assert response.status_code == 400
    assert response.json["error"] == "Trạng thái webhook không hợp lệ."


# ----------------- JWT HISTORY ROUTES -----------------

def test_history_my_route_unauthorized(client):
    """Test lịch sử cá nhân bị từ chối nếu không có JWT token"""
    response = client.get("/api/payments/history/my")
    assert response.status_code == 401


@patch('services.payment_service.PaymentService.get_history_by_user')
def test_history_my_route_success(mock_get_hist, client, app):
    """Test lịch sử cá nhân thành công với JWT token hợp lệ"""
    # Khởi tạo mock database model
    mock_tx = MagicMock()
    mock_tx.to_dict.return_value = {"id": 1, "user_id": 10, "amount": 50000.0, "status": "success"}
    mock_get_hist.return_value = [mock_tx]
    
    headers = get_auth_headers(app, identity=10, role="user")
    
    response = client.get("/api/payments/history/my", headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["user_id"] == 10
    mock_get_hist.assert_called_once_with("10")


def test_history_all_route_forbidden_for_user(client, app):
    """Test lịch sử toàn hệ thống (Admin-only) trả về 403 đối với tài khoản User thường"""
    headers = get_auth_headers(app, identity=10, role="user")
    
    response = client.get("/api/payments/history/all", headers=headers)
    assert response.status_code == 403
    assert "Admins only" in response.json["error"]


@patch('services.payment_service.PaymentService.get_all_history')
def test_history_all_route_success_for_admin(mock_get_all, client, app):
    """Test lịch sử toàn hệ thống thành công đối với tài khoản Admin"""
    mock_tx = MagicMock()
    mock_tx.to_dict.return_value = {"id": 1, "user_id": 10, "amount": 50000.0, "status": "success"}
    mock_get_all.return_value = [mock_tx]
    
    headers = get_auth_headers(app, identity=1, role="admin")
    
    response = client.get("/api/payments/history/all", headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 1
    mock_get_all.assert_called_once()


# ----------------- INTERNAL REPORT / SCHEDULER ROUTES -----------------

def test_internal_all_route_unauthorized(client):
    """Test lấy toàn bộ giao dịch nội bộ bị từ chối nếu không có token"""
    response = client.get("/internal/payments/all")
    assert response.status_code == 401


@patch('services.payment_service.PaymentService.get_all_history')
def test_internal_all_route_success(mock_get_all, client):
    """Test lấy toàn bộ giao dịch nội bộ thành công với X-Internal-Token"""
    mock_get_all.return_value = []
    
    headers = {"X-Internal-Token": "test_internal_token"}
    response = client.get("/internal/payments/all", headers=headers)
    
    assert response.status_code == 200
    assert response.json == []


@patch('services.payment_service.PaymentService.get_all_history')
def test_internal_due_soon_route_success(mock_get_all, client):
    """Test lấy các hóa đơn sắp hết hạn với X-Internal-Token"""
    # Tạo mock giao dịch pending
    mock_tx = MagicMock()
    mock_tx.id = 1
    mock_tx.user_id = 10
    mock_tx.amount = 50000.0
    mock_tx.status = "pending"
    # Giả lập due date (sắp đến hạn trong 1 ngày)
    import datetime
    mock_tx.due_date = datetime.datetime.now() + datetime.timedelta(days=1, hours=1)
    mock_tx.to_dict.return_value = {"id": 1, "status": "pending", "amount": 50000.0}
    
    mock_get_all.return_value = [mock_tx]
    
    headers = {"X-Internal-Token": "test_internal_token"}
    response = client.get("/internal/payments/due-soon", headers=headers)
    
    assert response.status_code == 200
    assert response.json["success"] is True
    # Kiểm tra đã lọc ra 1 item sắp đến hạn (còn 1 ngày)
    assert response.json["count"] == 1
    assert response.json["payments"][0]["id"] == 1


def test_internal_health_route(client):
    """Test check sức khỏe API nội bộ"""
    headers = {"X-Internal-Token": "test_internal_token"}
    response = client.get("/internal/payments/health", headers=headers)
    
    assert response.status_code == 200
    assert response.json["status"] == "healthy"
