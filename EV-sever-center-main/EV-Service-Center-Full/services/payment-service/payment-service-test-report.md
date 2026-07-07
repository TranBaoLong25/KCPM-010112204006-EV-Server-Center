# BÁO CÁO KIỂM THỬ PAYMENT SERVICE

## Dự án: EV Service Center Maintenance Management System

---

# 1. Giới thiệu

## 1.1 Mục tiêu

Kiểm thử Payment Service nhằm:

- Đảm bảo chức năng tạo giao dịch thanh toán (MoMo QR, Bank Transfer) hoạt động đúng yêu cầu.
- Đảm bảo cơ chế xác thực nội bộ (Internal Token) giữa các service hoạt động chính xác.
- Phát hiện lỗi dữ liệu đầu vào khi tạo giao dịch (invoice_id, user_id, amount, method).
- Đảm bảo Webhook xử lý kết quả thanh toán từ Cổng thanh toán (PG) chính xác và idempotent.
- Đảm bảo phân quyền giữa User và Admin khi truy vấn lịch sử giao dịch.
- Đánh giá chất lượng mã nguồn và độ ổn định của hệ thống.

---

## 1.2 Phạm vi kiểm thử

Các chức năng được kiểm thử:

- Tạo giao dịch thanh toán (Create Payment Request)
- Xử lý Webhook từ Cổng thanh toán (PG Webhook)
- Xem lịch sử giao dịch cá nhân (User)
- Xem toàn bộ lịch sử giao dịch (Admin)
- API nội bộ: Lấy toàn bộ giao dịch, Lấy danh sách giao dịch sắp đến hạn (cho notification-service)

---

# 2. Môi trường kiểm thử

| Thành phần       | Công nghệ      |
| ---------------- | -------------- |
| Backend          | Python Flask   |
| Database         | PostgreSQL     |
| API Testing      | Postman        |
| Unit Testing     | pytest         |
| Coverage         | pytest-cov     |
| Frontend Testing | Playwright     |
| CI/CD            | GitHub Actions |
| Version Control  | Git + GitHub   |

---

# 3. Danh sách API kiểm thử

| STT | API                            | Method | Mô tả                                             |
| --- | ------------------------------- | ------ | -------------------------------------------------- |
| 1   | /api/payments/create             | POST   | Tạo giao dịch thanh toán (chỉ Finance Service)      |
| 2   | /api/payments/webhook            | POST   | Nhận webhook kết quả thanh toán từ Cổng thanh toán  |
| 3   | /api/payments/history/my         | GET    | Lấy lịch sử giao dịch của User (JWT)                |
| 4   | /api/payments/history/all        | GET    | Lấy toàn bộ lịch sử giao dịch (Admin)               |
| 5   | /internal/payments/all           | GET    | Lấy toàn bộ giao dịch (cho report-service)          |
| 6   | /internal/payments/due-soon      | GET    | Lấy danh sách giao dịch sắp đến hạn (notification)  |

---

# 4. Black-box Testing

## 4.1 Phân hoạch lớp tương đương (Equivalence Partitioning)

### Create Payment Request

#### Internal Token

Lớp hợp lệ:

- X-Internal-Token đúng với cấu hình hệ thống

Lớp không hợp lệ:

- Thiếu X-Internal-Token
- X-Internal-Token sai

#### Invoice ID

Lớp hợp lệ:

- invoice_id tồn tại, thuộc về đúng user, chưa thanh toán

Lớp không hợp lệ:

- invoice_id = 0 hoặc âm
- invoice_id không tồn tại
- invoice_id đã ở trạng thái "paid" hoặc "canceled"

#### User ID

Lớp hợp lệ:

- user_id tồn tại và khớp với chủ sở hữu hóa đơn

Lớp không hợp lệ:

- user_id = 0 hoặc âm
- user_id không khớp với chủ sở hữu hóa đơn

#### Amount

Lớp hợp lệ:

- amount > 0 và khớp với tổng tiền hóa đơn (invoice.total_amount)

Lớp không hợp lệ:

- amount <= 0
- amount không khớp với tổng tiền hóa đơn

#### Phương thức thanh toán (method)

Lớp hợp lệ:

- momo_qr
- bank_transfer

Lớp không hợp lệ:

- Giá trị khác momo_qr / bank_transfer
- Rỗng

---

### PG Webhook

Lớp hợp lệ:

- pg_transaction_id tồn tại trong hệ thống
- status thuộc {pending, success, failed, expired}
- Giao dịch đang ở trạng thái "pending" khi xác nhận "success"

Lớp không hợp lệ:

- pg_transaction_id không tồn tại
- Thiếu pg_transaction_id hoặc status
- status không hợp lệ (ngoài danh sách cho phép)
- Xác nhận "success" khi giao dịch không ở trạng thái pending

---

### Payment History

Lớp hợp lệ:

- User có JWT hợp lệ xem lịch sử của chính mình
- Admin có JWT với role admin xem toàn bộ lịch sử

Lớp không hợp lệ:

- Không có token (401)
- User thường (role != admin) truy cập route Admin (403)

---

# 4.2 Boundary Value Analysis (BVA)

## Create Payment Request (/api/payments/create)

### Internal Token

| Test Case        | Input                               | Expected |
| --------------   | ----------------------------------- | -------- |
| EP-PAY-CREATE-03 | Thiếu X-Internal-Token              | 401      |
| EP-PAY-CREATE-04 | X-Internal-Token không hợp lệ       | 401      |

### Invoice ID

| Test Case         | Input                                   | Expected |
| ----------------- | --------------------------------------- | -------- |
| BVA-PAY-CREATE-05 | invoice_id = 0 (Biên dưới)              | 400      |
| BVA-PAY-CREATE-06 | invoice_id = -1 (Giá trị âm)            | 400      |
| EP-PAY-CREATE-07  | invoice_id không tồn tại                | 400      |
| EP-PAY-CREATE-17  | Hóa đơn đã được thanh toán trước đó     | 400      |

### User ID

| Test Case         | Input                                      | Expected |
| ----------------- | ------------------------------------------ | -------- |
| BVA-PAY-CREATE-08 | user_id = 0 (Biên dưới)                    | 400      |
| BVA-PAY-CREATE-09 | user_id = -1 (Giá trị âm)                  | 400      |
| EP-PAY-CREATE-10  | user_id không khớp với chủ sở hữu hóa đơn  | 400      |

### Amount

| Test Case         | Input                                       | Expected |
| ----------------- | ------------------------------------------  | -------- |
| BVA-PAY-CREATE-11 | amount = -1 (Số tiền âm)                    | 400      |
| BVA-PAY-CREATE-12 | amount = 0 (Biên dưới)                      | 400      |
| BVA-PAY-CREATE-13 | amount = 0.01 (Biên dương nhỏ nhất)         | 400      |
| EP-PAY-CREATE-14  | amount không khớp tổng tiền hóa đơn         | 400      |

### Phương thức thanh toán (method)

| Test Case        | Input                               | Expected     |
| ---------------- | ----------------------------------- | ------------ |
| EP-PAY-CREATE-01 | momo_qr (Token hợp lệ)              | 201          |
| EP-PAY-CREATE-02 | bank_transfer (Token hợp lệ)        | 201          |
| EP-PAY-CREATE-15 | Phương thức thanh toán không hợp lệ | 400          |
| EP-PAY-CREATE-16 | Phương thức thanh toán rỗng         | 400          |

---

## PG Webhook (/api/payments/webhook)

| Test Case           | Input                                                  | Expected     |
| --------------------| -----------------------------------------------------  | ------------ |
| EP-PAY-WEBHOOK-01   | Webhook báo thành công hợp lệ (pg_transaction_id động) | 200 hoặc 400 |
| EP-PAY-WEBHOOK-02   | Webhook với pg_transaction_id không tồn tại            | 400          |
| EP-PAY-WEBHOOK-03   | Webhook với status không hợp lệ                        | 400          |
| BVA-PAY-WEBHOOK-04  | Webhook thiếu pg_transaction_id (Biên rỗng)            | 400          |
| BVA-PAY-WEBHOOK-05  | Webhook thiếu status (Biên rỗng)                       | 400          |

---

## Payment History

| Test Case           | Input                                               | Expected |
| --------------------| --------------------------------------------------- | ------ |
| EP-PAY-HISTORY-01   | Lấy lịch sử giao dịch cá nhân - Có JWT token hợp lệ | 200    |
| EP-PAY-HISTORY-02   | Lấy lịch sử giao dịch cá nhân - Không có token      | 401    |
| EP-PAY-HISTORY-03   | Admin xem toàn bộ lịch sử - Token Admin hợp lệ      | 200    |
| EP-PAY-HISTORY-04   | Nhân viên xem toàn bộ lịch sử - Token Staff (Không phải Admin) | 403 |

---

# 4.3 Kết quả thực thi Black-box (Postman)

Bộ test Postman "[Payment-service] - BVA & Equivalence" đã được chạy với các bước Setup (đăng nhập Admin, đăng nhập Staff/User, chuẩn bị Internal Token, lấy hóa đơn thật từ DB) trước khi thực thi các test case chính.

| Nhóm chức năng       | Số test case  | Pass | Fail |
| -------------------- | ------------- | ---- | ---- |
| Setup                | 4             | 4    | 0    |
| Create Payment       | 17            | 17   | 0    |
| PG Webhook           | 5             | 0    | 5    |
| Payment History      | 4             | 4    | 0    |

**Ghi chú lỗi phát hiện (PG Webhook):**

- Toàn bộ 5 test case của nhóm Webhook đều **FAIL**. Nguyên nhân: API `/api/payments/webhook` hiện đang áp dụng luôn cơ chế xác thực Internal Token giống route `/api/payments/create`, nên mọi request (kể cả hợp lệ hoặc thiếu dữ liệu) đều trả về **401 Unauthorized** thay vì **200/400** như kỳ vọng.
- Cụ thể: Webhook báo thành công hợp lệ trả về 401 (kỳ vọng 200 hoặc 400); webhook với `pg_transaction_id` không tồn tại trả về 401 kèm thông báo "Unauthorized internal request" thay vì thông báo nghiệp vụ "Không tìm thấy giao dịch với PG ID này"; webhook với status không hợp lệ và các trường hợp thiếu `pg_transaction_id`/`status` cũng đều bị chặn ở tầng xác thực trước khi vào logic nghiệp vụ.
- Đây là lỗi cấu hình/middleware cần được đội phát triển kiểm tra lại, do route `/api/payments/webhook` (được Cổng thanh toán bên ngoài gọi vào) không nên yêu cầu `X-Internal-Token` giống các API nội bộ giữa các service.

---

# 5. White-box Testing

Công cụ:

- pytest
- unittest.mock

Thư mục:

services/payment-service/tests/


---

# 6. Frontend Testing

Công cụ:

- Playwright

Các kịch bản kiểm thử:

- FE-PAYMENT-01: Mở trang thanh toán
- FE-PAYMENT-02: Hiển thị thông tin thanh toán
- FE-PAYMENT-03: Hiển thị phương thức thanh toán
- FE-PAYMENT-04: Không cho thanh toán khi thiếu dữ liệu
- FE-PAYMENT-05: Hiển thị lịch sử thanh toán

---

# 7. Coverage Testing

Lệnh thực hiện:

```bash
pytest --cov=. --cov-report=html
```

Kết quả:

- Sinh file `.coverage`
- Sinh thư mục `htmlcov`
- Hiển thị tỷ lệ bao phủ mã nguồn của Payment Service.

Mục đích:

- Đánh giá mức độ các đoạn mã đã được kiểm thử.
- Xác định những phần chưa được test (ví dụ: hàm `process_payment` đã lỗi thời, các nhánh gửi notification).

---

# 8. CI/CD

Công cụ:

- GitHub Actions

Workflow:

Push Code
↓
Install Dependencies
↓
Run pytest
↓
Run Coverage
↓
Build thành công

File cấu hình:

.github/workflows/payment-service-ci.yml

---

# 9. Kết luận

Nhóm đã thực hiện:

✓ Black-box Testing  
✓ Equivalence Partitioning  
✓ Boundary Value Analysis  
✓ White-box Testing  
✓ Coverage Testing  
✓ Frontend Testing bằng Playwright  
✓ CI/CD bằng GitHub Actions

Kết quả kiểm thử cho thấy phần lớn chức năng của Payment Service (tạo giao dịch, phân quyền lịch sử giao dịch) hoạt động đúng yêu cầu, xử lý được dữ liệu hợp lệ và không hợp lệ. Tuy nhiên, nhóm đã phát hiện **lỗi nghiêm trọng ở chức năng Webhook** (`/api/payments/webhook`): route này đang bị áp dụng nhầm cơ chế xác thực Internal Token dành cho giao tiếp nội bộ giữa các service, khiến Cổng thanh toán bên ngoài không thể gọi webhook thành công (luôn trả về 401 Unauthorized). Cần đội phát triển khắc phục trước khi triển khai lên môi trường production.
