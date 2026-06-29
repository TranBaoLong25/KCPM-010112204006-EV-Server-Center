# Booking Service - Test Plan (Black-box / White-box)

## 1. Mục tiêu

Tài liệu này mô tả chiến lược kiểm thử black-box và white-box cho `booking-service`, bao gồm API tạo booking và logic nội bộ `BookingService`.

## 2. Phạm vi

- API public: `POST /booking`
- API public: `GET /booking/<id>`
- API internal: `POST /internal/booking/verify`
- Logic nội bộ: kiểm tra thời gian trùng lịch, xác thực `center_id`, trạng thái booking
- Tích hợp với User Service và Notification Helper

## 3. Black-box Test Scenarios

### 3.1. Tạo booking hợp lệ
- Input hợp lệ, `user_id` và thời gian booking không trùng.
- Kỳ vọng: trả về `201 Created`, booking được lưu.

### 3.2. Tạo booking với `service_type` rỗng
- Input: `service_type = ""`
- Kỳ vọng: `400 Bad Request` hoặc thông báo lỗi hợp lệ.

### 3.3. Tạo booking `start_time >= end_time`
- Input: `start_time` sau hoặc bằng `end_time`
- Kỳ vọng: `400 Bad Request`.

### 3.4. Tạo booking với `technician_id` hoặc `station_id` không hợp lệ
- Input: `technician_id = 0` hoặc `station_id = 0`
- Kỳ vọng: lỗi xác thực.

### 3.5. Tạo booking trùng lịch
- Input: same technician/station/center time overlap với booking hiện có.
- Kỳ vọng: `409 Conflict` hoặc lỗi không cho phép tạo.

### 3.6. Tạo booking với `center_id` không tồn tại
- Input: `center_id` lớn không tồn tại.
- Kỳ vọng: `400 Bad Request` hoặc lỗi xác thực chi nhánh.

### 3.7. Xem booking tồn tại
- Gọi `GET /booking/<id>` với id hợp lệ.
- Kỳ vọng: `200 OK` và trả về dữ liệu booking.

### 3.8. Xem booking không tồn tại
- Gọi `GET /booking/99999`.
- Kỳ vọng: `404 Not Found`.

### 3.9. Internal verify user
- Gọi `POST /internal/booking/verify` với token và `user_id` hợp lệ.
- Kỳ vọng: `200 OK` và xác thực thành công.

## 4. White-box Test Scenarios

### 4.1. Kiểm tra `BookingService.create_booking`
- Path 1: input hợp lệ, không trùng lịch, `center_id` tồn tại -> tạo booking.
- Path 2: `service_type` rỗng -> bỏ qua tạo, trả lỗi.
- Path 3: `start_time >= end_time` -> trả lỗi.
- Path 4: trùng lịch khi kiểm tra `is_time_available` -> trả lỗi.
- Path 5: `center_id` không tồn tại -> trả lỗi trước khi tạo.

### 4.2. Kiểm tra `BookingService.is_time_available`
- Booking mới không trùng với booking hiện có -> trả `True`.
- Booking mới trùng với booking hiện có về cùng `technician_id`/`station_id` -> trả `False`.
- Booking mới trùng theo cạnh biên (kết thúc đúng lúc booking khác bắt đầu) -> xét hợp lệ hoặc không trùng tùy định nghĩa.

### 4.3. Kiểm tra đoạn xác thực User Service
- Gọi nội bộ `User Service` giả lập hoặc mock response hợp lệ.
- Nếu User Service trả về `user_id` không tồn tại -> thất bại.

### 4.4. Kiểm tra `NotificationHelper` tích hợp (nếu có)
- Sau khi tạo booking, nếu notification helper được gọi thì kiểm tra lệnh gửi notification được kích hoạt.
- Mock notification helper để đảm bảo luồng `create_booking` trả về booking thành công nhưng không phụ thuộc vào hệ thống thông báo.

### 4.5. Kiểm tra xử lý trạng thái booking
- `status` mặc định phải là `pending` khi tạo.
- Nếu cập nhật trạng thái sang `confirmed`, `canceled`, `completed` thì luồng xử lý hợp lệ.

## 5. Marker đề xuất cho Pytest

- `@pytest.mark.blackbox` cho các test API public.
- `@pytest.mark.whitebox` cho các test logic `BookingService` và các helper nội bộ.

## 6. Commands chạy test

```powershell
cd services/booking-service
pytest -vv -m blackbox
pytest -vv -m whitebox
pytest -vv
```

## 7. Bằng chứng và hoàn thiện

- Lưu kết quả test vào file `booking-service/test_results.txt` sau khi chạy.
- Kèm thông tin `pytest -vv` và số lượng test passed.

## 8. Ghi chú

- Nếu cần tách riêng `booking-service/tests/conftest.py`, khuyến nghị dùng fixture tạo app Flask, DB memory, và mock `User Service`.
- Xây dựng testcase dựa trên giá trị biên trong `BOOKING_BVA.md` để đảm bảo bao phủ cả trường hợp hợp lệ và bất thường.
