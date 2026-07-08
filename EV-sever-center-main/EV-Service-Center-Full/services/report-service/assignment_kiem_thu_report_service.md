# Assignment: Kiểm thử chức năng Report Service

**Thời lượng:** 90 phút  
**Chủ đề:** Phân hoạch lớp tương đương, phân tích giá trị biên, thiết kế test case và kiểm thử API  
**Mức độ:** Cơ bản đến trung bình  
**Hình thức:** Cá nhân  
**Tổng điểm:** 10 điểm  

**Họ và tên:** Trần Anh Kiệt 
**MSSV:** 052205013377 
**Lớp:** CN2301E

---

# 1. Mục tiêu bài tập

1. Xác định điều kiện kiểm thử cho chức năng báo cáo trong Report Service.
2. Áp dụng kỹ thuật phân hoạch lớp tương đương cho token, role, query parameter ngày tháng và dữ liệu trả về từ service nội bộ.
3. Áp dụng kỹ thuật phân tích giá trị biên cho khoảng thời gian `start_date`, `end_date`.
4. Thiết kế test case cho API báo cáo doanh thu, báo cáo kho và dashboard tổng quan.
5. Ghi nhận đúng một lỗi thực tế khi kiểm thử bằng Postman: API báo cáo doanh thu trả `500 Internal Server Error`.
6. Tham chiếu toàn bộ thư mục `report-service` để phân tích nguyên nhân, tác động và đề xuất hướng khắc phục.

---

# 2. Nội dung tham khảo

Trong bài này em áp dụng các kỹ thuật kiểm thử sau:

* **Equivalence Partitioning:** chia dữ liệu đầu vào thành nhóm hợp lệ và không hợp lệ.
* **Boundary Value Analysis (BVA):** kiểm thử vùng biên của khoảng ngày báo cáo.
* **API Testing:** kiểm thử endpoint bằng Postman với Bearer Token.
* **Negative Testing:** kiểm thử lỗi kết nối hoặc dữ liệu trả về sai từ service nội bộ.
* **Unit Test:** dùng pytest và mock để kiểm tra logic xử lý báo cáo.
* **Integration Risk Analysis:** phân tích rủi ro khi Report Service phụ thuộc Payment, Inventory và Booking Service.

---

# 3. Mô tả bài toán

Hệ thống EV Service Center có **Report Service** dùng để tổng hợp dữ liệu từ các microservice khác và tạo báo cáo cho admin.

Report Service không có database/model riêng trong source hiện tại. Service này hoạt động như một tầng tổng hợp dữ liệu:

```text
Admin/Postman/Frontend
        |
        v
Report Service
        |
        +--> Payment Service: lấy giao dịch để tính doanh thu
        |
        +--> Inventory Service: lấy phụ tùng để tính tồn kho
        |
        +--> Booking Service: lấy booking để tạo dashboard
```

Các chức năng chính:

| Chức năng | Endpoint | Method | Mô tả |
| -------- | -------- | ------ | ----- |
| Báo cáo doanh thu | `/api/reports/revenue` | GET | Tổng hợp giao dịch thành công từ Payment Service |
| Báo cáo kho | `/api/reports/inventory` | GET | Tổng hợp tình trạng phụ tùng từ Inventory Service |
| Dashboard tổng quan | `/api/reports/dashboard` | GET | Tổng hợp doanh thu, kho và booking |
| Health check | `/health` | GET | Kiểm tra Report Service đang chạy |

Trong bài assignment này, lỗi thực tế chỉ tập trung vào endpoint:

```http
GET /api/reports/revenue
```

Lỗi từ ảnh Postman:

```http
HTTP/1.1 500 Internal Server Error
```

Body:

```json
{
  "error": "Lỗi kết nối Service: Expecting value: line 1 column 1 (char 0)"
}
```

---

# 4. Tham chiếu toàn bộ thư mục Report Service

Thư mục được kiểm thử:

```text
EV-Service-Center-Full/services/report-service
```

## 4.1 Cấu trúc thư mục

| Thành phần | File/thư mục | Vai trò |
| ---------- | ------------ | ------- |
| Flask app chính | `app.py` | Tạo Flask app, cấu hình JWT, internal token và URL các service liên quan |
| WSGI entrypoint | `wsgi.py` | Chạy service trên host `0.0.0.0`, port `8006` |
| Controller | `controllers/report_controller.py` | Định nghĩa endpoint `/api/reports/revenue`, `/inventory`, `/dashboard` |
| Service layer | `services/report_service.py` | Gọi internal API và xử lý dữ liệu báo cáo |
| Test fixture | `test/conftest.py` | Tạo app test, cấu hình token và service URL giả |
| Test chính | `test/test_report_service.py` | 22 unit test kiểm tra `_call_internal_api`, revenue, inventory, dashboard |
| Test demo fail | `test/test_report_service_fail.py` | 2 test cố tình fail để minh họa lỗi |
| Báo cáo sẵn có | `REPORT_SERVICE_REPORT.md` | Báo cáo kiểm thử tổng quan |
| Docker | `Dockerfile` | Cấu hình container |
| Dependencies | `requirements.txt` | Flask, JWT, requests, gunicorn |

## 4.2 Cấu hình môi trường

Các biến môi trường trong `app.py`:

| Biến môi trường | Mục đích |
| --------------- | -------- |
| `JWT_SECRET_KEY` | Xác thực Bearer Token |
| `INTERNAL_SERVICE_TOKEN` | Token nội bộ khi gọi service khác |
| `FINANCE_SERVICE_URL` | URL Finance Service, hiện chưa dùng trực tiếp trong report logic |
| `PAYMENT_SERVICE_URL` | URL Payment Service để lấy giao dịch |
| `INVENTORY_SERVICE_URL` | URL Inventory Service để lấy parts |
| `BOOKING_SERVICE_URL` | URL Booking Service để lấy booking |
| `MAINTENANCE_SERVICE_URL` | URL Maintenance Service, hiện chưa dùng trực tiếp trong report logic |

Nếu `PAYMENT_SERVICE_URL` hoặc `INTERNAL_SERVICE_TOKEN` bị thiếu/sai, báo cáo doanh thu sẽ không lấy được dữ liệu.

## 4.3 Luồng xử lý API báo cáo doanh thu

```text
GET /api/reports/revenue
        |
        v
report_controller.get_revenue_report()
        |
        v
ReportService.get_revenue_report(start_date, end_date)
        |
        v
ReportService._call_internal_api(PAYMENT_SERVICE_URL, "/internal/payments/all")
        |
        v
Payment Service trả danh sách transactions
        |
        v
Lọc status = "success"
        |
        v
Tính total_revenue, transaction_count, avg_transaction_value, payment_methods
```

## 4.4 Danh sách API thực tế

| STT | Method | Endpoint | Quyền | Service phụ thuộc | Expected |
| --- | ------ | -------- | ----- | ----------------- | -------- |
| 1 | GET | `/health` | Không yêu cầu token | Không | 200 |
| 2 | GET | `/api/reports/revenue` | Admin | Payment Service | 200 nếu Payment trả JSON hợp lệ |
| 3 | GET | `/api/reports/inventory` | Admin | Inventory Service | 200 nếu Inventory trả JSON hợp lệ |
| 4 | GET | `/api/reports/dashboard` | Admin | Payment, Inventory, Booking | 200 nếu các service trả dữ liệu hợp lệ hoặc fallback được |

---

# 5. Yêu cầu nghiệp vụ mong đợi

## 5.1 Quy tắc xác thực

Các endpoint `/api/reports/*` yêu cầu:

| Điều kiện | Expected |
| --------- | -------- |
| Có Bearer Token hợp lệ | Được kiểm tra tiếp role |
| Token có claim `role=admin` | Được truy cập báo cáo |
| Token role khác admin | 403 Forbidden |
| Không có token hoặc token sai | 401 Unauthorized |

## 5.2 Quy tắc báo cáo doanh thu

Endpoint:

```http
GET /api/reports/revenue?start_date=2026-07-01&end_date=2026-07-31
```

Điều kiện hợp lệ:

| Input | Miền giá trị hợp lệ |
| ----- | ------------------- |
| `start_date` | Có thể bỏ trống hoặc định dạng `YYYY-MM-DD` |
| `end_date` | Có thể bỏ trống hoặc định dạng `YYYY-MM-DD` |
| Payment data | JSON list các transaction |
| Transaction status | Chỉ tính transaction có `status = "success"` |
| `amount` | Số tiền, nếu thiếu thì tính `0` |
| `method` | Phương thức thanh toán, nếu thiếu thì tính `unknown` |
| `created_at` | ISO datetime để lọc theo ngày |

Kết quả mong đợi khi thành công:

```http
HTTP/1.1 200 OK
```

Ví dụ body:

```json
{
  "total_revenue": 300,
  "transaction_count": 2,
  "avg_transaction_value": 150,
  "payment_methods": {
    "cash": {
      "count": 1,
      "amount": 100
    },
    "card": {
      "count": 1,
      "amount": 200
    }
  },
  "period": {
    "start_date": "2026-07-01",
    "end_date": "2026-07-31"
  }
}
```

## 5.3 Quy tắc xử lý lỗi service nội bộ

Khi Payment Service lỗi, trả HTML, trả body rỗng hoặc trả dữ liệu không phải JSON, Report Service không nên crash. API nên trả lỗi rõ ràng:

```http
HTTP/1.1 502 Bad Gateway
```

Ví dụ body đề xuất:

```json
{
  "error": "Payment Service trả dữ liệu không hợp lệ hoặc không phải JSON"
}
```

Hiện tại source đang trả `500 Internal Server Error`, nên được ghi nhận là lỗi.

---

# PHẦN A. BÀI LÀM

---

## Câu 1. Phân hoạch lớp tương đương

### 1.1 Phân hoạch cho token và role

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| Bearer Token | Token hợp lệ, chưa hết hạn | V1 | Không có token | X1 |
| | | | Token sai định dạng | X2 |
| | | | Token hết hạn | X3 |
| Role | `admin` | V2 | `customer`, `technician`, role khác admin | X4 |

### 1.2 Phân hoạch cho khoảng thời gian báo cáo doanh thu

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| `start_date` | Bỏ trống hoặc `YYYY-MM-DD` | V3 | Sai định dạng, ví dụ `abc`, `2026-99-99` | X5 |
| `end_date` | Bỏ trống hoặc `YYYY-MM-DD` | V4 | Sai định dạng, ví dụ `abc`, `2026-99-99` | X6 |
| Khoảng ngày | `start_date <= end_date` | V5 | `start_date > end_date` | X7 |

### 1.3 Phân hoạch cho dữ liệu Payment Service

| Dữ liệu trả về từ Payment Service | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| --------------------------------- | ---------- | --- | ---------------- | --- |
| HTTP status | 200 hoặc 201 | V6 | 4xx, 5xx | X8 |
| Response body | JSON list transaction | V7 | Body rỗng | X9 |
| Response body | JSON parse được | V8 | HTML/text không phải JSON | X10 |
| Transaction | Có `status`, `amount`, `method`, `created_at` | V9 | Thiếu field, field sai kiểu | X11 |

### Nhận xét

Lỗi trong ảnh thuộc lớp không hợp lệ **X9 hoặc X10**: Payment Service hoặc gateway trả body rỗng/không phải JSON, làm `response.json()` phát sinh lỗi:

```text
Expecting value: line 1 column 1 (char 0)
```

---

## Câu 2. Phân tích giá trị biên

### 2.1 Giá trị biên cho ngày báo cáo

| Nhóm | Input | Ý nghĩa | Expected |
| ---- | ----- | ------- | -------- |
| Không truyền ngày | Không có `start_date`, `end_date` | Lấy toàn bộ giao dịch | 200 nếu Payment Service ổn |
| Cùng một ngày | `start_date=2026-07-01`, `end_date=2026-07-01` | Biên nhỏ nhất của khoảng hợp lệ | 200 |
| Ngày bắt đầu trước ngày kết thúc | `2026-07-01` đến `2026-07-31` | Khoảng hợp lệ | 200 |
| Ngày bắt đầu sau ngày kết thúc | `2026-07-31` đến `2026-07-01` | Khoảng không hợp lệ | 400 nếu có validate |
| Sai định dạng ngày | `start_date=abc` | Không parse được ISO date | 400 nếu có validate |
| End date chỉ có ngày | `end_date=2026-07-31` | Service thêm `T23:59:59` | 200 |

### 2.2 Giá trị biên cho dữ liệu giao dịch

| Nhóm | Input | Expected |
| ---- | ----- | -------- |
| Không có transaction | `[]` | 200, doanh thu bằng 0 |
| Không có transaction success | Chỉ có `status=failed` | 200, doanh thu bằng 0 |
| Một transaction success | 1 giao dịch hợp lệ | 200, tổng bằng amount |
| `amount=0` | Giao dịch success nhưng amount bằng 0 | 200, tổng không tăng |
| Thiếu `amount` | Không có field amount | 200, tính amount mặc định 0 |
| Body rỗng từ Payment | `""` | Hiện tại: 500, mong đợi: 502 hoặc lỗi rõ ràng |

---

## Câu 3. Thiết kế test case

### 3.1 Test case cho API doanh thu

| STT | Mã test case | Mô tả | Request/Input | Expected | Actual | Trạng thái |
| --: | ------------ | ----- | ------------- | -------- | ------ | ---------- |
| 1 | TC-REPORT-REV-01 | Admin lấy báo cáo doanh thu không truyền ngày | `GET /api/reports/revenue` | 200 nếu Payment Service trả JSON hợp lệ | Chưa ghi nhận | Not run |
| 2 | TC-REPORT-REV-02 | Admin lọc doanh thu theo khoảng ngày hợp lệ | `start_date=2026-07-01&end_date=2026-07-31` | 200 | Chưa ghi nhận | Not run |
| 3 | TC-REPORT-REV-03 | Không có token | Không truyền Authorization | 401 | Chưa ghi nhận | Not run |
| 4 | TC-REPORT-REV-04 | Token không phải admin | Token role customer/technician | 403 | Chưa ghi nhận | Not run |
| 5 | TC-REPORT-REV-05 | Payment Service trả dữ liệu rỗng/không phải JSON | `GET /api/reports/revenue` | 502 hoặc thông báo lỗi service rõ ràng | 500 Internal Server Error | Fail |

### 3.2 Test case cho Inventory Report

| STT | Mã test case | Mô tả | Request/Input | Expected |
| --: | ------------ | ----- | ------------- | -------- |
| 1 | TC-REPORT-INV-01 | Admin lấy báo cáo kho | `GET /api/reports/inventory` | 200 |
| 2 | TC-REPORT-INV-02 | Inventory rỗng | Inventory trả `[]` | 200, tổng bằng 0 |
| 3 | TC-REPORT-INV-03 | Có phụ tùng low stock | `quantity < 10` | 200, tăng `low_stock_count` |
| 4 | TC-REPORT-INV-04 | Có phụ tùng out of stock | `quantity = 0` | 200, tăng `out_of_stock_count` |
| 5 | TC-REPORT-INV-05 | Inventory Service lỗi | 4xx/5xx hoặc không JSON | Lỗi rõ ràng, không crash |

### 3.3 Test case cho Dashboard

| STT | Mã test case | Mô tả | Request/Input | Expected |
| --: | ------------ | ----- | ------------- | -------- |
| 1 | TC-REPORT-DASH-01 | Admin lấy dashboard | `GET /api/reports/dashboard` | 200 |
| 2 | TC-REPORT-DASH-02 | Revenue lỗi | Revenue trả `None` | Dashboard fallback doanh thu bằng 0 |
| 3 | TC-REPORT-DASH-03 | Inventory lỗi | Inventory trả `None` | Dashboard fallback tồn kho bằng 0 |
| 4 | TC-REPORT-DASH-04 | Booking rỗng | Booking trả `None` hoặc `[]` | Booking stats bằng 0 |

---

## Câu 4. Mô tả lỗi thực tế

## BUG-REPORT-01: API báo cáo doanh thu trả `500 Internal Server Error`

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-REPORT-01 |
| Chức năng | Báo cáo doanh thu theo khoảng thời gian |
| Method | GET |
| Endpoint được test | `/api/reports/revenue` |
| URL Postman | `http://localhost/api/reports/revenue` |
| Auth | Bearer Token |
| Kết quả thực tế | `500 Internal Server Error` |
| Body thực tế | `{"error": "Lỗi kết nối Service: Expecting value: line 1 column 1 (char 0)"}` |
| Kết quả mong đợi | 200 nếu Payment Service trả JSON hợp lệ, hoặc 502/503 nếu Payment Service lỗi |
| Mức độ nghiêm trọng | High |
| Trạng thái | Failed |

### Request trên Postman

```http
GET http://localhost/api/reports/revenue
Authorization: Bearer <admin_token>
```

### Kết quả thực tế

```http
HTTP/1.1 500 Internal Server Error
```

```json
{
  "error": "Lỗi kết nối Service: Expecting value: line 1 column 1 (char 0)"
}
```

### Kết quả mong đợi

Trường hợp Payment Service hoạt động đúng:

```http
HTTP/1.1 200 OK
```

Trường hợp Payment Service trả body rỗng hoặc không phải JSON:

```http
HTTP/1.1 502 Bad Gateway
```

Ví dụ body:

```json
{
  "error": "Payment Service trả dữ liệu không hợp lệ hoặc không phải JSON"
}
```

### Ảnh hưởng

* Admin không xem được báo cáo doanh thu.
* Frontend/dashboard không hiển thị được số liệu doanh thu.
* Lỗi `500` làm người dùng hiểu rằng Report Service bị crash.
* Thông báo lỗi kỹ thuật `Expecting value: line 1 column 1` khó hiểu với người dùng cuối.
* Việc tổng hợp dashboard có thể thiếu số liệu doanh thu nếu Payment Service trả dữ liệu sai.

---

## Câu 5. Phân tích nguyên nhân trong source code

File liên quan:

```text
EV-Service-Center-Full/services/report-service/controllers/report_controller.py
EV-Service-Center-Full/services/report-service/services/report_service.py
```

Route báo cáo doanh thu:

```python
@report_bp.route("/revenue", methods=["GET"])
@admin_required()
def get_revenue_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    report, error = ReportService.get_revenue_report(start_date, end_date)
    
    if error:
        return jsonify({"error": error}), 500
    
    return jsonify(report), 200
```

Hàm gọi internal API:

```python
response = requests.request(method, url, headers=headers, json=json_data, timeout=10)
if response.status_code in [200, 201]:
    return response.json(), None
else:
    error_msg = response.json().get('error', f"Lỗi Service (HTTP {response.status_code})")
    return None, error_msg
```

Nguyên nhân có khả năng cao:

1. `ReportService` gọi Payment Service tại:

```text
PAYMENT_SERVICE_URL + /internal/payments/all
```

2. Payment Service hoặc gateway trả về body rỗng, HTML, text hoặc dữ liệu không phải JSON.
3. Code gọi `response.json()` ngay mà chưa kiểm tra `Content-Type`, chưa kiểm tra body rỗng và chưa bắt riêng lỗi parse JSON.
4. Lỗi parse JSON tạo message:

```text
Expecting value: line 1 column 1 (char 0)
```

5. `get_revenue_report()` nhận `error` và controller trả về:

```python
return jsonify({"error": error}), 500
```

Vì vậy API trả `500 Internal Server Error`.

### Nhận xét kỹ thuật

Lỗi này là lỗi tích hợp giữa Report Service và Payment Service. Report Service không nên để lỗi parse JSON thô đi thẳng ra response. Nên phân biệt:

| Tình huống | Status nên trả |
| ---------- | -------------- |
| User thiếu token | 401 |
| User không phải admin | 403 |
| Query date sai | 400 |
| Payment Service không kết nối được | 503 |
| Payment Service trả non-JSON/empty body | 502 |
| Bug nội bộ không lường trước | 500 |

---

## Câu 6. Đề xuất hướng khắc phục

## Hướng 1: Bắt lỗi JSON rõ ràng trong `_call_internal_api`

Đề xuất sửa:

```python
try:
    response = requests.request(method, url, headers=headers, json=json_data, timeout=10)
except requests.exceptions.RequestException as e:
    return None, f"Lỗi kết nối Service: {str(e)}"

try:
    payload = response.json()
except ValueError:
    return None, "Service trả dữ liệu không hợp lệ hoặc không phải JSON"

if response.status_code in [200, 201]:
    return payload, None

return None, payload.get("error", f"Lỗi Service (HTTP {response.status_code})")
```

Ưu điểm:

* Không để lỗi `Expecting value` lộ ra ngoài.
* Phân biệt lỗi kết nối và lỗi dữ liệu.
* Dễ viết unit test.

## Hướng 2: Trả status code phù hợp ở controller

Hiện controller luôn trả `500` khi service layer có lỗi:

```python
if error:
    return jsonify({"error": error}), 500
```

Nên đổi theo loại lỗi:

```python
if error:
    status_code = 503 if "kết nối" in error else 502
    return jsonify({"error": error}), status_code
```

Hoặc service layer trả thêm `status_code` để controller không phải đoán theo chuỗi.

## Hướng 3: Kiểm tra đúng endpoint internal của Payment Service

Cần xác nhận Payment Service có hỗ trợ endpoint:

```text
GET /internal/payments/all
```

và response phải là JSON list:

```json
[
  {
    "status": "success",
    "amount": 100,
    "method": "cash",
    "created_at": "2026-07-01T10:00:00"
  }
]
```

Nếu endpoint sai hoặc Payment Service trả HTML 404, Report Service sẽ gặp lỗi parse JSON.

### Hướng đề xuất

Nên kết hợp cả 3 hướng:

1. Kiểm tra lại `PAYMENT_SERVICE_URL` và endpoint `/internal/payments/all`.
2. Bắt lỗi JSON rõ ràng trong `_call_internal_api`.
3. Trả `502/503` thay vì `500` cho lỗi từ service phụ thuộc.

---

## Câu 7. Thiết kế kiểm thử tự động

### 7.1 Unit test tái hiện lỗi Payment trả body rỗng

```python
from unittest.mock import patch, MagicMock
from services.report_service import ReportService


@patch("services.report_service.requests.request")
def test_call_internal_api_empty_body_should_return_readable_error(mock_request, app_context):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Expecting value: line 1 column 1 (char 0)")
    mock_request.return_value = mock_response

    data, error = ReportService._call_internal_api(
        "http://payment-service",
        "/internal/payments/all"
    )

    assert data is None
    assert "không phải JSON" in error or "không hợp lệ" in error
```

### 7.2 Unit test cho revenue khi Payment Service lỗi

```python
from unittest.mock import patch
from services.report_service import ReportService


@patch("services.report_service.ReportService._call_internal_api")
def test_get_revenue_report_payment_non_json_should_return_error(mock_call, app_context):
    mock_call.return_value = (None, "Payment Service trả dữ liệu không hợp lệ hoặc không phải JSON")

    report, error = ReportService.get_revenue_report()

    assert report is None
    assert "Payment Service" in error
```

### 7.3 API test cho controller

```python
from unittest.mock import patch


@patch("controllers.report_controller.ReportService.get_revenue_report")
def test_revenue_api_payment_error_should_not_return_raw_500(mock_report, client, admin_headers):
    mock_report.return_value = (None, "Payment Service trả dữ liệu không hợp lệ hoặc không phải JSON")

    response = client.get(
        "/api/reports/revenue",
        headers=admin_headers
    )

    assert response.status_code in [502, 503]
    assert "Payment Service" in response.get_json()["error"]
```

---

## Câu 8. Kịch bản kiểm thử Postman

### 8.1 Chuẩn bị

1. Chạy Report Service.
2. Chạy hoặc kiểm tra Payment Service.
3. Đăng nhập bằng tài khoản admin.
4. Copy access token.
5. Trong Postman chọn **Authorization**.
6. Chọn **Bearer Token**.
7. Dán token admin vào ô Token.

### 8.2 Test case: Revenue Report bị lỗi 500

Request:

```http
GET http://localhost/api/reports/revenue
Authorization: Bearer <admin_token>
```

Expected:

```text
Status: 200 OK nếu Payment Service trả JSON hợp lệ
```

Hoặc nếu Payment Service lỗi:

```text
Status: 502 Bad Gateway hoặc 503 Service Unavailable
Body có message dễ hiểu
```

Actual theo ảnh:

```text
Status: 500 Internal Server Error
```

Body:

```json
{
  "error": "Lỗi kết nối Service: Expecting value: line 1 column 1 (char 0)"
}
```

Đánh giá:

```text
Fail
```

---

# PHẦN B. KẾT QUẢ KIỂM THỬ

## 1. Tổng hợp kết quả Postman

| Tổng số lỗi thực tế ghi nhận | Pass | Fail |
| ---------------------------- | ---- | ---- |
| 1 | 0 | 1 |

## 2. Danh sách lỗi fail

| Mã lỗi | Endpoint | Expected | Actual |
| ------ | -------- | -------- | ------ |
| BUG-REPORT-01 | `GET /api/reports/revenue` | 200 nếu Payment trả JSON hợp lệ, hoặc 502/503 nếu Payment lỗi | 500 Internal Server Error |

## 3. Kết quả pytest hiện tại

Lệnh chạy test chính:

```bash
python -m pytest -q test/test_report_service.py
```

Kết quả:

```text
22 passed, 1 warning
```

Lệnh chạy toàn bộ test:

```bash
python -m pytest -q
```

Kết quả:

```text
24 tests
22 passed
2 failed
```

Hai test fail nằm trong:

```text
test/test_report_service_fail.py
```

Đây là các test demo cố tình sai expected:

| Test | Lý do fail |
| ---- | ---------- |
| `test_demo_fail_total_revenue` | Mock amount là 100 nhưng assert expected 200 |
| `test_demo_fail_inventory` | Mock 1 part nhưng assert expected total_parts = 5 |

Hai test demo này không phải lỗi nghiệp vụ của Report Service. Lỗi nghiệp vụ chính của assignment vẫn chỉ là `BUG-REPORT-01`.

## 4. Cảnh báo khi chạy test

Pytest có cảnh báo không ghi được `.pytest_cache`:

```text
PytestCacheWarning: could not create cache path ... Access is denied
```

Cảnh báo này liên quan quyền ghi cache trong môi trường test, không ảnh hưởng kết quả logic test.

---

# PHẦN C. BỔ SUNG THAM CHIẾU TOÀN BỘ REPORT SERVICE

## C1. Vai trò từng file trong kiểm thử

| File | Nội dung cần kiểm thử |
| ---- | --------------------- |
| `app.py` | Cấu hình JWT, internal token và service URL |
| `wsgi.py` | Cổng chạy service `8006` |
| `controllers/report_controller.py` | Auth admin, route revenue/inventory/dashboard, status code khi lỗi |
| `services/report_service.py` | Logic gọi internal API, parse JSON, tính toán báo cáo |
| `test/conftest.py` | Fixture app, client, app_context và config service URL |
| `test/test_report_service.py` | Unit test chính, 22 test pass |
| `test/test_report_service_fail.py` | Demo fail, không nên tính là lỗi sản phẩm |
| `REPORT_SERVICE_REPORT.md` | Báo cáo tổng quan, có thể dùng làm tài liệu tham khảo |

## C2. Ma trận phụ thuộc service

| Report API | Service phụ thuộc | Internal endpoint | Rủi ro |
| ---------- | ----------------- | ----------------- | ------ |
| `/api/reports/revenue` | Payment Service | `/internal/payments/all` | Endpoint sai, service chưa chạy, trả HTML/body rỗng |
| `/api/reports/inventory` | Inventory Service | `/internal/parts/all` | Không có endpoint, trả sai schema |
| `/api/reports/dashboard` | Payment, Inventory, Booking | `/internal/payments/all`, `/internal/parts/all`, `/internal/bookings/all` | Một service lỗi làm thiếu dữ liệu dashboard |

## C3. Ma trận phân quyền

| Endpoint | Không token | Token user thường | Token admin |
| -------- | ----------- | ----------------- | ----------- |
| `/api/reports/revenue` | 401 | 403 | 200 hoặc lỗi service phụ thuộc |
| `/api/reports/inventory` | 401 | 403 | 200 hoặc lỗi service phụ thuộc |
| `/api/reports/dashboard` | 401 | 403 | 200 hoặc fallback dữ liệu |
| `/health` | 200 | 200 | 200 |

## C4. White-box coverage cần có

| Hàm | Nhánh cần kiểm thử |
| --- | ------------------ |
| `_call_internal_api` | Thiếu config, HTTP 200, HTTP 201, HTTP lỗi, request exception, JSONDecodeError |
| `get_revenue_report` | API lỗi, không có transaction success, có success, lọc ngày, thống kê method, thiếu amount |
| `get_inventory_report` | API lỗi, kho rỗng, kho bình thường, low stock, out of stock, thiếu quantity/price |
| `get_dashboard_overview` | Thành công, không có booking, revenue None, inventory None, booking nhiều trạng thái |

## C5. Checklist hoàn thiện kiểm thử

| Hạng mục | Trạng thái |
| -------- | ---------- |
| Đọc toàn bộ source report-service | Hoàn thành |
| Lập danh sách endpoint thực tế | Hoàn thành |
| Ghi nhận lỗi Postman `500` của revenue report | Hoàn thành |
| Phân tích nguyên nhân từ `_call_internal_api` | Hoàn thành |
| Chạy test chính `test_report_service.py` | Hoàn thành, 22 pass |
| Chạy toàn bộ test | Hoàn thành, 22 pass / 2 demo fail |
| Bổ sung test cho body rỗng/non-JSON | Cần thực hiện |
| Đổi status lỗi service phụ thuộc từ 500 sang 502/503 | Cần thực hiện |
| Kiểm tra endpoint Payment Service `/internal/payments/all` | Cần thực hiện |
| Xuất coverage HTML sau khi sửa | Cần thực hiện |

---

# PHẦN D. KẾT LUẬN

Qua bài kiểm thử Report Service, em đã áp dụng được các kỹ thuật phân hoạch lớp tương đương, phân tích giá trị biên, thiết kế test case, kiểm thử API bằng Postman và phân tích lỗi dựa trên source code.

Report Service là service tổng hợp dữ liệu, không có database riêng trong source hiện tại. Các API báo cáo phụ thuộc nhiều vào dữ liệu trả về từ Payment, Inventory và Booking Service. Vì vậy, chất lượng của Report Service không chỉ phụ thuộc logic tính toán nội bộ mà còn phụ thuộc khả năng xử lý lỗi khi service khác trả dữ liệu sai.

Lỗi thực tế được ghi nhận trong bài là:

```text
BUG-REPORT-01: GET /api/reports/revenue trả 500 Internal Server Error
```

Nguyên nhân có khả năng cao là Payment Service hoặc gateway trả body rỗng/không phải JSON, trong khi `ReportService._call_internal_api()` gọi `response.json()` trực tiếp và controller đang chuyển mọi lỗi service thành `500`.

Để khắc phục, cần kiểm tra lại `PAYMENT_SERVICE_URL`, endpoint `/internal/payments/all`, bổ sung xử lý lỗi JSON trong `_call_internal_api()` và trả status code phù hợp hơn như `502 Bad Gateway` hoặc `503 Service Unavailable`. Sau khi sửa, cần chạy lại:

```bash
python -m pytest -q test/test_report_service.py
python -m pytest --cov=. --cov-report=html
```

Khi API revenue không còn trả lỗi `500` thô và các test case xử lý body rỗng/non-JSON đều pass, Report Service sẽ ổn định hơn cho chức năng báo cáo doanh thu và dashboard tổng quan.
