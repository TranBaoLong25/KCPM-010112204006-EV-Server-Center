# File: services/payment-service/tests/test_payment_service_fail_demo.py

import os
import sys
import pytest
from unittest.mock import patch

# Đảm bảo import được các module của service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from models.payment_model import PaymentTransaction
from services.payment_service import PaymentService

@patch('services.payment_service.PaymentService._get_invoice_details')
def test_fail_demo_initial_status(mock_get_invoice, db_session):
    """FAIL DEMO: Kỳ vọng giao dịch mới tạo có ngay trạng thái 'success' (Thực tế là 'pending')"""
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
        amount=50000.0
    )

    assert error is None
    # LỖI CỐ Ý: Trạng thái đúng phải là 'pending'
    assert tx_dict["status"] == "success", "Demo Failure: Giao dịch mới tạo phải ở trạng thái pending!"


@patch('services.notification_helper.NotificationHelper.send_notification')
@patch('services.payment_service.PaymentService._update_booking_status')
@patch('services.payment_service.PaymentService._get_invoice_details')
@patch('services.payment_service.PaymentService._update_invoice_status')
def test_fail_demo_webhook_amount(mock_update_invoice, mock_get_invoice, mock_update_booking, mock_notify, db_session):
    """FAIL DEMO: Kỳ vọng số tiền giao dịch tăng gấp đôi sau khi webhook báo thành công (Thực tế không đổi)"""
    tx = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="pending",
        pg_transaction_id="PG_MOMO_TEST",
        payment_data_json='{}'
    )
    db.session.add(tx)
    db.session.commit()

    mock_update_invoice.return_value = ({"status": "paid"}, None)
    mock_get_invoice.return_value = ({"id": 1, "booking_id": 200}, None)
    mock_update_booking.return_value = ({"status": "completed"}, None)
    mock_notify.return_value = True

    updated_tx, error = PaymentService.handle_pg_webhook("PG_MOMO_TEST", "success")

    assert error is None
    # LỖI CỐ Ý: Số tiền thực tế vẫn là 50000.0, không đổi thành 100000.0
    assert updated_tx.amount == 100000.0, "Demo Failure: Số tiền giao dịch bị thay đổi sai lệch!"


def test_fail_demo_history_count(db_session):
    """FAIL DEMO: Kỳ vọng tìm thấy 5 giao dịch trong lịch sử sau khi chỉ tạo 1 giao dịch"""
    tx = PaymentTransaction(
        invoice_id=1,
        user_id=10,
        amount=50000.0,
        method="momo_qr",
        status="pending",
        pg_transaction_id="PG_TEST"
    )
    db.session.add(tx)
    db.session.commit()

    history = PaymentService.get_history_by_user(10)
    # LỖI CỐ Ý: Thực tế len(history) == 1
    assert len(history) == 5, "Demo Failure: Số lượng giao dịch lịch sử không khớp!"
