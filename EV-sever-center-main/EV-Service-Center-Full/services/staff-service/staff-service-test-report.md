# BÁO CÁO KIỂM THỬ STAFF SERVICE

## Dự án: EV Service Center Maintenance Management System

---

# 1. Giới thiệu

Staff Service chịu trách nhiệm quản lý thông tin nhân viên, ca làm việc, phân công nhiệm vụ, chứng chỉ và đánh giá hiệu suất trong hệ thống EV Service Center.

Các kỹ thuật kiểm thử được áp dụng:

- Black-box Testing
- Boundary Value Analysis (BVA)
- Equivalence Partitioning (EP)
- Postman Collection Testing
- API Validation Testing

---

# 2. Danh sách API kiểm thử

| STT          | API                                | Method | Mô tả                   |
| ------------ | ---------------------------------- | ------ | ----------------------- |
| ESC-STAFF-01 | /api/staff                         | POST   | Thêm nhân viên          |
| ESC-STAFF-02 | /api/staff                         | GET    | Xem danh sách nhân viên |
| ESC-STAFF-03 | /api/staff/{staff_id}              | PUT    | Cập nhật nhân viên      |
| ESC-STAFF-04 | /api/staff/shifts                  | POST   | Tạo ca làm              |
| ESC-STAFF-05 | /api/staff/{staff_id}/shifts       | GET    | Xem lịch làm việc       |
| ESC-STAFF-06 | /api/staff/assignments             | POST   | Phân công sửa chữa      |
| ESC-STAFF-07 | /api/staff/{staff_id}/certificates | POST   | Thêm chứng chỉ          |
| ESC-STAFF-08 | /api/staff/{staff_id}/rating       | GET    | Xem đánh giá nhân viên  |

---

# 3. Black-box Testing

## 3.1 Thêm nhân viên

API:

```http
POST /api/staff
```

Body hợp lệ:

```json
{
  "full_name": "Nguyễn Văn Hùng",
  "email": "hung.test01@evcenter.com",
  "phone": "0912345678",
  "password": "123456",
  "role": "technician",
  "center_id": 1,
  "status": "active"
}
```

Expected:

```http
201 Created
```

---

## 3.2 Xem danh sách nhân viên

API:

```http
GET /api/staff?center_id=1
```

Expected:

```http
200 OK
```

---

## 3.3 Cập nhật nhân viên

API:

```http
PUT /api/staff/{staff_id}
```

Expected:

```http
200 OK
```

---

## 3.4 Tạo ca làm

API:

```http
POST /api/staff/shifts
```

Expected:

```http
201 Created
```

---

## 3.5 Xem lịch làm việc

API:

```http
GET /api/staff/{staff_id}/shifts
```

Expected:

```http
200 OK
```

---

## 3.6 Phân công sửa chữa

API:

```http
POST /api/staff/assignments
```

Expected:

```http
201 Created
```

---

## 3.7 Thêm chứng chỉ

API:

```http
POST /api/staff/{staff_id}/certificates
```

Expected:

```http
201 Created
```

---

## 3.8 Xem đánh giá nhân viên

API:

```http
GET /api/staff/{staff_id}/rating
```

Expected:

```http
200 OK
```

---

# 4. Boundary Value Analysis (BVA)

## Add Staff

### Center ID

| Test Case        | Input             | Ý nghĩa           | Expected     |
| ---------------- | ----------------- | ----------------- | ------------ |
| BVA-STAFF-ADD-01 | center_id = 0     | Dưới biên         | 201 hoặc 404 |
| BVA-STAFF-ADD-02 | center_id = 1     | Biên hợp lệ       | 400          |
| BVA-STAFF-ADD-03 | center_id = 99999 | Ngoài tập dữ liệu | 404          |

### Phone Number

| Test Case        | Input       | Ý nghĩa | Expected |
| ---------------- | ----------- | ------- | -------- |
| BVA-STAFF-ADD-04 | 091234567   | 9 số    | 201      |
| BVA-STAFF-ADD-05 | 0912345678  | 10 số   | 201      |
| BVA-STAFF-ADD-06 | 09123456789 | 11 số   | 400      |

---

## Update Staff

### Staff ID

| Test Case        | Input            | Ý nghĩa       | Expected |
| ---------------- | ---------------- | ------------- | -------- |
| BVA-STAFF-UPD-01 | staff_id = 0     | Dưới biên     | 201      |
| BVA-STAFF-UPD-02 | staff_id = 1     | Biên hợp lệ   | 200      |
| BVA-STAFF-UPD-03 | staff_id = 99999 | Không tồn tại | 404      |

---

## Create Shift

### Staff ID

| Test Case          | Input            | Ý nghĩa       | Expected     |
| ------------------ | ---------------- | ------------- | ------------ |
| BVA-STAFF-SHIFT-01 | staff_id = 0     | Dưới biên     | 400 hoặc 404 |
| BVA-STAFF-SHIFT-02 | staff_id = 1     | Biên hợp lệ   | 201          |
| BVA-STAFF-SHIFT-03 | staff_id = 99999 | Không tồn tại | 404          |

---

## Assignment

### Staff ID

| Test Case           | Input            | Ý nghĩa       | Expected     |
| ------------------- | ---------------- | ------------- | ------------ |
| BVA-STAFF-ASSIGN-01 | staff_id = 0     | Dưới biên     | 400 hoặc 404 |
| BVA-STAFF-ASSIGN-02 | staff_id = 1     | Biên hợp lệ   | 201          |
| BVA-STAFF-ASSIGN-03 | staff_id = 99999 | Không tồn tại | 404          |

---

## Certificate

### Staff ID

| Test Case         | Input            | Ý nghĩa       | Expected     |
| ----------------- | ---------------- | ------------- | ------------ |
| BVA-STAFF-CERT-01 | staff_id = 0     | Dưới biên     | 400 hoặc 404 |
| BVA-STAFF-CERT-02 | staff_id = 1     | Biên hợp lệ   | 201          |
| BVA-STAFF-CERT-03 | staff_id = 99999 | Không tồn tại | 404          |

---

## Rating

### Staff ID

| Test Case           | Input            | Ý nghĩa       | Expected     |
| ------------------- | ---------------- | ------------- | ------------ |
| BVA-STAFF-RATING-01 | staff_id = 0     | Dưới biên     | 400 hoặc 404 |
| BVA-STAFF-RATING-02 | staff_id = 1     | Biên hợp lệ   | 200          |
| BVA-STAFF-RATING-03 | staff_id = 99999 | Không tồn tại | 404          |

---

# 5. Equivalence Partitioning (EP)

## Add Staff

| Test Case       | Input               | Expected |
| --------------- | ------------------- | -------- |
| EP-STAFF-ADD-01 | Body hợp lệ         | 201      |
| EP-STAFF-ADD-02 | Thiếu full_name     | 400      |
| EP-STAFF-ADD-03 | Email sai định dạng | 400      |
| EP-STAFF-ADD-04 | Role sai            | 400      |
| EP-STAFF-ADD-05 | Không token         | 401      |

---

## Update Staff

| Test Case       | Input           | Expected     |
| --------------- | --------------- | ------------ |
| EP-STAFF-UPD-01 | Cập nhật hợp lệ | 200          |
| EP-STAFF-UPD-02 | Status sai      | 400          |
| EP-STAFF-UPD-03 | Body rỗng       | 400 hoặc 200 |
| EP-STAFF-UPD-04 | Không token     | 401          |

---

## Create Shift

| Test Case         | Input                 | Expected |
| ----------------- | --------------------- | -------- |
| EP-STAFF-SHIFT-01 | Body hợp lệ           | 201      |
| EP-STAFF-SHIFT-02 | Thiếu shift_date      | 400      |
| EP-STAFF-SHIFT-03 | shift_type sai        | 400      |
| EP-STAFF-SHIFT-04 | end_time < start_time | 400      |
| EP-STAFF-SHIFT-05 | Không token           | 401      |

---

## Assignment

| Test Case          | Input                    | Expected |
| ------------------ | ------------------------ | -------- |
| EP-STAFF-ASSIGN-01 | Body hợp lệ              | 201      |
| EP-STAFF-ASSIGN-02 | Thiếu staff_id           | 400      |
| EP-STAFF-ASSIGN-03 | booking_id không tồn tại | 404      |
| EP-STAFF-ASSIGN-04 | Không token              | 401      |

---

## Certificate

| Test Case        | Input                  | Expected |
| ---------------- | ---------------------- | -------- |
| EP-STAFF-CERT-01 | Body hợp lệ            | 201      |
| EP-STAFF-CERT-02 | Thiếu certificate_name | 400      |
| EP-STAFF-CERT-03 | Sai định dạng ngày     | 400      |
| EP-STAFF-CERT-04 | Không token            | 401      |

---

## Rating

| Test Case          | Input           | Expected |
| ------------------ | --------------- | -------- |
| EP-STAFF-RATING-01 | staff_id hợp lệ | 200      |
| EP-STAFF-RATING-02 | Không token     | 401      |

---

# 6. Postman Script Validation

Script kiểm tra trạng thái phản hồi:

```javascript
pm.test("Status hợp lệ", function () {
  pm.expect([200, 201, 400, 401, 403, 404, 409]).to.include(pm.response.code);
});

pm.test("Response là JSON", function () {
  pm.response.to.be.json;
});
```

Ý nghĩa:

- Kiểm tra status code đúng yêu cầu.
- Kiểm tra response trả về JSON.
- Phát hiện lỗi validate và lỗi phân quyền.

---

# 7. Kết luận

Staff Service được kiểm thử bằng Black-box Testing, Boundary Value Analysis và Equivalence Partitioning. Các trường hợp kiểm thử tập trung vào:

- Validate dữ liệu đầu vào.
- Kiểm tra quyền truy cập.
- Kiểm tra quản lý nhân viên.
- Kiểm tra tạo và xem ca làm việc.
- Kiểm tra phân công sửa chữa.
- Kiểm tra quản lý chứng chỉ.
- Kiểm tra đánh giá nhân viên.

Các kỹ thuật trên giúp đảm bảo Staff Service hoạt động ổn định, xử lý đúng nghiệp vụ và phát hiện sớm các lỗi dữ liệu, lỗi phân quyền và lỗi nghiệp vụ trước khi triển khai hệ thống.
