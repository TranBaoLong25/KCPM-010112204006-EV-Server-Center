# Notification Service - BVA / Test Case Design

## 1. Mục tiêu

Phần này thiết kế kiểm thử cho `notification-service`, tập trung vào API nội bộ tạo thông báo `/internal/notifications/create` và các ràng buộc dữ liệu đầu vào.

## 2. Yêu cầu hợp lệ của notification payload

Một notification hợp lệ khi tất cả các trường bắt buộc tồn tại và nằm trong giá trị chấp nhận được:

- `user_id`: số nguyên dương (>= 1)
- `title`: chuỗi không rỗng, tối đa 255 ký tự
- `message`: chuỗi không rỗng
- `notification_type`: một trong các giá trị `booking_status`, `inventory_alert`, `payment`, `reminder`, `system`
- `channel`: một trong các giá trị `in_app`, `email`, `sms`, `push`
- `priority`: một trong các giá trị `low`, `medium`, `high`, `urgent`
- `scheduled_at`: chuỗi ISO 8601 hợp lệ hoặc không truyền để gửi ngay

## 3. Câu 1. Xác định lớp tương đương

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
|---|---|---|---|---|
| user_id | `user_id >= 1` | V1 | `user_id <= 0` | X1 |
| title | `1 <= len(title) <= 255` | V2 | `len(title) = 0` <br> `len(title) > 255` | X2 <br> X3 |
| message | `len(message) >= 1` | V3 | `len(message) = 0` | X4 |
| notification_type | one of valid enums | V4 | any other value | X5 |
| channel | one of valid enums | V5 | any other value | X6 |
| priority | one of valid enums | V6 | any other value | X7 |
| scheduled_at | valid ISO datetime string or absent | V7 | invalid datetime format | X8 |

## 4. Câu 2. Phân tích giá trị biên

Áp dụng Standard Boundary Value Analysis cho các trường có biên rõ ràng.

| Biến đầu vào | min | min+ | nominal | max- | max | Tag biên |
|---|---|---|---|---|---|---|
| user_id | 1 | 2 | 100 | 999998 | 999999 | B1, B2, B3, B4, B5 |
| title length | 1 | 2 | 128 | 254 | 255 | B6, B7, B8, B9, B10 |
| message length | 1 | 2 | 100 | 999 | 1000 | B11, B12, B13, B14, B15 |
| scheduled_at | `2026-06-29T08:00:00` | `2026-06-29T08:00:01` | `2026-12-31T12:00:00` | `2027-01-01T00:00:00` | `2027-12-31T23:59:59` | B16, B17, B18, B19, B20 |

> Ghi chú: `scheduled_at` là chuỗi ISO 8601 được dùng để kiểm thử ngày giờ lập lịch; nếu không truyền trường này thì thông báo được gửi ngay.

## 5. Câu 3. Thiết kế test case

Thiết kế tối thiểu 8 test case cho API tạo notification.

| STT | Tên test case | Payload chính | Kết quả mong đợi | Tag được bao phủ |
|---:|---|---|---|---|
| 1 | Tạo notification hợp lệ | `user_id=1`, `title="Đặt lịch thành công"`, `message="Xe của bạn đã được lên lịch"`, `notification_type="booking_status"`, `channel="email"`, `priority="medium"` | Hợp lệ | V1, V2, V3, V4, V5, V6 |
| 2 | Thiếu `user_id` | `title`, `message`, `notification_type`, `channel`, `priority` | Không hợp lệ (Missing required fields) | X1, V2, V3, V4, V5, V6 |
| 3 | `title` trống | `user_id=1`, `title=""`, `message=...` | Không hợp lệ (title empty) | V1, X2, V3, V4, V5, V6 |
| 4 | `title` quá dài | `user_id=1`, `title=256 ký tự`, `message=...` | Không hợp lệ (title > 255) | V1, X3, V3, V4, V5, V6 |
| 5 | `notification_type` không hợp lệ | `notification_type="unknown"` | Không hợp lệ (invalid enum) | V1, V2, V3, X5, V5, V6 |
| 6 | `channel` không hợp lệ | `channel="fax"` | Không hợp lệ (invalid enum) | V1, V2, V3, V4, X6, V6 |
| 7 | Hợp lệ tại biên `title` min | `title="A"` | Hợp lệ | B6, V1, V3, V4, V5, V6 |
| 8 | Hợp lệ tại biên `title` max | `title=255 ký tự`, `user_id=1` | Hợp lệ | B10, V1, V3, V4, V5, V6 |

### Bổ sung test case `scheduled_at`

| STT | Tên test case | Payload chính | Kết quả mong đợi | Tag được bao phủ |
|---:|---|---|---|---|
| 9 | Lập lịch gửi notification đúng ISO | `scheduled_at="2026-07-01T09:00:00"` | Hợp lệ | V7, B16 |
| 10 | `scheduled_at` định dạng sai | `scheduled_at="01-07-2026 09:00"` | Không hợp lệ | X8 |

## 6. Câu 4. Đề xuất kiểm thử tự động

Bạn có thể viết unit test cho `NotificationService.create_notification` theo kiểu pytest hoặc unittest.

Ví dụ mẫu:

```python
import json
import pytest
from services.notification_service import NotificationService

class TestNotificationService:
    def test_create_notification_valid(self):
        data = {
            "user_id": 1,
            "title": "Đặt lịch thành công",
            "message": "Xe của bạn đã được lên lịch.",
            "notification_type": "booking_status",
            "channel": "email",
            "priority": "medium"
        }

        notification, error = NotificationService.create_notification(data)
        assert error is None
        assert notification is not None
        assert notification.status == "sent"

    def test_create_notification_missing_user_id(self):
        data = {
            "title": "Thông báo",
            "message": "Nội dung...",
            "notification_type": "system",
            "channel": "in_app",
            "priority": "medium"
        }

        notification, error = NotificationService.create_notification(data)
        assert notification is None
        assert "Missing required fields" in error
```

> Lưu ý: để test service này, cần chạy trong application context của Flask và cấu hình cơ sở dữ liệu test phù hợp.
