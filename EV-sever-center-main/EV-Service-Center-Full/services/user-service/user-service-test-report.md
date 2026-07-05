# BÁO CÁO KIỂM THỬ USER SERVICE

## Dự án: EV Service Center Maintenance Management System

---

# 1. Giới thiệu

## 1.1 Mục tiêu

Kiểm thử User Service nhằm:

- Đảm bảo các chức năng xác thực hoạt động đúng yêu cầu.
- Phát hiện lỗi dữ liệu đầu vào.
- Đảm bảo việc quản lý hồ sơ người dùng chính xác.
- Đảm bảo phân quyền Admin và User được thực hiện đúng.
- Đánh giá chất lượng mã nguồn và độ ổn định của hệ thống.

---

## 1.2 Phạm vi kiểm thử

Các chức năng được kiểm thử:

- Đăng ký tài khoản
- Đăng nhập
- Gửi OTP quên mật khẩu
- Xem hồ sơ cá nhân
- Cập nhật hồ sơ cá nhân
- Khóa/Mở khóa tài khoản

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

| STT    | API                                    | Method | Mô tả                  |
| ------ | -------------------------------------- | ------ | ---------------------- |
| ESC-6  | /api/register                          | POST   | Đăng ký tài khoản      |
| ESC-7  | /api/login                             | POST   | Đăng nhập              |
| ESC-8  | /api/send-otp                          | POST   | Gửi OTP                |
| ESC-43 | /api/profile                           | GET    | Lấy hồ sơ cá nhân      |
| ESC-44 | /api/profile                           | PUT    | Cập nhật hồ sơ         |
| ESC-46 | /api/admin/users/{user_id}/toggle-lock | PUT    | Khóa/Mở khóa tài khoản |

---

# 4. Black-box Testing

## 4.1 Phân hoạch lớp tương đương (Equivalence Partitioning)

### Register

#### Email

Lớp hợp lệ:

- user@gmail.com

Lớp không hợp lệ:

- usergmail.com
- abc@
- @gmail.com

#### Username

Lớp hợp lệ:

- username có ít nhất 5 ký tự

Lớp không hợp lệ:

- username nhỏ hơn 5 ký tự

#### Password

Lớp hợp lệ:

- password có ít nhất 6 ký tự

Lớp không hợp lệ:

- password nhỏ hơn 6 ký tự

---

### Login

Lớp hợp lệ:

- Email hoặc username tồn tại
- Password đúng
- Tài khoản active

Lớp không hợp lệ:

- Sai password
- Tài khoản không tồn tại
- Tài khoản bị khóa
- Thiếu trường bắt buộc

---

### Send OTP

Lớp hợp lệ:

- Email tồn tại
- Email đúng định dạng

Lớp không hợp lệ:

- Email sai định dạng
- Thiếu email
- Email không tồn tại

---

### Update Profile

Lớp hợp lệ:

- Phone Number gồm 10 số
- VIN không rỗng

Lớp không hợp lệ:

- Phone Number sai định dạng
- VIN rỗng

---

### Toggle Lock

Lớp hợp lệ:

- user_id tồn tại
- Admin token hợp lệ

Lớp không hợp lệ:

- user_id không tồn tại
- Thiếu token
- Sai quyền

---

# 4.2 Boundary Value Analysis (BVA)

## Register

### Password

| Test Case  | Input   | Expected |
| ---------- | ------- | -------- |
| BVA-REG-01 | 12345   | 400      |
| BVA-REG-02 | 123456  | 201      |
| BVA-REG-03 | 1234567 | 201      |

### Username

| Test Case  | Input  | Expected |
| ---------- | ------ | -------- |
| BVA-REG-04 | abcd   | 400      |
| BVA-REG-05 | abcde  | 201      |
| BVA-REG-06 | abcdef | 201      |

### Email

| Test Case  | Input        | Expected     |
| ---------- | ------------ | ------------ |
| BVA-REG-07 | a@b.c        | 200 hoặc 400 |
| BVA-REG-08 | abcgmail.com | 400          |
| BVA-REG-09 | abc@         | 400          |
| BVA-REG-10 | @gmail.com   | 400          |

---

## Login

| Test Case    | Input             | Expected     |
| ------------ | ----------------- | ------------ |
| BVA-LOGIN-01 | password=12345    | 400 hoặc 401 |
| BVA-LOGIN-02 | password=123456   | 200          |
| BVA-LOGIN-03 | password=1234567  | 200          |
| BVA-LOGIN-04 | email_username="" | 400          |
| BVA-LOGIN-05 | thiếu password    | 400          |
| BVA-LOGIN-06 | sai password      | 401          |

---

## Send OTP

| Test Case  | Input               | Expected     |
| ---------- | ------------------- | ------------ |
| BVA-OTP-01 | a@b.c               | 200 hoặc 400 |
| BVA-OTP-02 | abcgmail.com        | 400          |
| BVA-OTP-03 | abc@                | 400          |
| BVA-OTP-04 | @gmail.com          | 400          |
| BVA-OTP-05 | email không tồn tại | 404 hoặc 400 |
| BVA-OTP-06 | {}                  | 400          |

---

## Update Profile

### Phone Number

| Test Case      | Input       | Expected |
| -------------- | ----------- | -------- |
| BVA-PROFILE-01 | 091234567   | 400      |
| BVA-PROFILE-02 | 0912345678  | 200      |
| BVA-PROFILE-03 | 09123456789 | 400      |
| BVA-PROFILE-04 | abc123      | 400      |

### VIN Number

| Test Case      | Input         | Expected     |
| -------------- | ------------- | ------------ |
| BVA-PROFILE-05 | ""            | 400          |
| BVA-PROFILE-06 | VIN123        | 200          |
| BVA-PROFILE-07 | Chuỗi rất dài | 200 hoặc 400 |

---

## Toggle Lock

| Test Case   | Input           | Expected     |
| ----------- | --------------- | ------------ |
| BVA-LOCK-01 | user_id = 0     | 400 hoặc 404 |
| BVA-LOCK-02 | user_id = 1     | 200          |
| BVA-LOCK-03 | user_id = 99999 | 404          |
| BVA-LOCK-04 | user_id = abc   | 400 hoặc 404 |
| BVA-LOCK-05 | Không token     | 401          |
| BVA-LOCK-06 | User token      | 403          |

---

# 5. White-box Testing

Công cụ:

- pytest
- unittest.mock

Thư mục:

services/user-service/tests/

Các unit test đã thực hiện:

### Register

- register_success
- register_duplicate_email
- register_invalid_email

### Login

- login_success
- login_wrong_password
- login_locked_account

### Send OTP

- send_otp_success
- send_otp_invalid_email
- send_otp_email_not_found

### Profile

- get_profile_success
- update_profile_success
- update_profile_invalid_phone
- update_profile_invalid_vin

### Admin Toggle Lock

- toggle_lock_success
- toggle_lock_unauthorized
- toggle_lock_forbidden

---

# 6. Frontend Testing

Công cụ:

- Playwright

Các kịch bản kiểm thử:

- FE-USER-01: Mở trang đăng nhập
- FE-USER-02: Đăng nhập thành công
- FE-USER-03: Đăng nhập sai mật khẩu
- FE-USER-04: Để trống Email
- FE-USER-05: Để trống Password
- FE-USER-06: Đăng ký tài khoản thành công

---

# 7. Coverage Testing

Lệnh thực hiện:

```bash
pytest --cov=. --cov-report=html
```

Kết quả:

- Sinh file `.coverage`
- Sinh thư mục `htmlcov`
- Hiển thị tỷ lệ bao phủ mã nguồn của User Service.

Mục đích:

- Đánh giá mức độ các đoạn mã đã được kiểm thử.
- Xác định những phần chưa được test.

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

.github/workflows/user-service-ci-cd.yml

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

Kết quả kiểm thử cho thấy các chức năng chính của User Service hoạt động đúng yêu cầu, xử lý được dữ liệu hợp lệ và không hợp lệ, đồng thời đảm bảo phân quyền và tính ổn định của hệ thống.
