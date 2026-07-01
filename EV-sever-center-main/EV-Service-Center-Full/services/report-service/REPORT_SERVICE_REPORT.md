# BÁO CÁO KIỂM THỬ REPORT SERVICE

## Dự án: EV Service Center Maintenance Management System

---

# 1. Giới thiệu

## 1.1 Mục tiêu

Kiểm thử Report Service nhằm:

- Đảm bảo các API báo cáo trả về dữ liệu chính xác.
- Kiểm tra việc lọc dữ liệu theo khoảng thời gian.
- Đảm bảo Dashboard hiển thị đúng số liệu thống kê.
- Kiểm tra phân quyền Admin đối với các API báo cáo.
- Đánh giá chất lượng mã nguồn và độ ổn định của hệ thống.

---

## 1.2 Phạm vi kiểm thử

Các chức năng được kiểm thử:

- Báo cáo doanh thu
- Báo cáo tình trạng kho
- Dashboard tổng quan
- Phân quyền truy cập báo cáo

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
|-----|------|--------|------------------------------|
| ESC-66 | /api/reports/revenue | GET | Báo cáo doanh thu |
| ESC-67 | /api/reports/inventory | GET | Báo cáo tình trạng kho |
| ESC-68 | /api/reports/dashboard | GET | Dashboard tổng quan |
| ESC-69 | /api/reports/* | GET | Kiểm thử phân quyền Admin |

---

# 4. Black-box Testing

## 4.1 Phân hoạch lớp tương đương (Equivalence Partitioning)

### Revenue Report

#### Lớp hợp lệ

- Có Token hợp lệ
- Start Date hợp lệ
- End Date hợp lệ
- Start Date ≤ End Date

#### Lớp không hợp lệ

- Không có Token
- Token không hợp lệ
- Sai định dạng ngày
- Thiếu Start Date
- Thiếu End Date
- Thiếu cả hai tham số
- Start Date > End Date

---

### Inventory Report

#### Lớp hợp lệ

- Có Token
- Có dữ liệu tồn kho

#### Lớp không hợp lệ

- Không có Token
- Token không hợp lệ

---

### Dashboard Report

#### Lớp hợp lệ

- Có Token
- Dashboard trả về dữ liệu

#### Lớp không hợp lệ

- Không có Token
- Token không hợp lệ

---

### Admin Authorization

#### Lớp hợp lệ

- Admin Token

#### Lớp không hợp lệ

- User Token
- Không có Token

---

# 4.2 Boundary Value Analysis (BVA)

## Revenue Report

### Start Date

| Test Case | Input | Expected |
|------------|-------|----------|
| BVA-REPORT-REVENUE-01 | Start Date = rỗng | 400 |

### End Date

| Test Case | Input | Expected |
|------------|-------|----------|
| BVA-REPORT-REVENUE-02 | End Date = rỗng | 400 |

### Khoảng thời gian

| Test Case | Input | Expected |
|------------|-------|----------|
| BVA-REPORT-REVENUE-03 | Start = End | 200 |
| BVA-REPORT-REVENUE-04 | Start > End | 400 |

---

## Equivalence Partition

### Revenue Report

| Test Case | Input | Expected |
|------------|-------|----------|
| EP-REPORT-REVENUE-01 | Có Token | 200 |
| EP-REPORT-REVENUE-02 | Không Token | 401 |
| EP-REPORT-REVENUE-03 | Token không hợp lệ | 401 |
| EP-REPORT-REVENUE-04 | Sai định dạng ngày | 400 |
| EP-REPORT-REVENUE-05 | Thiếu cả hai tham số | 400 |
| EP-REPORT-REVENUE-06 | Khoảng thời gian hợp lệ | 200 |

---

### Inventory Report

| Test Case | Input | Expected |
|------------|-------|----------|
| EP-REPORT-INVENTORY-01 | Có Token | 200 |
| EP-REPORT-INVENTORY-02 | Không Token | 401 |
| EP-REPORT-INVENTORY-03 | Token không hợp lệ | 401 |
| EP-REPORT-INVENTORY-04 | Có dữ liệu | 200 |

---

### Dashboard

| Test Case | Input | Expected |
|------------|-------|----------|
| EP-REPORT-DASHBOARD-01 | Có Token | 200 |
| EP-REPORT-DASHBOARD-02 | Không Token | 401 |
| EP-REPORT-DASHBOARD-03 | Token không hợp lệ | 401 |
| EP-REPORT-DASHBOARD-04 | Dashboard trả về dữ liệu | 200 |

---

### Admin Authorization

| Test Case | Input | Expected |
|------------|-------|----------|
| EP-REPORT-ADMIN-01 | Admin Token | 200 |
| EP-REPORT-ADMIN-02 | User Token | 403 |
| EP-REPORT-ADMIN-03 | Không có Token | 401 |

---

# 5. White-box Testing

## Công cụ

- pytest
- unittest.mock

Thư mục

```
services/report-service/tests/
```

Các Unit Test đã thực hiện

### Revenue Report

- test_revenue_report_success
- test_revenue_missing_start_date
- test_revenue_missing_end_date
- test_revenue_invalid_date
- test_revenue_start_after_end

### Inventory Report

- test_inventory_success
- test_inventory_unauthorized
- test_inventory_invalid_token

### Dashboard

- test_dashboard_success
- test_dashboard_unauthorized
- test_dashboard_invalid_token

### Authorization

- test_admin_access_success
- test_user_forbidden
- test_missing_token

---

# 6. Frontend Testing

## Công cụ

- Playwright

Các kịch bản kiểm thử

- FE-REPORT-01: Mở Dashboard
- FE-REPORT-02: Xem báo cáo doanh thu
- FE-REPORT-03: Xem báo cáo kho
- FE-REPORT-04: Lọc theo khoảng thời gian
- FE-REPORT-05: Truy cập bằng User thường
- FE-REPORT-06: Kiểm tra hiển thị lỗi khi nhập sai ngày

---

# 7. Coverage Testing

Lệnh thực hiện

```bash
pytest --cov=. --cov-report=html
```

Kết quả

- Sinh file `.coverage`
- Sinh thư mục `htmlcov`
- Hiển thị tỷ lệ bao phủ mã nguồn của Report Service.

Mục đích

- Đánh giá mức độ bao phủ của Unit Test.
- Xác định các hàm chưa được kiểm thử.
- Nâng cao chất lượng và độ tin cậy của mã nguồn.

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
.github/workflows/report-service-ci-cd.yml
```

---

# 9. Kết luận

Nhóm đã thực hiện đầy đủ các hoạt động kiểm thử cho Report Service gồm:

✓ Black-box Testing

✓ Equivalence Partitioning

✓ Boundary Value Analysis

✓ White-box Testing

✓ Coverage Testing

✓ Frontend Testing bằng Playwright

✓ CI/CD bằng GitHub Actions

Kết quả kiểm thử cho thấy các API báo cáo hoạt động đúng theo yêu cầu, xử lý chính xác các trường hợp dữ liệu hợp lệ và không hợp lệ, đồng thời đảm bảo phân quyền giữa Admin và User. Việc áp dụng kiểm thử hộp đen, hộp trắng, đo độ bao phủ mã nguồn và tự động hóa thông qua GitHub Actions góp phần nâng cao chất lượng, tính ổn định và khả năng triển khai của Report Service trong hệ thống EV Service Center Maintenance Management System.