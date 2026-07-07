# Assignment: Kiểm thử chức năng User Service

**Thời lượng:** 90 phút  
**Chủ đề:** Phân hoạch lớp tương đương, phân tích giá trị biên, thiết kế test case và kiểm thử API  
**Mức độ:** Cơ bản đến trung bình  
**Hình thức:** Cá nhân  
**Tổng điểm:** 10 điểm  

**Họ và tên:** ........................................  
**MSSV:** ........................................  
**Lớp:** ........................................  

---

# 1. Mục tiêu bài tập

1. Xác định điều kiện kiểm thử cho chức năng xác thực và quản lý hồ sơ trong User Service.
2. Áp dụng kỹ thuật phân hoạch lớp tương đương cho email, username, password, token và `user_id`.
3. Áp dụng kỹ thuật phân tích giá trị biên cho `user_id`, password và dữ liệu cập nhật hồ sơ.
4. Thiết kế test case cho API đăng ký, đăng nhập, gửi OTP, xem/cập nhật hồ sơ và quản trị tài khoản.
5. Ghi nhận lỗi thực tế khi kiểm thử bằng Postman/Newman và đồng bộ trạng thái trên Jira.
6. Đề xuất hướng xử lý lỗi và viết kiểm thử tự động để xác nhận hệ thống hoạt động đúng.

---

# 2. Nội dung tham khảo

Trong bài này em áp dụng các kỹ thuật kiểm thử sau:

* **Equivalence Partitioning:** chia dữ liệu đầu vào thành nhóm hợp lệ và không hợp lệ.
* **Boundary Value Analysis (BVA):** chọn dữ liệu tại vùng biên, ví dụ `user_id = 0`, `user_id = 1`, `user_id = 99999`.
* **API Testing:** kiểm thử endpoint bằng Postman với Bearer Token.
* **Negative Testing:** kiểm thử thiếu token, thiếu field, email sai định dạng, tài khoản không tồn tại.
* **Integration Test / CI:** chạy collection bằng Newman trên GitHub Actions và ghi nhận lỗi sang Jira.

---

# 3. Mô tả bài toán

Hệ thống EV Service Center có **User Service** dùng để quản lý tài khoản, xác thực và hồ sơ người dùng.

User Service hỗ trợ các chức năng chính:

| Chức năng | Endpoint | Method | Mô tả |
| -------- | -------- | ------ | ----- |
| Đăng ký tài khoản | `/api/register` | POST | Tạo tài khoản người dùng mới |
| Đăng nhập | `/api/login` | POST | Xác thực và cấp access token |
| Gửi OTP quên mật khẩu | `/api/send-otp` | POST | Gửi mã OTP đến email |
| Đặt lại mật khẩu | `/api/reset-password` | POST | Xác minh OTP và đổi mật khẩu |
| Lấy hồ sơ cá nhân | `/api/profile` | GET | Lấy profile của người đang đăng nhập |
| Cập nhật hồ sơ cá nhân | `/api/profile` | PUT | Cập nhật thông tin cá nhân, xe và VIN |
| Cập nhật tài khoản | `/api/account` | PUT | Người dùng tự sửa thông tin tài khoản |
| Xóa tài khoản cá nhân | `/api/account` | DELETE | Người dùng xóa tài khoản của mình |
| Lấy danh sách user | `/api/admin/users` | GET | Admin lấy toàn bộ tài khoản |
| Admin tạo user | `/api/admin/users` | POST | Admin tạo tài khoản mới |
| Admin xóa user | `/api/admin/users/<user_id>` | DELETE | Admin xóa tài khoản |
| Admin khóa/mở khóa user | `/api/admin/users/<user_id>/toggle-lock` | PUT | Admin chuyển trạng thái `active`/`locked` |

Trong bài assignment này, phạm vi kiểm thử tập trung vào các nhóm API đã có trong Postman/Jira:

```text
POST /api/register
POST /api/login
POST /api/send-otp
GET  /api/profile
PUT  /api/profile
GET  /api/admin/users
PUT  /api/admin/users/<user_id>/toggle-lock
```

và các testcase BVA/Equivalence trong folder:

```text
[Black-box] - BVA & Equivalence / [user-service] - BVA & Equivalence
```

---

# 4. Yêu cầu nghiệp vụ mong đợi

## 4.1 Quy tắc đăng ký tài khoản

Endpoint:

```http
POST /api/register
```

Điều kiện hợp lệ:

* Body phải có `email`, `username`, `password`.
* Email chưa tồn tại trong database.
* Username chưa tồn tại trong database.
* Password thỏa điều kiện tối thiểu theo quy định hệ thống.

Kết quả mong đợi:

```text
HTTP 201 Created nếu đăng ký thành công
HTTP 400 Bad Request nếu thiếu field bắt buộc
HTTP 409 Conflict nếu email hoặc username đã tồn tại
```

## 4.2 Quy tắc đăng nhập

Endpoint:

```http
POST /api/login
```

Điều kiện hợp lệ:

* Body phải có `email_username` và `password`.
* Email hoặc username tồn tại.
* Password đúng.
* Tài khoản có trạng thái `active`.

Kết quả mong đợi:

```text
HTTP 200 OK và trả về access_token nếu hợp lệ
HTTP 400 Bad Request nếu thiếu email_username hoặc password
HTTP 401 Unauthorized nếu sai thông tin đăng nhập
HTTP 403 Forbidden nếu tài khoản bị khóa
```

## 4.3 Quy tắc hồ sơ cá nhân

Endpoint:

```http
GET /api/profile
PUT /api/profile
```

Điều kiện hợp lệ:

* Người dùng phải đăng nhập.
* Token hợp lệ và chưa hết hạn.
* Với PUT, body có thể cập nhật các field: `full_name`, `phone_number`, `address`, `vehicle_model`, `vin_number`.

Kết quả mong đợi:

```text
HTTP 200 OK nếu lấy/cập nhật thành công
HTTP 401 Unauthorized nếu thiếu token hoặc token không hợp lệ
HTTP 400 Bad Request nếu body không hợp lệ
HTTP 404 Not Found nếu profile không tồn tại
```

## 4.4 Quy tắc admin quản lý user

Endpoint:

```http
GET /api/admin/users
PUT /api/admin/users/<user_id>/toggle-lock
```

Điều kiện hợp lệ:

* Người gọi phải có token hợp lệ.
* Role trong JWT phải là `admin`.
* `user_id` phải là số nguyên dương.
* User cần khóa/mở khóa phải tồn tại.

Kết quả mong đợi:

```text
HTTP 200 OK nếu thao tác thành công
HTTP 401 Unauthorized nếu thiếu token
HTTP 403 Forbidden nếu không phải admin
HTTP 404 Not Found nếu user_id không tồn tại
HTTP 400 Bad Request nếu user_id sai kiểu hoặc không hợp lệ
```

---

# 5. Danh sách test case lấy từ Postman/Jira

## 5.1 Test case chức năng chính

| STT | Mã test case | Method | Endpoint | Mô tả | Expected |
| --: | ------------ | ------ | -------- | ----- | -------- |
| 1 | ESC-6 / ESC-User-01 | POST | `/api/register` | Đăng ký tài khoản người dùng mới | 201 Created |
| 2 | ESC-7 | POST | `/api/login` | Đăng nhập và cấp access token | 200 OK, có `access_token` |
| 3 | ESC-8 | POST | `/api/send-otp` | Gửi OTP quên mật khẩu | 200 OK |
| 4 | ESC-43 | GET | `/api/profile` | Lấy hồ sơ cá nhân | 200 OK |
| 5 | ESC-44 | PUT | `/api/profile` | Cập nhật hồ sơ cá nhân | 200 OK |
| 6 | ESC-45 | GET | `/api/admin/users` | Admin lấy danh sách user | 200 OK |
| 7 | ESC-46 | PUT | `/api/admin/users/{user_id}/toggle-lock` | Admin khóa/mở khóa tài khoản | 200 OK |

## 5.2 Test case BVA & Equivalence

| STT | Mã test case | Method | Endpoint | Dữ liệu kiểm thử | Expected |
| --: | ------------ | ------ | -------- | ---------------- | -------- |
| 1 | TC-USER-002 | POST | `/api/register` hoặc `/api/login` | Email sai định dạng | 400 Bad Request |
| 2 | TC-USER-003 | POST | `/api/login` | Thiếu email/email_username | 400 Bad Request |
| 3 | BVA-LOGIN-05 | POST | `/api/login` | Tài khoản không tồn tại | 401 Unauthorized |
| 4 | BVA-OTP-02 | POST | `/api/send-otp` | Email thiếu `@` | 400 Bad Request |
| 5 | TC-USER-006 | POST | `/api/login` | Email/tài khoản đã tồn tại hoặc dữ liệu đăng nhập không hợp lệ | 401/409 tùy API |
| 6 | BVA-OTP-03 | POST | `/api/send-otp` | Email thiếu domain | 400 Bad Request |
| 7 | BVA-OTP-04 | POST | `/api/send-otp` | Thiếu email | 400 Bad Request |
| 8 | BVA-LOCK-01 | PUT | `/api/admin/users/0/toggle-lock` | `user_id = 0` | 400 hoặc 404 |
| 9 | BVA-LOCK-02 | PUT | `/api/admin/users/1/toggle-lock` | `user_id = 1` | 200 nếu tồn tại |
| 10 | BVA-LOCK-03 | PUT | `/api/admin/users/99999/toggle-lock` | User không tồn tại | 404 Not Found |
| 11 | BVA-PROFILE-01 | PUT | `/api/profile` | Body đầy đủ nhưng phone/VIN có dữ liệu biên | 200 hoặc 400 tùy validate |
| 12 | BVA-PROFILE-02 | PUT | `/api/profile` | Body thiếu vài field | 200 OK nếu cho cập nhật partial |
| 13 | BVA-PROFILE-03 | PUT | `/api/profile` | Body rỗng | 400 Bad Request hoặc 200 nếu API cho phép no-op |
| 14 | BVA-PROFILE-04 | PUT | `/api/profile` | Không token | 401 Unauthorized |

---

# 6. Mô tả lỗi phát hiện

## 6.1 BUG-USER-01: API gửi OTP trả status không khớp với test script

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-USER-01 |
| Test case liên quan | ESC-8 |
| Chức năng | Gửi OTP quên mật khẩu |
| Method | POST |
| Endpoint | `/api/send-otp` |
| Dữ liệu đầu vào | Email tồn tại |
| Kết quả mong đợi theo nghiệp vụ | 200 OK |
| Test script Postman hiện tại | Kiểm tra 201 Created |
| Mức độ nghiêm trọng | Medium |
| Trạng thái | Failed nếu test script giữ expected 201 |

### Request trên Postman

```http
POST http://localhost/api/send-otp
Content-Type: application/json

{
  "email": "testuser_nhom7@gmail.com"
}
```

### Kết quả mong đợi

Theo controller hiện tại, API gửi OTP thành công trả:

```http
HTTP/1.1 200 OK
```

Body ví dụ:

```json
{
  "message": "Gửi OTP thành công"
}
```

### Kết quả thực tế trong test script

Postman script lại đang kiểm tra:

```javascript
pm.response.to.have.status(201);
```

Do đó nếu API trả đúng 200 thì testcase vẫn bị đánh dấu fail.

### Nguyên nhân phân tích

Test script của ESC-8 có phần mô tả giống API đăng ký ESC-6 và đang expected sai status code. Đây là lỗi ở testcase/script kiểm thử, không nhất thiết là lỗi nghiệp vụ backend.

### Đề xuất xử lý

Sửa Postman test script:

```javascript
pm.test("[ESC-8] Gửi OTP thành công - Mã trả về phải là 200 OK", function () {
    pm.response.to.have.status(200);
});
```

---

## 6.2 BUG-USER-02: Test lấy hồ sơ kiểm tra field `username` nhưng API chỉ trả profile

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-USER-02 |
| Test case liên quan | ESC-43 |
| Chức năng | Lấy hồ sơ cá nhân |
| Method | GET |
| Endpoint | `/api/profile` |
| Kết quả mong đợi theo test script | Body có field `username` |
| Kết quả backend thiết kế | Body trả profile, không có `username` |
| Mức độ nghiêm trọng | Medium |
| Trạng thái | Failed nếu giữ assertion `username` |

### Request trên Postman

```http
GET http://localhost/api/profile
Authorization: Bearer <token>
```

### Kết quả thực tế theo serializer

API trả profile gồm các trường:

```json
{
  "user_id": 1,
  "full_name": "...",
  "phone_number": "...",
  "address": "...",
  "bio": "...",
  "avatar_url": "...",
  "vehicle_model": "...",
  "vin_number": "..."
}
```

Không có field `username`.

### Nguyên nhân phân tích

Trong controller, hàm `serialize_profile()` chỉ serialize thông tin bảng profile. Test script lại kiểm tra field thuộc bảng user:

```javascript
pm.expect(jsonData).to.have.property('username');
```

### Đề xuất xử lý

Có hai hướng:

**Hướng 1: Sửa test script đúng với API hiện tại**

```javascript
pm.test("[ESC-43] Lấy hồ sơ cá nhân thành công", function () {
    pm.response.to.have.status(200);
    const data = pm.response.json();
    pm.expect(data).to.have.property("user_id");
    pm.expect(data).to.have.property("full_name");
});
```

**Hướng 2: Sửa backend nếu yêu cầu nghiệp vụ cần trả username**

Bổ sung `username` vào response profile bằng cách join hoặc lấy thông tin user tương ứng.

---

## 6.3 BUG-USER-03: Request cập nhật profile trong Postman đang để method GET

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-USER-03 |
| Test case liên quan | ESC-44 |
| Chức năng | Cập nhật hồ sơ cá nhân |
| Endpoint đúng | `PUT /api/profile` |
| Postman hiện tại | Đang hiển thị method GET trong collection |
| Kết quả mong đợi | 200 OK và message `Profile updated` |
| Mức độ nghiêm trọng | High |
| Trạng thái | Failed nếu dùng GET |

### Request đúng

```http
PUT http://localhost/api/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Trần Bảo Long",
  "phone_number": "0912345678",
  "address": "Thành phố Hồ Chí Minh",
  "vehicle_model": "VinFast VF8",
  "vin_number": "VIN888777666"
}
```

### Nguyên nhân phân tích

Backend định nghĩa cập nhật profile bằng:

```text
PUT /api/profile
```

nhưng trong Postman collection, test ESC-44 có tên `[PUT]` nhưng request method lại là `GET`. Khi chạy Newman, request không đi vào route update nên response không có `message = Profile updated`.

### Đề xuất xử lý

Sửa method trong Postman từ `GET` sang `PUT`.

---

## 6.4 BUG-USER-04: Toggle lock trả object user nhưng test script yêu cầu `message`

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-USER-04 |
| Test case liên quan | ESC-46 |
| Chức năng | Admin khóa/mở khóa tài khoản |
| Method | PUT |
| Endpoint | `/api/admin/users/{user_id}/toggle-lock` |
| Expected theo script | Response có property `message` |
| Backend hiện tại | Response là object user đã serialize |
| Mức độ nghiêm trọng | Low/Medium |
| Trạng thái | Failed nếu giữ assertion `message` |

### Request trên Postman

```http
PUT http://localhost/api/admin/users/15/toggle-lock
Authorization: Bearer <admin_token>
```

### Response backend hiện tại

```json
{
  "user_id": 15,
  "username": "...",
  "email": "...",
  "role": "user",
  "status": "locked"
}
```

### Nguyên nhân phân tích

Controller đang trả trực tiếp `serialize_user(user)`, không bọc trong object có message. Trong khi Postman script kiểm tra:

```javascript
pm.expect(data).to.have.property("message");
```

### Đề xuất xử lý

Có thể sửa backend để response rõ hơn:

```python
return jsonify({
    "message": "User lock status updated",
    "user": serialize_user(user)
}), 200
```

Hoặc sửa Postman script để kiểm tra `status`:

```javascript
pm.test("Response có trạng thái user", function () {
    const data = pm.response.json();
    pm.expect(data).to.have.property("status");
});
```

---

# PHẦN A. BÀI LÀM

---

## Câu 1. Xác định lớp tương đương

### 1.1 Phân hoạch cho đăng ký tài khoản

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| `email` | Email đúng định dạng và chưa tồn tại | V1 | Thiếu email | X1 |
| | | | Email sai định dạng, ví dụ `abcgmail.com` | X2 |
| | | | Email đã tồn tại | X3 |
| `username` | Username chưa tồn tại | V2 | Thiếu username | X4 |
| | | | Username đã tồn tại | X5 |
| `password` | Password đủ độ dài tối thiểu | V3 | Thiếu password | X6 |
| | | | Password quá ngắn | X7 |

### 1.2 Phân hoạch cho đăng nhập

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| `email_username` | Email hoặc username tồn tại | V4 | Thiếu email_username | X8 |
| | | | Tài khoản không tồn tại | X9 |
| `password` | Password đúng | V5 | Thiếu password | X10 |
| | | | Password sai | X11 |
| `status` | Tài khoản active | V6 | Tài khoản locked | X12 |

### 1.3 Phân hoạch cho token và quyền

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| Bearer Token | Token hợp lệ, chưa hết hạn | V7 | Không có token | X13 |
| | | | Token sai hoặc hết hạn | X14 |
| Role | `admin` khi gọi API admin | V8 | `user` gọi API admin | X15 |

### 1.4 Phân hoạch cho `user_id`

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| `user_id` | Số nguyên dương và tồn tại | V9 | `0` | X16 |
| | | | Số âm | X17 |
| | | | Số nguyên dương nhưng không tồn tại, ví dụ `99999` | X18 |
| | | | Sai kiểu, ví dụ `abc` | X19 |

---

## Câu 2. Phân tích giá trị biên

### 2.1 BVA cho `user_id`

| Nhóm | Giá trị | Ý nghĩa | Kết quả mong đợi |
| ---- | ------- | ------- | ---------------- |
| Dưới biên | `-1` | ID âm | 400 Bad Request hoặc 404 theo route |
| Tại biên dưới không hợp lệ | `0` | ID không hợp lệ | 400 Bad Request hoặc 404 |
| Biên hợp lệ nhỏ nhất | `1` | User đầu tiên | 200 nếu tồn tại |
| Giá trị không tồn tại | `99999` | Đúng kiểu nhưng không có dữ liệu | 404 Not Found |
| Sai kiểu | `abc` | Không phải số nguyên | 400 Bad Request hoặc 404 nếu route không match |

### 2.2 BVA cho password

| Nhóm | Giá trị | Ý nghĩa | Kết quả mong đợi |
| ---- | ------- | ------- | ---------------- |
| Dưới biên | `12345` | Password 5 ký tự | 400 hoặc 401 tùy validate |
| Tại biên | `123456` | Password 6 ký tự | 201 khi register hoặc 200 khi login nếu hợp lệ |
| Trên biên | `1234567` | Password 7 ký tự | 201/200 nếu hợp lệ |

### 2.3 BVA cho cập nhật profile

| Nhóm | Giá trị | Ý nghĩa | Kết quả mong đợi |
| ---- | ------- | ------- | ---------------- |
| Body đầy đủ | Có đủ `full_name`, `phone_number`, `address`, `vehicle_model`, `vin_number` | Dữ liệu cập nhật đầy đủ | 200 OK |
| Body thiếu vài field | Chỉ có `full_name` | Cập nhật partial | 200 OK |
| Body rỗng | `{}` | Không có dữ liệu cập nhật | 400 Bad Request nếu validate chặt |
| Không token | Không gửi Authorization | Chưa xác thực | 401 Unauthorized |

---

## Câu 3. Thiết kế test case

### 3.1 Test case cho chức năng xác thực

| STT | Mã test case | Mô tả | Request | Dữ liệu đầu vào | Expected | Actual/Ghi chú | Trạng thái |
| --: | ------------ | ----- | ------- | --------------- | -------- | -------------- | ---------- |
| 1 | ESC-6 | Đăng ký tài khoản mới | `POST /api/register` | email, username, password | 201 Created | Theo Postman script expected 201 | Pass nếu dữ liệu chưa tồn tại |
| 2 | ESC-7 | Đăng nhập | `POST /api/login` | email_username, password | 200 OK + token | Token được lưu vào environment | Pass nếu user tồn tại |
| 3 | ESC-8 | Gửi OTP | `POST /api/send-otp` | email tồn tại | 200 OK | Script đang expected 201 | Fail do script sai expected |
| 4 | TC-USER-003 | Thiếu email_username | `POST /api/login` | `{}` | 400 Bad Request | API có validate thiếu field | Pass |
| 5 | BVA-LOGIN-05 | Tài khoản không tồn tại | `POST /api/login` | user không tồn tại | 401 Unauthorized | API trả Invalid credentials | Pass |
| 6 | BVA-OTP-04 | Thiếu email | `POST /api/send-otp` | `{}` | 400 Bad Request | API trả Email is required | Pass |

### 3.2 Test case cho hồ sơ cá nhân

| STT | Mã test case | Mô tả | Request | Dữ liệu đầu vào | Expected | Actual/Ghi chú | Trạng thái |
| --: | ------------ | ----- | ------- | --------------- | -------- | -------------- | ---------- |
| 1 | ESC-43 | Lấy hồ sơ cá nhân | `GET /api/profile` | Token hợp lệ | 200 OK | Script kiểm tra `username` không có trong response profile | Fail nếu giữ assertion cũ |
| 2 | ESC-44 | Cập nhật hồ sơ cá nhân | `PUT /api/profile` | Body đầy đủ | 200 OK | Collection đang để method GET | Fail nếu chưa sửa method |
| 3 | BVA-PROFILE-01 | Body đầy đủ | `PUT /api/profile` | full profile | 200 hoặc 400 tùy validate | Dùng để kiểm tra validate phone/VIN | Cần xác nhận runtime |
| 4 | BVA-PROFILE-02 | Body thiếu vài field | `PUT /api/profile` | chỉ `full_name` | 200 OK | API hiện hỗ trợ partial update | Pass |
| 5 | BVA-PROFILE-03 | Body rỗng | `PUT /api/profile` | `{}` | 400 nếu validate chặt | API hiện có thể trả 200 no-op | Cần rà soát expected |
| 6 | BVA-PROFILE-04 | Không token | `PUT /api/profile` | Không Authorization | 401 Unauthorized | JWT xử lý thiếu token | Pass/Fail tùy script |

### 3.3 Test case cho admin quản lý user

| STT | Mã test case | Mô tả | Request | Dữ liệu đầu vào | Expected | Actual/Ghi chú | Trạng thái |
| --: | ------------ | ----- | ------- | --------------- | -------- | -------------- | ---------- |
| 1 | ESC-45 | Admin lấy danh sách user | `GET /api/admin/users` | Admin token | 200 OK | Response là JSON array | Pass |
| 2 | ESC-46 | Khóa/mở khóa user | `PUT /api/admin/users/15/toggle-lock` | Admin token | 200 OK | Backend trả user object, script đòi `message` | Fail nếu giữ assertion cũ |
| 3 | BVA-LOCK-01 | User ID = 0 | `PUT /api/admin/users/0/toggle-lock` | Admin token | 400 hoặc 404 | Không tìm thấy user | Pass nếu expected 404 |
| 4 | BVA-LOCK-02 | User ID = 1 | `PUT /api/admin/users/1/toggle-lock` | Admin token | 200 nếu tồn tại | Toggle status active/locked | Pass nếu user tồn tại |
| 5 | BVA-LOCK-03 | User ID = 99999 | `PUT /api/admin/users/99999/toggle-lock` | Admin token | 404 Not Found | Không tìm thấy người dùng | Pass |

---

## Câu 4. Bảng mô tả lỗi

| Mã lỗi | Tên lỗi | Test case | Expected | Actual | Nguyên nhân | Mức độ |
| ------ | ------- | --------- | -------- | ------ | ----------- | ------ |
| BUG-USER-01 | Send OTP expected sai status | ESC-8 | 200 OK | Script check 201 | Test script copy từ ESC-6 hoặc chưa cập nhật theo API | Medium |
| BUG-USER-02 | Lấy profile check sai field | ESC-43 | Body profile hợp lệ | Script check `username` | API trả profile, không trả user account | Medium |
| BUG-USER-03 | Cập nhật profile dùng sai HTTP method | ESC-44 | PUT `/api/profile` | Collection đang để GET | Cấu hình Postman sai method | High |
| BUG-USER-04 | Toggle lock response không có `message` | ESC-46 | Có message hoặc kiểm tra status user | Backend trả user object | Không thống nhất contract response/test script | Low/Medium |

---

## Câu 5. Phân tích nguyên nhân trong source code

File liên quan:

```text
EV-Service-Center-Full/services/user-service/controllers/controllers_api.py
```

### 5.1 API gửi OTP

Controller:

```python
@api_bp.route("/send-otp", methods=["POST"])
def send_otp():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    success, message = UserLogic.send_reset_otp(email)
    if not success:
        return jsonify(error=message), 404
    return jsonify(message=message), 200
```

Vấn đề nằm ở Postman script: API trả 200 nhưng script đang expected 201.

### 5.2 API lấy profile

Controller:

```python
@api_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_my_profile():
    current_user_id = get_jwt_identity()
    profile = ProfileLogic.get_profile_by_user_id(current_user_id)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(serialize_profile(profile)), 200
```

Serializer:

```python
def serialize_profile(profile):
    return {
        "user_id": profile.user_id,
        "full_name": profile.full_name,
        "phone_number": profile.phone_number,
        "address": profile.address,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "vehicle_model": getattr(profile, "vehicle_model", None),
        "vin_number": getattr(profile, "vin_number", None)
    }
```

Vì serializer không có `username`, test script không nên kiểm tra field `username` nếu API contract là trả profile.

### 5.3 API cập nhật profile

Controller:

```python
@api_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_my_profile():
    current_user_id = get_jwt_identity()
    profile, error = ProfileLogic.update_profile(current_user_id, request.json)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({"message": "Profile updated", "profile": serialize_profile(profile)}), 200
```

Endpoint đúng là `PUT /api/profile`. Nếu Postman dùng GET thì không thể cập nhật profile và sẽ không có `message`.

### 5.4 API toggle lock

Controller:

```python
@api_bp.route("/admin/users/<string:user_id>/toggle-lock", methods=["PUT"])
@admin_required()
def toggle_user_lock_account(user_id):
    user, error = UserLogic.toggle_user_lock(user_id)
    if error:
        return jsonify(error=error), 404
    return jsonify(serialize_user(user)), 200
```

Backend trả trực tiếp object user. Nếu muốn test kiểm tra message thì backend nên bọc response có `message`.

---

## Câu 6. Đề xuất hướng khắc phục

## 6.1 Sửa testcase Postman cho ESC-8

Đổi expected từ 201 sang 200:

```javascript
pm.test("[ESC-8] Gửi OTP thành công - Mã trả về phải là 200 OK", function () {
    pm.response.to.have.status(200);
});
```

## 6.2 Sửa testcase Postman cho ESC-43

Đổi assertion:

```javascript
pm.test("[ESC-43] Lấy hồ sơ cá nhân thành công", function () {
    pm.response.to.have.status(200);
    const data = pm.response.json();
    pm.expect(data).to.have.property("user_id");
    pm.expect(data).to.have.property("full_name");
});
```

## 6.3 Sửa method Postman cho ESC-44

Cấu hình lại request:

```text
Method: PUT
URL: {{base_url}}/api/profile
Authorization: Bearer Token
Body: raw JSON
```

## 6.4 Chuẩn hóa response toggle lock

Nếu chọn sửa backend, đổi controller thành:

```python
return jsonify({
    "message": "User lock status updated",
    "user": serialize_user(user)
}), 200
```

Nếu chọn sửa test script, đổi assertion thành:

```javascript
pm.test("Response có trạng thái tài khoản", function () {
    const data = pm.response.json();
    pm.expect(data).to.have.property("status");
});
```

## 6.5 Validate body rỗng khi update profile

Hiện tại `ProfileService.update_profile()` cho phép body rỗng và commit không thay đổi dữ liệu. Nếu nghiệp vụ yêu cầu body rỗng là lỗi, nên thêm:

```python
if not profile_data:
    return None, "Body không được rỗng"
```

và controller trả 400 thay vì 404 cho lỗi validate.

---

## Câu 7. Thiết kế kiểm thử tự động

### 7.1 Unit test validate email

```python
import re


def is_valid_email(email):
    if not email:
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


def test_email_valid():
    assert is_valid_email("user@gmail.com") is True


def test_email_missing_at():
    assert is_valid_email("usergmail.com") is False


def test_email_missing_domain():
    assert is_valid_email("user@") is False
```

### 7.2 API test đăng nhập thiếu field

```python
def test_login_missing_email_username_should_return_400(client):
    response = client.post("/api/login", json={})

    assert response.status_code == 400
    assert "error" in response.get_json()
```

### 7.3 API test gửi OTP thiếu email

```python
def test_send_otp_missing_email_should_return_400(client):
    response = client.post("/api/send-otp", json={})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Email is required"
```

### 7.4 API test profile không token

```python
def test_update_profile_without_token_should_return_401(client):
    response = client.put("/api/profile", json={"full_name": "Nguyen Van A"})

    assert response.status_code == 401
```

### 7.5 API test admin toggle user không tồn tại

```python
def test_admin_toggle_user_not_found_should_return_404(client, admin_token):
    response = client.put(
        "/api/admin/users/99999/toggle-lock",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404
```

---

## Câu 8. Kịch bản kiểm thử Postman

### 8.1 Chuẩn bị

1. Chạy hệ thống backend bằng Docker Compose.
2. Đăng ký hoặc seed tài khoản admin/user.
3. Đăng nhập bằng API `/api/login`.
4. Lưu token vào Postman environment:

```text
admin_token
staff_token
user_token
```

5. Với API cần xác thực, dùng Authorization type `Bearer Token`.

### 8.2 Test đăng ký tài khoản

Request:

```http
POST http://localhost/api/register
Content-Type: application/json

{
  "email": "ga@gmai.com",
  "username": "user12",
  "password": "12345"
}
```

Expected:

```text
Status: 201 Created nếu dữ liệu hợp lệ và chưa trùng
Body có message và user
```

### 8.3 Test đăng nhập

Request:

```http
POST http://localhost/api/login
Content-Type: application/json

{
  "email_username": "staf111",
  "password": "12345"
}
```

Expected:

```text
Status: 200 OK
Body có access_token
```

### 8.4 Test gửi OTP

Request:

```http
POST http://localhost/api/send-otp
Content-Type: application/json

{
  "email": "testuser_nhom7@gmail.com"
}
```

Expected:

```text
Status: 200 OK
Body có message
```

### 8.5 Test lấy profile

Request:

```http
GET http://localhost/api/profile
Authorization: Bearer <token>
```

Expected:

```text
Status: 200 OK
Body có user_id, full_name, phone_number, address, vehicle_model, vin_number
```

### 8.6 Test cập nhật profile

Request:

```http
PUT http://localhost/api/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Trần Bảo Long",
  "phone_number": "0912345678",
  "address": "Thành phố Hồ Chí Minh",
  "vehicle_model": "VinFast VF8",
  "vin_number": "VIN888777666"
}
```

Expected:

```text
Status: 200 OK
Body có message = Profile updated
```

### 8.7 Test admin toggle lock

Request:

```http
PUT http://localhost/api/admin/users/15/toggle-lock
Authorization: Bearer <admin_token>
```

Expected:

```text
Status: 200 OK
Body trả user đã đổi status hoặc message + user
```

---

# PHẦN B. KẾT QUẢ KIỂM THỬ

## 1. Tổng hợp kết quả

Dựa trên Postman collection và đối chiếu source code User Service, kết quả tạm tổng hợp như sau:

| Tổng số testcase chính | Pass/Expected pass | Fail cần rà soát | Ghi chú |
| ---------------------- | ------------------ | ---------------- | ------- |
| 21 | 13 | 4 lỗi chính | Một số testcase BVA đang dùng expected rộng `[200, 400, 401, 403, 404, 409]` nên cần chuẩn hóa expected để đánh giá chính xác |

## 2. Danh sách testcase fail/cần sửa

| Mã test case | Lỗi | Expected đúng | Cần sửa |
| ------------ | --- | ------------- | ------- |
| ESC-8 | Send OTP script expected 201 | 200 OK | Sửa script Postman |
| ESC-43 | Script kiểm tra `username` | Kiểm tra field profile | Sửa script hoặc backend response |
| ESC-44 | Request cập nhật profile đang là GET | PUT `/api/profile` | Sửa method trong Postman |
| ESC-46 | Script yêu cầu `message` nhưng backend trả user | Kiểm tra `status` hoặc backend bọc message | Thống nhất response contract |

## 3. Đánh giá

Các lỗi chính không phải đều là lỗi crash backend. Phần lớn là lỗi không thống nhất giữa **API contract** và **Postman test script**:

* Backend gửi OTP trả 200 nhưng script kiểm tra 201.
* Endpoint profile trả profile nhưng script kiểm tra username.
* Request update profile cấu hình nhầm method.
* API toggle lock trả user object nhưng script kiểm tra message.

Những lỗi này vẫn quan trọng vì khi chạy Newman/GitHub Actions, test fail sẽ tự tạo Bug trên Jira, ảnh hưởng báo cáo CI/CD.

---

# PHẦN C. KẾT LUẬN

Qua bài kiểm thử User Service, em đã áp dụng được các kỹ thuật:

* Phân hoạch lớp tương đương.
* Phân tích giá trị biên.
* Thiết kế test case cho API authentication/profile/admin.
* Kiểm thử API bằng Postman.
* Phân tích lỗi dựa trên source code.
* Đề xuất hướng sửa và kiểm thử tự động.

Kết quả kiểm thử cho thấy User Service có các chức năng cốt lõi: đăng ký, đăng nhập, gửi OTP, xem/cập nhật hồ sơ và admin quản lý tài khoản. Tuy nhiên, một số testcase Postman chưa khớp với backend hiện tại, dẫn đến lỗi khi chạy tự động bằng Newman.

Các lỗi quan trọng cần xử lý trước là:

1. ESC-8: sửa expected status của API gửi OTP từ 201 sang 200.
2. ESC-43: sửa assertion profile, không kiểm tra `username` nếu API chỉ trả profile.
3. ESC-44: đổi method request từ GET sang PUT.
4. ESC-46: thống nhất response toggle lock: trả message + user hoặc sửa test script kiểm tra `status`.

Sau khi sửa, cần chạy lại Postman collection và workflow GitHub Actions để tự động cập nhật trạng thái Jira: testcase pass chuyển DONE, testcase fail tạo Bug.
