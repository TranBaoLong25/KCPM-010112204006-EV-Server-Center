import requests
import json
import os # Import os để tạo random bytes
from datetime import datetime, timedelta
from flask import current_app, jsonify
from app import db
from models.payment_model import PaymentTransaction, PAYMENT_STATUSES, VALID_PAYMENT_METHODS
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError # Import để bắt lỗi DB

class PaymentService:
    """Service xử lý logic nghiệp vụ về Thanh toán"""
    
    # --- Helper Internal API Caller (Giữ nguyên) ---
    @staticmethod
    def _call_internal_api(service_url, endpoint, method="GET", json_data=None):
        """Hàm nội bộ gọi Internal API của các service khác"""
        internal_token = current_app.config.get("INTERNAL_SERVICE_TOKEN")
        url = f"{service_url}{endpoint}"
        headers = {"X-Internal-Token": internal_token}
        
        if not service_url or not internal_token:
             return None, "Lỗi cấu hình Service URL hoặc Internal Token."

        try:
            response = requests.request(method, url, headers=headers, json=json_data) 

            if response.status_code == 200 or response.status_code == 201:
                return response.json(), None
            else:
                error_msg = response.json().get('error', f"Lỗi Service (HTTP {response.status_code})")
                return None, error_msg
        except requests.exceptions.RequestException as e:
            return None, f"Lỗi kết nối Service: {str(e)}"

    @staticmethod
    def _get_invoice_details(invoice_id):
        """Lấy chi tiết Invoice từ Finance Service"""
        finance_url = current_app.config.get("FINANCE_SERVICE_URL")
        return PaymentService._call_internal_api(finance_url, f"/internal/invoices/{invoice_id}")
    
    @staticmethod
    def _update_invoice_status(invoice_id, new_status):
        """Cập nhật trạng thái Invoice"""
        finance_url = current_app.config.get("FINANCE_SERVICE_URL")
        return PaymentService._call_internal_api(
            finance_url,
            f"/internal/invoices/{invoice_id}/status",
            "PUT",
            {"status": new_status}
        )

    @staticmethod
    def _update_booking_status(booking_id, new_status):
        """Cập nhật trạng thái Booking"""
        booking_url = current_app.config.get("BOOKING_SERVICE_URL")
        return PaymentService._call_internal_api(
            booking_url,
            f"/internal/bookings/items/{booking_id}/status",
            "PUT",
            {"status": new_status}
        )
    
    @staticmethod
    def _generate_mock_pg_data(invoice_id, amount, method):
        """Giả lập tạo dữ liệu cho Cổng Thanh toán (QR/Bank info)"""
        # Tạo ID duy nhất bằng random hex
        pg_id = f"PG_{method.upper()}_{invoice_id}_{int(amount)}_{os.urandom(4).hex()}"
        note = f"EV_TT_{invoice_id}"
        
        # Lấy cấu hình URL tĩnh (dù không khuyến khích cho thanh toán động, nhưng giữ lại cho test)
        custom_momo_url = current_app.config.get("MOMO_QR_CODE_URL")
        
        if method == "momo_qr":
            # 🎯 TẠO QR CODE ĐỘNG DỰA TRÊN THÔNG SỐ GIAO DỊCH

            # Chuỗi mã hóa (content) cần chứa thông tin động: amount, note, pg_id
            # Sử dụng format chuẩn: TYPE|AMOUNT|NOTE|PG_ID (hoặc format phù hợp với cổng TT)
            qr_content = f"MOMO|{note}|{amount}|{pg_id}"

            # Tạo URL hình ảnh QR Code từ QuickChart.io API (Kích thước 200x200)
            # QuickChart.io là dịch vụ miễn phí, ổn định hơn Google Charts
            import urllib.parse
            encoded_content = urllib.parse.quote(qr_content)
            qr_url = f"https://quickchart.io/qr?text={encoded_content}&size=200"

            # Chỉ dùng ảnh tĩnh khi URL tuyệt đối (http/https).
            # Path tương đối (/images/...) gây lỗi Postman/API — giữ QR động QuickChart.
            if custom_momo_url and custom_momo_url.startswith(("http://", "https://")):
                 import time
                 cache_buster = int(time.time())
                 qr_url = f"{custom_momo_url}?v={cache_buster}"
            elif custom_momo_url:
                 current_app.logger.warning(
                     f"MOMO_QR_CODE_URL '{custom_momo_url}' is relative; using dynamic QR instead."
                 )

            current_app.logger.info(f"🔍 Generated QR URL: {qr_url}")

            qr_data = {
                "qr_code_url": qr_url, 
                "payment_text": note,
                "amount": amount,
                "note": f"Thanh toan HD {invoice_id} cho EV Service Center",
                "pg_id": pg_id, # THÊM PG_ID VÀO DATA TRẢ VỀ CHO FE
                "test_code": f"SUCCESS_PG_{pg_id}" 
            }
            return pg_id, json.dumps(qr_data)
        
        elif method == "bank_transfer":
            bank_data = {
                "bank_name": "Techcombank",
                "account_name": "Trần Bảo Long",
                "account_number": "19072525585011",
                "amount": amount,
                "note": note,
                "pg_id": pg_id, # THÊM PG_ID VÀO DATA TRẢ VỀ CHO FE
                "test_code": f"SUCCESS_PG_{pg_id}"
            }
            return pg_id, json.dumps(bank_data)

        return None, None

    # --- Core Business Logic (Giữ nguyên logic tạo request) ---
    @staticmethod
    def create_payment_request(invoice_id, method, user_id, amount):
        """Bắt đầu tạo giao dịch thanh toán — validate đầy đủ trước khi ghi DB."""

        if method not in VALID_PAYMENT_METHODS:
            return None, "Phương thức thanh toán không hợp lệ. Chỉ hỗ trợ: momo_qr, bank_transfer."

        try:
            invoice_id = int(invoice_id)
            user_id = int(user_id)
            amount = float(amount)
        except (TypeError, ValueError):
            return None, "Dữ liệu invoice_id, user_id hoặc amount không hợp lệ."

        if amount <= 0:
            return None, "Số tiền thanh toán phải lớn hơn 0."

        invoice_data, invoice_error = PaymentService._get_invoice_details(invoice_id)
        if invoice_error or not invoice_data:
            return None, "Không tìm thấy hóa đơn hoặc không thể xác minh hóa đơn."

        invoice_status = invoice_data.get("status")
        if invoice_status == "paid":
            return None, "Hóa đơn này đã được thanh toán."
        if invoice_status == "canceled":
            return None, "Hóa đơn này đã bị hủy, không thể thanh toán."

        if str(invoice_data.get("user_id")) != str(user_id):
            return None, "User không khớp với chủ sở hữu hóa đơn."

        invoice_amount = float(invoice_data.get("total_amount") or 0)
        if abs(amount - invoice_amount) > 0.01:
            return None, "Số tiền thanh toán không khớp với tổng tiền hóa đơn."

        pending_tx = PaymentTransaction.query.filter_by(
            invoice_id=invoice_id,
            status="pending",
        ).first()
        if pending_tx:
            return None, "Đã có giao dịch đang chờ thanh toán cho hóa đơn này."

        pg_id, payment_data = PaymentService._generate_mock_pg_data(invoice_id, amount, method)
        
        if not pg_id:
             return None, "Phương thức thanh toán không hợp lệ."

        # 4. Tạo Payment Transaction trong DB
        new_transaction = PaymentTransaction(
            invoice_id=invoice_id,
            user_id=user_id,
            amount=amount,
            method=method,
            pg_transaction_id=pg_id,
            payment_data_json=payment_data
        )

        try:
            db.session.add(new_transaction)
            db.session.commit()
            return new_transaction.to_dict(), None # Trả về dictionary
        except IntegrityError:
            # Lỗi khi PG ID bị trùng (rất hiếm do có random hex)
            db.session.rollback()
            return None, "Lỗi: Đã có giao dịch đang chờ hoặc giao dịch trùng lặp."
        except Exception as e:
            # Bắt mọi lỗi khác và rollback, ngăn chặn worker crash
            current_app.logger.error(f"CRITICAL ERROR in PaymentService.create_payment_request: {str(e)}")
            db.session.rollback()
            return None, "Lỗi máy chủ nghiêm trọng khi tạo giao dịch."
            
    # --- History Functions (Giữ nguyên) ---
    @staticmethod
    def get_transaction_by_pg_id(pg_transaction_id):
        return PaymentTransaction.query.filter_by(pg_transaction_id=pg_transaction_id).first()

    @staticmethod
    def handle_pg_webhook(pg_transaction_id, final_status):
        """Xử lý Webhook giả lập từ Cổng Thanh toán"""

        # Thử tìm transaction bằng pg_transaction_id
        transaction = PaymentService.get_transaction_by_pg_id(pg_transaction_id)

        # Nếu không tìm thấy, thử với test_code (loại bỏ prefix SUCCESS_PG_)
        if not transaction and pg_transaction_id.startswith("SUCCESS_PG_"):
            actual_pg_id = pg_transaction_id.replace("SUCCESS_PG_", "", 1)
            transaction = PaymentService.get_transaction_by_pg_id(actual_pg_id)

        if not transaction:
            return None, "Không tìm thấy giao dịch với PG ID này."

        if transaction.status == 'success':
            return transaction, "Giao dịch đã được xử lý thành công trước đó."

        if final_status == "success" and transaction.status != "pending":
            return None, f"Không thể xác nhận thanh toán khi giao dịch đang ở trạng thái '{transaction.status}'."

        # Valid payment statuses defined in the model
        valid_statuses = ["pending", "success", "failed", "expired"]
        if final_status not in valid_statuses:
            return None, "Trạng thái webhook không hợp lệ."
            
        try:
            # 1. Cập nhật trạng thái giao dịch
            transaction.status = final_status
            db.session.commit()

            # 2. Nếu thành công, cập nhật trạng thái Invoice VÀ Booking VÀ GỬI NOTIFICATION
            if final_status == 'success':
                # Cập nhật trạng thái Invoice thành 'paid'
                _, error = PaymentService._update_invoice_status(transaction.invoice_id, 'paid')
                if error:
                    current_app.logger.error(f"Failed to update Invoice {transaction.invoice_id} status to 'paid': {error}")

                # Lấy thông tin Invoice để biết booking_id
                invoice_data, invoice_error = PaymentService._get_invoice_details(transaction.invoice_id)
                if not invoice_error and invoice_data:
                    booking_id = invoice_data.get('booking_id')
                    if booking_id:
                        # Cập nhật trạng thái Booking thành 'completed'
                        _, booking_error = PaymentService._update_booking_status(booking_id, 'completed')
                        if booking_error:
                            current_app.logger.error(f"Failed to update Booking {booking_id} status to 'completed': {booking_error}")
                        else:
                            current_app.logger.info(f"✅ Successfully updated Booking {booking_id} to 'completed' after payment success")
                    else:
                        current_app.logger.warning(f"Invoice {transaction.invoice_id} has no booking_id")
                else:
                    current_app.logger.error(f"Failed to get Invoice {transaction.invoice_id} details: {invoice_error}")

                # 🎯 BỔ SUNG: GỬI NOTIFICATION THANH TOÁN THÀNH CÔNG
                PaymentService._notify_payment_success(transaction) 
            
            # 3. Nếu thất bại/hết hạn, có thể gửi notification thất bại (tùy chọn)
            elif final_status in ('failed', 'expired'):
                PaymentService._notify_payment_failed(transaction)

            return transaction, None
        except Exception as e:
            db.session.rollback()
            return None, f"Lỗi khi xử lý webhook: {str(e)}"

    @staticmethod
    def get_history_by_user(user_id):
        """Lấy lịch sử giao dịch của User"""
        return PaymentTransaction.query.filter_by(user_id=int(user_id)).order_by(desc(PaymentTransaction.created_at)).all()
    
    @staticmethod
    def get_all_history():
        """Lấy tất cả lịch sử giao dịch (Admin)"""
        return PaymentTransaction.query.order_by(desc(PaymentTransaction.created_at)).all()
        
    @staticmethod
    def _notify_payment_success(payment):
        """Thông báo thanh toán thành công"""
        # Import từ cùng thư mục
        try:
            from services.notification_helper import NotificationHelper
        except ImportError:
            # Fallback: skip notification nếu không import được
            current_app.logger.warning("NotificationHelper not available, skipping notification")
            return False 
        
        # Dữ liệu cần thiết cho metadata
        payment_data = json.loads(payment.payment_data_json)
        
        return NotificationHelper.send_notification(
            user_id=payment.user_id,
            notification_type="payment",
            title="✅ Thanh toán thành công",
            message=f"Thanh toán {payment.amount:,.0f} VNĐ cho hóa đơn #{payment.invoice_id} đã được xử lý thành công.",
            channel="in_app",
            priority="high",
            related_entity_type="payment",
            related_entity_id=payment.id,
            metadata={
                "amount": payment.amount,
                "invoice_id": payment.invoice_id,
                "payment_method": payment.method, # Sửa: dùng payment.method
                "pg_id": payment.pg_transaction_id
            }
        )
    
    @staticmethod
    def _notify_payment_failed(payment):
        """Thông báo thanh toán thất bại"""
        try:
            from services.notification_helper import NotificationHelper
        except ImportError:
            current_app.logger.warning("NotificationHelper not available, skipping notification")
            return False 
        
        return NotificationHelper.send_notification(
            user_id=payment.user_id,
            notification_type="payment",
            title="❌ Thanh toán thất bại",
            message=f"Thanh toán {payment.amount:,.0f} VNĐ không thành công. Trạng thái: {payment.status}. Vui lòng thử lại hoặc liên hệ hỗ trợ.",
            channel="in_app",
            priority="high",
            related_entity_type="payment",
            related_entity_id=payment.id
        )
    
    # ⚠️ HÀM process_payment DƯ THỪA (Đã được thay thế bằng handle_pg_webhook)
    @staticmethod
    def process_payment(data):
        # Hàm này không cần thiết vì logic đã nằm trong handle_pg_webhook
        # Nếu muốn dùng lại, cần định nghĩa lại logic và loại bỏ dòng gọi notify ở cuối.
        
        # Giữ nguyên code cũ nhưng cảnh báo:
        current_app.logger.warning("PaymentService.process_payment called. This function is deprecated.")
        # ... existing payment processing code ...
        
        # Bỏ các dòng này (vì đã được thêm vào handle_pg_webhook)
        # if payment.status == "success": # type: ignore
        #     PaymentService._notify_payment_success(payment) # type: ignore
        # elif payment.status == "failed": # type: ignore
        #     PaymentService._notify_payment_failed(payment) # type: ignore

        # return payment, None # type: ignore
        
        # Thay thế bằng:
        return None, "Function deprecated."


    @staticmethod
    def expire_pending_transactions():
        """
        Tự động hủy các giao dịch pending quá 15 phút
        Được gọi định kỳ bởi scheduler
        """
        try:
            # Tính thời gian 15 phút trước
            fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)

            # Tìm tất cả giao dịch pending quá 1 phút
            expired_transactions = PaymentTransaction.query.filter(
                PaymentTransaction.status == 'pending',
                PaymentTransaction.created_at < expiration_time
            ).all()

            expired_count = 0
            for transaction in expired_transactions:
                # 1. Cập nhật trạng thái
                transaction.status = 'expired'
                
                # 2. Thông báo thất bại (Expired)
                PaymentService._notify_payment_failed(transaction) 
                
                expired_count += 1

            if expired_count > 0:
                db.session.commit()
                current_app.logger.info(f"✅ Đã hủy {expired_count} giao dịch quá hạn")

            return expired_count
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"❌ Lỗi khi hủy giao dịch quá hạn: {str(e)}")
            return 0