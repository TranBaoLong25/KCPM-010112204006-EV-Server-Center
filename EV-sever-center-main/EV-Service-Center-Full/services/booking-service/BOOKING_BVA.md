# Booking Service - Boundary Value Analysis (BVA)

## 1. Mục tiêu

Tài liệu này xác định các giá trị biên cần kiểm thử cho chức năng tạo lịch đặt (`BookingService.create_booking`) của `booking-service`.

## 2. Các biến đầu vào chính cho tạo booking

| Biến đầu vào | Ý nghĩa | Kiểu | Miền hợp lệ | Ghi chú |
|---|---|---|---|---|
| `user_id` | ID người dùng đăng ký | Số nguyên | `>= 1` | Tham chiếu đến User Service |
| `service_type` | Loại dịch vụ | Chuỗi | không rỗng, <= 100 ký tự | |
| `technician_id` | ID kỹ thuật viên | Số nguyên | `>= 1` | |
| `station_id` | ID trạm dịch vụ | Số nguyên | `>= 1` | |
| `center_id` | ID chi nhánh | Số nguyên | `>= 1` hoặc `null` | Nếu có, phải tồn tại trong ServiceCenter |
| `start_time` | Thời gian bắt đầu | ISO datetime | hợp lệ, trước `end_time` | |
| `end_time` | Thời gian kết thúc | ISO datetime | hợp lệ, sau `start_time` | |

## 3. Giả định giá trị biên

### user_id
- min: `1`
- min+: `2`
- nominal: `10`
- max-: `999998`
- max: `999999`

### service_type
- min: `A` (1 ký tự)
- min+: `AB` (2 ký tự)
- nominal: `Thay pin xe` (độ dài trung bình)
- max-: `A` * 99
- max: `A` * 100

### technician_id
- min: `1`
- min+: `2`
- nominal: `10`
- max-: `999998`
- max: `999999`

### station_id
- min: `1`
- min+: `2`
- nominal: `10`
- max-: `999998`
- max: `999999`

### center_id
- min: `1`
- min+: `2`
- nominal: `10`
- max-: `999998`
- max: `999999`

### start_time / end_time
- min: `2026-07-01T08:00:00`
- min+: `2026-07-01T09:00:00`
- nominal: `2026-07-15T10:00:00`
- max-: `2026-12-31T16:00:00`
- max: `2026-12-31T17:00:00`

## 4. Test case biên đề xuất

| STT | Tên test case | Input | Expected | Tags |
|---|---|---|---|---|
| 1 | Booking hợp lệ | `user_id=1`, `service_type="Thay pin"`, `technician_id=2`, `station_id=3`, `start_time=2026-07-01T08:00:00`, `end_time=2026-07-01T09:00:00` | Hợp lệ | B1, B6 |
| 2 | Booking hợp lệ nominal | `user_id=10`, `service_type="Bảo dưỡng"`, `technician_id=10`, `station_id=10`, `start_time=2026-07-15T10:00:00`, `end_time=2026-07-15T11:00:00` | Hợp lệ | B3, B8 |
| 3 | Booking bắt đầu/trùng lịch | `start_time=2026-07-01T08:00:00`, `end_time=2026-07-01T09:00:00` mà trùng với booking khác | Không hợp lệ | B1, X1 |
| 4 | `service_type` rỗng | `service_type=""` | Không hợp lệ | X2 |
| 5 | `start_time >= end_time` | `start_time=2026-07-01T10:00:00`, `end_time=2026-07-01T09:00:00` | Không hợp lệ | X3 |
| 6 | `center_id` không tồn tại | `center_id=999999` | Không hợp lệ | X4 |
| 7 | `technician_id` ngoài biên | `technician_id=0` | Không hợp lệ | X5 |

## 5. Ghi chú

- `BookingService.is_time_available` là bước kiểm tra quan trọng cho test trùng lịch.
- `center_id` là tùy chọn, nhưng nếu được gửi thì phải tồn tại.
- `user_id` được xác thực qua `User Service` nội bộ.
