# BÁO CÁO KIỂM THỬ MAINTENANCE SERVICE

## Dự án: EV Service Center Maintenance Management System

---

# 1. Giới thiệu

## 1.1 Mục tiêu

Kiểm thử Maintenance Service nhằm:

- Đảm bảo các chức năng quản lý bảo trì hoạt động đúng yêu cầu.
- Kiểm tra tính chính xác của dữ liệu đầu vào.
- Đảm bảo việc tạo, cập nhật và xóa công việc bảo trì chính xác.
- Đảm bảo phân quyền giữa Technician, User và Admin.
- Đánh giá chất lượng mã nguồn và mức độ ổn định của hệ thống.

---

## 1.2 Phạm vi kiểm thử

Các chức năng được kiểm thử:

- Xem danh sách công việc bảo trì
- Tạo công việc bảo trì
- Xem chi tiết công việc
- Cập nhật trạng thái công việc
- Hủy/Xóa công việc bảo trì

---

# 2. Môi trường kiểm thử

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Python Flask |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| API Testing | Postman |
| Unit Testing | pytest |
| Coverage | pytest-cov |
| Frontend Testing | Playwright |
| CI/CD | GitHub Actions |
| Version Control | Git + GitHub |

---

# 3. Danh sách API kiểm thử

| STT | API | Method | Mô tả |
|-----|------|--------|-----------------------------|
| ESC-Maint-02 | /api/maintenance | GET | Lấy danh sách bảo trì |
| ESC-Maint-03 | /api/maintenance/{task_id} | GET | Xem chi tiết bảo trì |
| ESC-Maint-04 | /api/maintenance/{task_id}/status | PUT | Cập nhật trạng thái |
| ESC-Maint-05 | /api/maintenance | POST | Tạo công việc bảo trì |
| ESC-Maint-06 | /api/maintenance/{task_id} | DELETE | Hủy/Xóa công việc |

---

# 4. Black-box Testing

## 4.1 Phân hoạch lớp tương đương (Equivalence Partitioning)

### 4.1.1 Lấy danh sách bảo trì

#### Lớp hợp lệ

- Token hợp lệ
- Người dùng đã xác thực

#### Lớp không hợp lệ

- Không có Token
- Token không hợp lệ
- Token hết hạn

---

### 4.1.2 Tạo công việc bảo trì

#### Booking ID

Lớp hợp lệ

- Booking ID tồn tại

Lớp không hợp lệ

- Booking ID không tồn tại
- Booking ID bằng 0
- Thiếu Booking ID

#### Technician ID

Lớp hợp lệ

- Technician ID tồn tại

Lớp không hợp lệ

- Technician ID bằng 0
- Technician ID không tồn tại
- Thiếu Technician ID

#### Description

Lớp hợp lệ

- Có mô tả công việc

Lớp không hợp lệ

- Chuỗi rỗng
- Thiếu Description

---

### 4.1.3 Xem chi tiết công việc

#### Lớp hợp lệ

- Task ID tồn tại
- Token hợp lệ

#### Lớp không hợp lệ

- Task ID không tồn tại
- Task ID sai kiểu dữ liệu
- Không có Token

---

### 4.1.4 Cập nhật trạng thái

#### Status hợp lệ

- Pending
- In Progress
- Completed
- Cancelled

#### Status không hợp lệ

- Chuỗi rỗng
- Sai giá trị
- Thiếu Status

---

### 4.1.5 Xóa công việc

#### Lớp hợp lệ

- Task ID tồn tại
- Có quyền thực hiện

#### Lớp không hợp lệ

- Task ID không tồn tại
- Không có Token
- Không đủ quyền

---

# 4.2 Boundary Value Analysis (BVA)

## Lấy danh sách

| Test Case | Input | Expected |
|------------|--------|----------|
| BVA-MAINT-LIST-01 | Token hợp lệ | 200 |
| BVA-MAINT-LIST-02 | Không Token | 401 |
| BVA-MAINT-LIST-03 | Token sai | 401 |

---

## Tạo công việc

### Booking ID

| Test Case | Input | Expected |
|------------|--------|----------|
| BVA-MAINT-CREATE-01 | Booking ID = 0 | 400 |
| BVA-MAINT-CREATE-02 | Booking ID = 1 | 201 |

### Technician ID

| Test Case | Input | Expected |
|------------|--------|----------|
| BVA-MAINT-CREATE-03 | Technician ID = 0 | 400 |
| BVA-MAINT-CREATE-04 | Technician ID = 1 | 201 |

### Description

| Test Case | Input | Expected |
|------------|--------|----------|
| BVA-MAINT-CREATE-05 | "" | 400 |
| BVA-MAINT-CREATE-06 | "Oil Change" | 201 |

---

## Chi tiết công việc

| Test Case | Input | Expected |
|------------|--------|----------|
| BVA-MAINT-DETAIL-01 | Task ID = 0 | 404 |
| BVA-MAINT-DETAIL-02 | Task ID = 1 | 200 |
| BVA-MAINT-DETAIL-03 | Task ID = abc | 400 |
| BVA-MAINT-DETAIL-04 | Không Token | 401 |

---

## Cập nhật trạng thái

| Test Case | Input | Expected |
|------------|--------|----------|
| BVA-MAINT-STATUS-01 | Task ID = 0 | 404 |
| BVA-MAINT-STATUS-02 | Task ID = 1 | 200 |
| BVA-MAINT-STATUS-03 | Status = "" | 400 |
| BVA-MAINT-STATUS-04 | Status = Completed | 200 |
| BVA-MAINT-STATUS-05 | Status = abc | 400 |
| BVA-MAINT-STATUS-06 | Không Token | 401 |

---

## Xóa công việc

| Test Case | Input | Expected |
|------------|--------|----------|
| BVA-MAINT-DELETE-01 | Task ID = 0 | 404 |
| BVA-MAINT-DELETE-02 | Task ID = 1 | 200 |
| BVA-MAINT-DELETE-03 | Không Token | 401 |
| BVA-MAINT-DELETE-04 | Không đủ quyền | 403 |

---

# 5. White-box Testing

## Công cụ

- pytest
- unittest.mock

Thư mục

```
services/maintenance-service/tests/
```

Các Unit Test đã thực hiện

### Maintenance List

- test_get_tasks_success
- test_get_tasks_no_token
- test_get_tasks_invalid_token

### Create Maintenance

- test_create_task_success
- test_create_invalid_booking
- test_create_invalid_technician
- test_create_missing_description

### Detail

- test_get_task_detail_success
- test_get_task_not_found
- test_get_task_invalid_id

### Update Status

- test_update_status_success
- test_update_invalid_status
- test_update_task_not_found

### Delete

- test_delete_success
- test_delete_not_found
- test_delete_unauthorized

---

# 6. Frontend Testing

## Công cụ

- Playwright

Các kịch bản kiểm thử

- FE-MAINT-01: Mở trang danh sách bảo trì
- FE-MAINT-02: Xem chi tiết công việc
- FE-MAINT-03: Tạo công việc bảo trì
- FE-MAINT-04: Cập nhật trạng thái
- FE-MAINT-05: Hủy công việc
- FE-MAINT-06: Kiểm tra hiển thị thông báo lỗi khi nhập dữ liệu không hợp lệ

---

# 7. Coverage Testing

Lệnh thực hiện

```bash
pytest --cov=. --cov-report=html
```

Kết quả

- Sinh file `.coverage`
- Sinh thư mục `htmlcov`
- Hiển thị tỷ lệ bao phủ mã nguồn của Maintenance Service.

Mục đích

- Đánh giá mức độ bao phủ của các Unit Test.
- Xác định những hàm chưa được kiểm thử.
- Hỗ trợ cải thiện chất lượng mã nguồn.

---

# 8. CI/CD

## Công cụ

- GitHub Actions

Workflow

```
Push Code
      │
      ▼
Checkout Source
      │
      ▼
Install Dependencies
      │
      ▼
Run pytest
      │
      ▼
Run Coverage
      │
      ▼
Build Docker Image
      │
      ▼
Build Success
```

File cấu hình

```
.github/workflows/maintenance-service-ci-cd.yml
```

---

# 9. Kết luận

Nhóm đã thực hiện thành công các hoạt động kiểm thử cho Maintenance Service bao gồm:

✓ Black-box Testing

✓ Equivalence Partitioning

✓ Boundary Value Analysis

✓ White-box Testing

✓ Coverage Testing

✓ Frontend Testing bằng Playwright

✓ CI/CD bằng GitHub Actions

Kết quả kiểm thử cho thấy các chức năng quản lý bảo trì hoạt động đúng theo yêu cầu. Hệ thống xử lý chính xác các trường hợp dữ liệu hợp lệ và không hợp lệ, đảm bảo tính toàn vẹn dữ liệu, kiểm soát quyền truy cập và duy trì tính ổn định trong quá trình vận hành. Việc kết hợp giữa kiểm thử hộp đen, kiểm thử hộp trắng, kiểm thử giao diện, đo độ bao phủ mã nguồn và quy trình CI/CD đã góp phần nâng cao chất lượng và độ tin cậy của Maintenance Service trước khi triển khai.