# File: services/payment-service/tests/test_payment_service.py

import os
import sys
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytest
from sqlalchemy.exc import IntegrityError

# Đảm bảo import được các module của service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from models.payment_model import PaymentTransaction
from services.payment_service import PaymentService

# ----------------- TESTS CHO CREATE_PAYMENT_REQUEST -----------------

@patch('services.payment_service.PaymentService._get_invoice_details')
def test_create_momo_success(mock_get_invoice, db_session):
    """Test tạo giao dịch MoMo QR thành công"""
    # Thiết lập mock invoice chi tiết
    mock_get_invoice.return_value = ({
        "id": 1,
        "status": "pending",
        "user_id": 10,
        "total_amount": 50000.0,
        "booking_id": 100
    }, None)

    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="momo_qr",
        user_id=10,
        amount=50000.0
    )

    assert error is None
    assert tx_dict is not None
    assert tx_dict["status"] == "pending"
    assert tx_dict["amount"] == 50000.0
    assert tx_dict["method"] == "momo_qr"
    assert tx_dict["invoice_id"] == 1
    assert tx_dict["user_id"] == 10
    assert tx_dict["pg_transaction_id"].startswith("PG_MOMO_QR_1_50000_")

    # Kiểm tra lưu vào DB
    db_tx = PaymentTransaction.query.filter_by(invoice_id=1).first()
    assert db_tx is not None
    assert db_tx.status == "pending"


@patch('services.payment_service.PaymentService._get_invoice_details')
def test_create_bank_success(mock_get_invoice, db_session):
    """Test tạo giao dịch chuyển khoản ngân hàng thành công"""
    mock_get_invoice.return_value = ({
        "id": 2,
        "status": "pending",
        "user_id": 11,
        "total_amount": 120000.0,
        "booking_id": 101
    }, None)

    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=2,
        method="bank_transfer",
        user_id=11,
        amount=120000.0
    )

    assert error is None
    assert tx_dict is not None
    assert tx_dict["method"] == "bank_transfer"
    assert tx_dict["pg_transaction_id"].startswith("PG_BANK_TRANSFER_2_120000_")


def test_create_invalid_method(db_session):
    """Test tạo giao dịch với phương thức không hợp lệ"""
    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="stripe_card", # Không hỗ trợ
        user_id=10,
        amount=50000.0
    )
    assert tx_dict is None
    assert "Phương thức thanh toán không hợp lệ" in error


def test_create_invalid_types(db_session):
    """Test tạo giao dịch với kiểu dữ liệu không hợp lệ"""
    tx_dict, error = PaymentService.create_payment_request(
        invoice_id="abc", # Chuỗi không thể parse sang int
        method="momo_qr",
        user_id=10,
        amount=50000.0
    )
    assert tx_dict is None
    assert "Dữ liệu invoice_id, user_id hoặc amount không hợp lệ" in error


def test_create_negative_amount(db_session):
    """Test tạo giao dịch với số tiền <= 0"""
    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="momo_qr",
        user_id=10,
        amount=-500.0
    )
    assert tx_dict is None
    assert "Số tiền thanh toán phải lớn hơn 0" in error


@patch('services.payment_service.PaymentService._get_invoice_details')
def test_create_invoice_not_found(mock_get_invoice, db_session):
    """Test tạo giao dịch khi hóa đơn không tồn tại hoặc API lỗi"""
    mock_get_invoice.return_value = (None, "Invoice not found")

    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="momo_qr",
        user_id=10,
        amount=50000.0
    )
    assert tx_dict is None
    assert "Không tìm thấy hóa đơn hoặc không thể xác minh hóa đơn" in error


@patch('services.payment_service.PaymentService._get_invoice_details')
def test_create_invoice_already_paid(mock_get_invoice, db_session):
    """Test tạo giao dịch khi hóa đơn đã được thanh toán"""
    mock_get_invoice.return_value = ({
        "id": 1,
        "status": "paid",
        "user_id": 10,
        "total_amount": 50000.0
    }, None)

    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="momo_qr",
        user_id=10,
        amount=50000.0
    )
    assert tx_dict is None
    assert "Hóa đơn này đã được thanh toán" in error


@patch('services.payment_service.PaymentService._get_invoice_details')
def test_create_invoice_canceled(mock_get_invoice, db_session):
    """Test tạo giao dịch khi hóa đơn bị hủy"""
    mock_get_invoice.return_value = ({
        "id": 1,
        "status": "canceled",
        "user_id": 10,
        "total_amount": 50000.0
    }, None)

    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="momo_qr",
        user_id=10,
        amount=50000.0
    )
    assert tx_dict is None
    assert "Hóa đơn này đã bị hủy, không thể thanh toán" in error


@patch('services.payment_service.PaymentService._get_invoice_details')
def test_create_user_mismatch(mock_get_invoice, db_session):
    """Test tạo giao dịch khi user không khớp với chủ sở hữu hóa đơn"""
    mock_get_invoice.return_value = ({
        "id": 1,
        "status": "pending",
        "user_id": 99, # Hóa đơn của user 99
        "total_amount": 50000.0
    }, None)

    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="momo_qr",
        user_id=10, # Request gửi lên từ user 10
        amount=50000.0
    )
    assert tx_dict is None
    assert "User không khớp với chủ sở hữu hóa đơn" in error


@patch('services.payment_service.PaymentService._get_invoice_details')
def test_create_amount_mismatch(mock_get_invoice, db_session):
    """Test tạo giao dịch khi số tiền không khớp hóa đơn"""
    mock_get_invoice.return_value = ({
        "id": 1,
        "status": "pending",
        "user_id": 10,
        "total_amount": 50000.0
    }, None)

    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="momo_qr",
        user_id=10,
        amount=49000.0 # Số tiền lệch
    )
    assert tx_dict is None
    assert "Số tiền thanh toán không khớp với tổng tiền hóa đơn" in error


@patch('services.payment_service.PaymentService._get_invoice_details')
def test_create_pending_exists(mock_get_invoice, db_session):
    """Test tạo giao dịch khi đã có 1 giao dịch pending khác cho hóa đơn này"""
    mock_get_invoice.return_value = ({
        "id": 1,
        "status": "pending",
        "user_id": 10,
        "total_amount": 50000.0
    }, None)

    # Thêm sẵn 1 giao dịch pending vào database
    existing_tx = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="pending",
        pg_transaction_id="PG_MOMO_OLD"
    )
    db.session.add(existing_tx)
    db.session.commit()

    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="momo_qr",
        user_id=10,
        amount=50000.0
    )
    assert tx_dict is None
    assert "Đã có giao dịch đang chờ thanh toán cho hóa đơn này" in error


@patch('services.payment_service.PaymentService._get_invoice_details')
@patch('app.db.session.commit')
def test_create_db_integrity_error(mock_commit, mock_get_invoice, db_session):
    """Test xử lý lỗi db IntegrityError khi commit"""
    mock_get_invoice.return_value = ({
        "id": 1,
        "status": "pending",
        "user_id": 10,
        "total_amount": 50000.0
    }, None)
    mock_commit.side_effect = IntegrityError("Integrity error mock", {}, None)

    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="momo_qr",
        user_id=10,
        amount=50000.0
    )
    assert tx_dict is None
    assert "Đã có giao dịch đang chờ hoặc giao dịch trùng lặp" in error


@patch('services.payment_service.PaymentService._get_invoice_details')
@patch('app.db.session.commit')
def test_create_db_general_error(mock_commit, mock_get_invoice, db_session):
    """Test xử lý lỗi db ngoại lệ chung khi commit"""
    mock_get_invoice.return_value = ({
        "id": 1,
        "status": "pending",
        "user_id": 10,
        "total_amount": 50000.0
    }, None)
    mock_commit.side_effect = Exception("General database crash")

    tx_dict, error = PaymentService.create_payment_request(
        invoice_id=1,
        method="momo_qr",
        user_id=10,
        amount=50000.0
    )
    assert tx_dict is None
    assert "Lỗi máy chủ nghiêm trọng khi tạo giao dịch" in error


# ----------------- TESTS CHO HANDLE_PG_WEBHOOK -----------------

@patch('services.notification_helper.NotificationHelper.send_notification')
@patch('services.payment_service.PaymentService._update_booking_status')
@patch('services.payment_service.PaymentService._get_invoice_details')
@patch('services.payment_service.PaymentService._update_invoice_status')
def test_webhook_success(mock_update_invoice, mock_get_invoice, mock_update_booking, mock_notify, db_session):
    """Test xử lý webhook thanh toán thành công hoàn chỉnh"""
    # Khởi tạo giao dịch pending trong DB
    tx = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="pending",
        pg_transaction_id="PG_MOMO_TEST_123",
        payment_data_json=json.dumps({"qr_code_url": "url", "amount": 50000})
    )
    db.session.add(tx)
    db.session.commit()

    # Cấu hình mock cho API nội bộ và Notification
    mock_update_invoice.return_value = ({"status": "paid"}, None)
    mock_get_invoice.return_value = ({"id": 1, "booking_id": 200}, None)
    mock_update_booking.return_value = ({"status": "completed"}, None)
    mock_notify.return_value = True

    updated_tx, error = PaymentService.handle_pg_webhook("PG_MOMO_TEST_123", "success")

    assert error is None
    assert updated_tx.status == "success"
    
    # Kiểm tra các mock được gọi đúng
    mock_update_invoice.assert_called_once_with(1, 'paid')
    mock_get_invoice.assert_called_once_with(1)
    mock_update_booking.assert_called_once_with(200, 'completed')
    mock_notify.assert_called_once()


@patch('services.notification_helper.NotificationHelper.send_notification')
def test_webhook_failed(mock_notify, db_session):
    """Test xử lý webhook thanh toán thất bại"""
    tx = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="pending",
        pg_transaction_id="PG_MOMO_TEST_123",
        payment_data_json=json.dumps({})
    )
    db.session.add(tx)
    db.session.commit()

    mock_notify.return_value = True

    updated_tx, error = PaymentService.handle_pg_webhook("PG_MOMO_TEST_123", "failed")

    assert error is None
    assert updated_tx.status == "failed"
    mock_notify.assert_called_once()


@patch('services.notification_helper.NotificationHelper.send_notification')
def test_webhook_expired(mock_notify, db_session):
    """Test xử lý webhook thanh toán hết hạn"""
    tx = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="pending",
        pg_transaction_id="PG_MOMO_TEST_123",
        payment_data_json=json.dumps({})
    )
    db.session.add(tx)
    db.session.commit()

    mock_notify.return_value = True

    updated_tx, error = PaymentService.handle_pg_webhook("PG_MOMO_TEST_123", "expired")

    assert error is None
    assert updated_tx.status == "expired"
    mock_notify.assert_called_once()


@patch('services.notification_helper.NotificationHelper.send_notification')
@patch('services.payment_service.PaymentService._update_booking_status')
@patch('services.payment_service.PaymentService._get_invoice_details')
@patch('services.payment_service.PaymentService._update_invoice_status')
def test_webhook_success_pg_prefix(mock_update_invoice, mock_get_invoice, mock_update_booking, mock_notify, db_session):
    """Test xử lý webhook nhận id chứa tiền tố SUCCESS_PG_"""
    tx = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="pending",
        pg_transaction_id="PG_MOMO_TEST_123",
        payment_data_json=json.dumps({"qr_code_url": "url", "amount": 50000})
    )
    db.session.add(tx)
    db.session.commit()

    mock_update_invoice.return_value = ({"status": "paid"}, None)
    mock_get_invoice.return_value = ({"id": 1, "booking_id": 200}, None)
    mock_update_booking.return_value = ({"status": "completed"}, None)
    mock_notify.return_value = True

    # Gọi webhook với tiền tố SUCCESS_PG_
    updated_tx, error = PaymentService.handle_pg_webhook("SUCCESS_PG_PG_MOMO_TEST_123", "success")

    assert error is None
    assert updated_tx.status == "success"


def test_webhook_tx_not_found(db_session):
    """Test webhook với ID giao dịch không tồn tại"""
    updated_tx, error = PaymentService.handle_pg_webhook("PG_NOT_EXIST", "success")
    assert updated_tx is None
    assert "Không tìm thấy giao dịch với PG ID này" in error


def test_webhook_already_processed(db_session):
    """Test tính lũy đẳng: Webhook gửi trạng thái success khi giao dịch đã success"""
    tx = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="success", # Đã success từ trước
        pg_transaction_id="PG_MOMO_TEST_123",
        payment_data_json=json.dumps({})
    )
    db.session.add(tx)
    db.session.commit()

    updated_tx, error = PaymentService.handle_pg_webhook("PG_MOMO_TEST_123", "success")

    assert updated_tx is not None
    assert updated_tx.status == "success"
    assert "Giao dịch đã được xử lý thành công trước đó" in error


def test_webhook_not_pending_fail(db_session):
    """Test webhook gửi success nhưng trạng thái hiện tại khác pending (ví dụ failed)"""
    tx = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="failed", # Đã failed
        pg_transaction_id="PG_MOMO_TEST_123",
        payment_data_json=json.dumps({})
    )
    db.session.add(tx)
    db.session.commit()

    updated_tx, error = PaymentService.handle_pg_webhook("PG_MOMO_TEST_123", "success")

    assert updated_tx is None
    assert "Không thể xác nhận thanh toán khi giao dịch đang ở trạng thái 'failed'" in error


def test_webhook_invalid_status(db_session):
    """Test webhook gửi trạng thái final_status không hợp lệ"""
    tx = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="pending",
        pg_transaction_id="PG_MOMO_TEST_123",
        payment_data_json=json.dumps({})
    )
    db.session.add(tx)
    db.session.commit()

    updated_tx, error = PaymentService.handle_pg_webhook("PG_MOMO_TEST_123", "unknown_status")

    assert updated_tx is None
    assert "Trạng thái webhook không hợp lệ" in error


# ----------------- TESTS CHO EXPIRE_PENDING_TRANSACTIONS -----------------

@patch('services.notification_helper.NotificationHelper.send_notification')
def test_expire_pending_transactions(mock_notify, db_session):
    """Test quét và hủy các giao dịch pending quá hạn 15 phút"""
    mock_notify.return_value = True

    # 1. Giao dịch pending tạo cách đây 20 phút (quá hạn)
    tx_expired = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="pending",
        pg_transaction_id="PG_EXPIRED",
        created_at=datetime.utcnow() - timedelta(minutes=20)
    )

    # 2. Giao dịch pending tạo ngay bây giờ (chưa quá hạn)
    tx_active = PaymentTransaction(
        invoice_id=2,
        user_id=10,
        amount=30000.0,
        method="momo_qr",
        status="pending",
        pg_transaction_id="PG_ACTIVE",
        created_at=datetime.utcnow()
    )

    db.session.add(tx_expired)
    db.session.add(tx_active)
    db.session.commit()

    expired_count = PaymentService.expire_pending_transactions()

    assert expired_count == 1
    assert tx_expired.status == "expired"
    assert tx_active.status == "pending"


# ----------------- TESTS CHO HISTORY & OTHERS -----------------

def test_get_history_by_user(db_session):
    """Test lấy lịch sử giao dịch theo user_id"""
    tx1 = PaymentTransaction(
        invoice_id=1, user_id=10, amount=50000.0, method="momo_qr", status="success", pg_transaction_id="PG1"
    )
    tx2 = PaymentTransaction(
        invoice_id=2, user_id=10, amount=30000.0, method="momo_qr", status="pending", pg_transaction_id="PG2"
    )
    tx3 = PaymentTransaction(
        invoice_id=3, user_id=20, amount=90000.0, method="bank_transfer", status="success", pg_transaction_id="PG3"
    )
    db.session.add_all([tx1, tx2, tx3])
    db.session.commit()

    history = PaymentService.get_history_by_user(10)
    assert len(history) == 2
    assert history[0].pg_transaction_id in ["PG1", "PG2"]


def test_get_all_history(db_session):
    """Test lấy toàn bộ lịch sử giao dịch (cho Admin)"""
    tx1 = PaymentTransaction(
        invoice_id=1, user_id=10, amount=50000.0, method="momo_qr", status="success", pg_transaction_id="PG1"
    )
    tx2 = PaymentTransaction(
        invoice_id=2, user_id=20, amount=90000.0, method="bank_transfer", status="success", pg_transaction_id="PG2"
    )
    db.session.add_all([tx1, tx2])
    db.session.commit()

    history = PaymentService.get_all_history()
    assert len(history) == 2
