# Notification Service Test Plan

## 1. Tổng quan
Tài liệu này mô tả:
- kiểm thử hộp đen (black-box testing)
- kiểm thử hộp trắng (white-box testing)

Phần kiểm thử tập trung vào API nội bộ `/internal/notifications/create` và dịch vụ `NotificationService.create_notification`.

## 2. Black-box Testing (Kiểm thử hộp đen)

### Mục tiêu
Kiểm thử hành vi bên ngoài của dịch vụ mà không cần biết chi tiết cài đặt bên trong.

### Đối tượng kiểm thử
- `POST /internal/notifications/create`
- logic validation đầu vào của payload
- phản hồi HTTP và mã trạng thái
- trạng thái thông báo trong cơ sở dữ liệu

### Kịch bản kiểm thử

| STT | Mô tả | Payload | Expected | Type |
|---|---|---|---|---|
| 1 | Tạo notification hợp lệ | `user_id`, `title`, `message`, `notification_type=system`, `channel=email`, `priority=medium` | `201 Created` + notification object | Valid |
| 2 | Thiếu `user_id` | no `user_id` | `400 Bad Request` + error message missing field | Invalid |
| 3 | Header nội bộ thiếu token | valid payload nhưng không có `X-Internal-Token` | `401 Unauthorized` | Invalid |
| 4 | `scheduled_at` hợp lệ | payload với `scheduled_at=2026-07-01T09:00:00` | `201 Created`, `notification.scheduled_at` not null, status pending | Valid |
| 5 | `notification_type` không hợp lệ | invalid enum | `400 Bad Request` + error message | Invalid |

### Bằng chứng test pass
File `test_results.txt` đã lưu đầu ra `pytest` với kết quả:
- `5 passed in 1.67s`

## 3. White-box Testing (Kiểm thử hộp trắng)

### Mục tiêu
Kiểm thử các nhánh, điều kiện và logic nội bộ của hàm `NotificationService.create_notification`.

### Coverages cần đạt
- kiểm tra điều kiện bắt buộc `user_id`, `title`, `message`
- validation độ dài `title`
- validation `message` không rỗng
- enum hợp lệ cho `notification_type`, `channel`, `priority`
- xử lý `scheduled_at` đúng ISO format
- nhánh auto-send khi không truyền `scheduled_at`

### Đường dẫn logic

| STT | Condition | Code path | Test case |
|---|---|---|---|
| 1 | missing required field | `if not all(k in data...)` | `test_create_notification_missing_user_id` |
| 2 | invalid title length | `len(data['title']) > 255` | `test_create_notification_title_too_long` |
| 3 | invalid enum `notification_type` | `notification_type not in valid_types` | `test_create_notification_invalid_notification_type` |
| 4 | invalid enum `channel` | `channel not in valid_channels` | `test_create_notification_invalid_channel` |
| 5 | scheduled notification | `scheduled_at = datetime.fromisoformat(...)` and no auto-send | `test_create_notification_scheduled_at_valid` |
| 6 | normal send notification | no `scheduled_at` -> `_send_notification` sets status sent | `test_create_notification_valid` |

### Cải tiến white-box

Nếu mở rộng, có thể bổ sung thêm:
- test `priority` không hợp lệ
- test `message` trống
- test trường `extra_data` nhận dict hoặc JSON string

## 4. Kết luận

Hiện tại bộ test đã bao phủ:
- 5 test case pass
- cả hai dạng kiểm thử: black-box và white-box
- logic validation chính của `NotificationService.create_notification`

File test hiện tại:
- `tests/conftest.py`
- `tests/test_notification_service.py`

Kết quả kiểm thử đã lưu bằng chứng trong `test_results.txt`.

## 5. Các lệnh thử nghiệm đã sử dụng

### Cài thư viện cần thiết
```powershell
C:/Users/ADMIN/AppData/Local/Programs/Python/Python313/python.exe -m pip install Flask==2.3.3 Flask-SQLAlchemy==3.1.1 Flask-Migrate==4.0.7 python-dotenv==1.0.1 gunicorn==21.2.0 Flask-Cors==4.0.1 Flask-JWT-Extended==4.6.0 requests==2.31.0 redis==5.0.1 APScheduler==3.10.4
```

### Chạy test trực tiếp
```powershell
C:/Users/ADMIN/AppData/Local/Programs/Python/Python313/python.exe -m pytest -q tests
```

### Chạy nhóm kiểm thử black-box
```powershell
C:/Users/ADMIN/AppData/Local/Programs/Python/Python313/python.exe -m pytest -q tests -m blackbox
```

### Chạy nhóm kiểm thử white-box
```powershell
C:/Users/ADMIN/AppData/Local/Programs/Python/Python313/python.exe -m pytest -q tests -m whitebox
```

### Chạy toàn bộ với script PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File .\run_tests.ps1
```

### Nếu cần chạy file test item riêng lẻ
```powershell
C:/Users/ADMIN/AppData/Local/Programs/Python/Python313/python.exe -m pytest -q tests/test_notification_service.py
```

### Xem kết quả test đã lưu
- `services/notification-service/test_results.txt`
