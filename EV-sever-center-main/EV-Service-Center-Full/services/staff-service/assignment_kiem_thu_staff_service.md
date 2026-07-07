# Assignment: Kiểm thử chức năng Staff Service

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

1. Xác định điều kiện kiểm thử cho chức năng quản lý nhân sự trong Staff Service.
2. Áp dụng kỹ thuật phân hoạch lớp tương đương để chia dữ liệu đầu vào hợp lệ và không hợp lệ.
3. Áp dụng kỹ thuật phân tích giá trị biên cho các tham số `staff_id`, `center_id`, dữ liệu ca làm, giao việc, chứng chỉ và đánh giá.
4. Thiết kế test case cho các API quản lý nhân viên, ca làm, lịch làm việc, giao việc, chứng chỉ và điểm đánh giá.
5. Ghi nhận các lỗi thực tế khi kiểm thử bằng Postman và đồng bộ trạng thái lên Jira.
6. Đề xuất hướng xử lý lỗi và kiểm thử lại sau khi sửa.

---

# 2. Nội dung tham khảo

Trong bài này em áp dụng các kỹ thuật kiểm thử sau:

* **Equivalence Partitioning:** chia dữ liệu đầu vào thành nhóm hợp lệ và không hợp lệ.
* **Boundary Value Analysis (BVA):** kiểm thử giá trị biên như `staff_id = 0`, `staff_id = 1`, `staff_id = 99999`.
* **API Testing:** kiểm thử endpoint bằng Postman với token xác thực.
* **Negative Testing:** kiểm thử trường hợp thiếu trường bắt buộc, sai định dạng, không token, id không tồn tại.
* **Defect Tracking:** ghi nhận testcase fail và chuyển trạng thái lỗi trên Jira.

---

# 3. Mô tả bài toán

Hệ thống EV Service Center có **Staff Service** dùng để quản lý nhân sự, ca làm việc, phân công công việc, chứng chỉ kỹ thuật và đánh giá hiệu suất nhân viên.

Các nhóm chức năng chính:

| Nhóm chức năng | Endpoint chính | Method | Mô tả |
| -------------- | -------------- | ------ | ----- |
| Quản lý nhân viên | `/api/staff/` | GET/POST | Lấy danh sách và thêm nhân viên |
| Cập nhật nhân viên | `/api/staff/<staff_id>` | PUT | Cập nhật thông tin nhân viên |
| Quản lý ca làm | `/api/staff/shifts` | POST | Tạo ca làm việc cho nhân viên |
| Xem lịch làm việc | `/api/staff/<staff_id>/shifts` | GET | Lấy lịch làm việc theo nhân viên |
| Giao việc | `/api/staff/assignments` | POST | Giao booking/task cho nhân viên |
| Chứng chỉ | `/api/staff/<staff_id>/certificates` | POST | Thêm chứng chỉ cho nhân viên |
| Đánh giá | `/api/staff/<staff_id>/rating` | GET | Lấy điểm đánh giá nhân viên |

Phạm vi báo cáo tập trung vào các testcase Staff Service đã được đồng bộ từ Postman sang Jira, đặc biệt các testcase đang có trạng thái **BUG**.

---

# 4. Yêu cầu nghiệp vụ mong đợi

## 4.1 Quy tắc xác thực

* Các API quản lý Staff Service phải yêu cầu Bearer Token hợp lệ.
* Nếu thiếu token, API phải trả `401 Unauthorized`.
* Nếu token không đủ quyền, API phải trả `403 Forbidden`.

## 4.2 Quy tắc `staff_id`

| Biến đầu vào | Kiểu dữ liệu | Miền hợp lệ | Kết quả mong đợi |
| ------------ | ------------ | ----------- | ---------------- |
| `staff_id` | Integer | `staff_id >= 1` và tồn tại | 200/201 nếu dữ liệu hợp lệ |
| `staff_id = 0` | Integer | Không hợp lệ | 400 Bad Request hoặc 404 Not Found tùy endpoint |
| `staff_id = 99999` | Integer | Đúng kiểu nhưng không tồn tại | 404 Not Found |
| `staff_id = abc` | String | Sai kiểu | 400 Bad Request hoặc route không match |

## 4.3 Quy tắc dữ liệu ca làm

| Trường | Điều kiện hợp lệ |
| ------ | ---------------- |
| `staff_id` | Số nguyên dương, tồn tại |
| `shift_date` | Định dạng ngày hợp lệ |
| `shift_type` | Thuộc danh sách hợp lệ, ví dụ `morning`, `afternoon`, `evening` |
| `start_time` | Định dạng giờ hợp lệ |
| `end_time` | Phải sau `start_time` |

## 4.4 Quy tắc giao việc

| Trường | Điều kiện hợp lệ |
| ------ | ---------------- |
| `staff_id` | Số nguyên dương, tồn tại |
| `booking_id` hoặc `task_id` | Tồn tại trong hệ thống liên quan |
| `note` | Có thể có hoặc không tùy thiết kế |

## 4.5 Quy tắc chứng chỉ

| Trường | Điều kiện hợp lệ |
| ------ | ---------------- |
| `certificate_name` | Bắt buộc |
| `issued_by` | Bắt buộc hoặc tùy thiết kế |
| `issued_date` | Định dạng ngày hợp lệ |
| `expiry_date` | Định dạng ngày hợp lệ và sau ngày cấp |

---

# 5. Danh sách API kiểm thử trong Postman

| STT | Mã nhóm | Method | Endpoint | Mô tả |
| --: | ------ | ------ | -------- | ----- |
| 1 | Staff Add | POST | `/api/staff/` | Thêm nhân viên |
| 2 | Staff List | GET | `/api/staff/?center_id=1` | Lấy danh sách nhân viên theo trung tâm |
| 3 | Staff Update | PUT | `/api/staff/1` | Cập nhật thông tin nhân viên |
| 4 | Staff Shift | POST | `/api/staff/shifts` | Tạo ca làm cho nhân viên |
| 5 | Staff Schedule | GET | `/api/staff/1/shifts` | Lấy lịch làm việc của nhân viên |
| 6 | Staff Assign | POST | `/api/staff/assignments` | Giao việc cho nhân viên |
| 7 | Staff Certificate | POST | `/api/staff/1/certificates` | Thêm chứng chỉ cho nhân viên |
| 8 | Staff Rating | GET | `/api/staff/1/rating` | Lấy điểm đánh giá nhân viên |

---

# 6. Kết quả kiểm thử ghi nhận từ Jira

Các testcase Staff Service sau đang có trạng thái **BUG** tại thời điểm ghi nhận:

| Jira Key | Mã test case | Mô tả | Trạng thái |
| -------- | ------------ | ----- | ---------- |
| ESCT-157 | BVA-STAFF-UPD-01 | `staff_id = 0` | BUG |
| ESCT-160 | EP-STAFF-UPD-03 | Body rỗng | BUG |
| ESCT-162 | EP-STAFF-SHIFT-01 | Body hợp lệ | BUG |
| ESCT-163 | BVA-STAFF-SHIFT-01 | `staff_id = 0` | BUG |
| ESCT-164 | BVA-STAFF-SHIFT-02 | `staff_id = 1` | BUG |
| ESCT-169 | EP-STAFF-SCHEDULE-01 | `staff_id` hợp lệ | BUG |
| ESCT-170 | BVA-STAFF-SCHEDULE-01 | `staff_id = 0` | BUG |
| ESCT-173 | EP-STAFF-ASSIGN-01 | Body hợp lệ | BUG |
| ESCT-174 | BVA-STAFF-ASSIGN-01 | `staff_id = 0` | BUG |
| ESCT-175 | BVA-STAFF-ASSIGN-02 | `staff_id = 1` | BUG |
| ESCT-176 | EP-STAFF-ASSIGN-02 | Thiếu `staff_id` | BUG |
| ESCT-179 | EP-STAFF-CERT-01 | Body hợp lệ | BUG |
| ESCT-180 | BVA-STAFF-CERT-01 | `staff_id = 0` | BUG |
| ESCT-181 | BVA-STAFF-CERT-02 | `staff_id = 1` | BUG |
| ESCT-185 | EP-STAFF-RATING-01 | `staff_id` hợp lệ | BUG |
| ESCT-186 | BVA-STAFF-RATING-01 | `staff_id = 0` | BUG |

Các testcase khác như `EP-STAFF-UPD-02 status sai`, `EP-STAFF-UPD-04 Không token`, `EP-STAFF-SHIFT-02 Thiếu shift_date`, `EP-STAFF-SHIFT-03 shift_type sai`, `EP-STAFF-SHIFT-04 end_time trước start_time`, `EP-STAFF-SHIFT-05 Không token`, `BVA-STAFF-SCHEDULE-02 staff_id = 99999`, `EP-STAFF-SCHEDULE-02 Không token`, `EP-STAFF-ASSIGN-03 booking_id/task_id không tồn tại`, `EP-STAFF-ASSIGN-04 Không token`, `EP-STAFF-CERT-02 Thiếu certificate_name`, `EP-STAFF-CERT-03 Ngày hết hạn sai định dạng`, `EP-STAFF-CERT-04 Không token`, `BVA-STAFF-RATING-02 staff_id = 99999`, `EP-STAFF-RATING-02 Không token` đang được ghi nhận là **DONE**.

---

# 7. Mô tả lỗi phát hiện

## 7.1 BUG-STAFF-01: Cập nhật nhân viên với `staff_id = 0`

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-157 |
| Testcase | BVA-STAFF-UPD-01 |
| Method | PUT |
| Endpoint | `/api/staff/0` |
| Dữ liệu đầu vào | `{ "phone": "0988888888", "status": "active" }` |
| Expected | 400 Bad Request hoặc 404 Not Found |
| Actual | Testcase fail |
| Mức độ | Medium |

### Phân tích

`staff_id = 0` là giá trị biên dưới không hợp lệ vì ID trong database thường bắt đầu từ 1. API cần validate rõ ràng trước khi xử lý cập nhật.

### Đề xuất sửa

* Nếu `staff_id <= 0`, trả `400 Bad Request` với message rõ ràng.
* Nếu `staff_id > 0` nhưng không tồn tại, trả `404 Not Found`.

---

## 7.2 BUG-STAFF-02: Cập nhật nhân viên với body rỗng

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-160 |
| Testcase | EP-STAFF-UPD-03 |
| Method | PUT |
| Endpoint | `/api/staff/1` |
| Dữ liệu đầu vào | `{}` |
| Expected | 400 Bad Request |
| Actual | Testcase fail |
| Mức độ | Medium |

### Phân tích

Body rỗng không có trường nào để cập nhật. Nếu API vẫn trả thành công hoặc xử lý không rõ ràng thì frontend/QA không biết dữ liệu có thực sự được thay đổi hay không.

### Đề xuất sửa

Thêm validate:

```python
if not data:
    return jsonify({"error": "Body không được rỗng"}), 400
```

---

## 7.3 BUG-STAFF-03: Tạo ca làm với body hợp lệ nhưng fail

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-162 |
| Testcase | EP-STAFF-SHIFT-01 |
| Method | POST |
| Endpoint | `/api/staff/shifts` |
| Dữ liệu đầu vào | `staff_id = 20`, `shift_date = 2026-06-01`, `shift_type = morning`, `start_time = 08:00:00`, `end_time = 12:00:00` |
| Expected | 201 Created hoặc 200 OK |
| Actual | Testcase fail |
| Mức độ | High |

### Phân tích

Đây là testcase hợp lệ. Lỗi có thể đến từ một trong các nguyên nhân:

* Nhân viên `staff_id = 20` chưa tồn tại trong database.
* Controller không map đúng endpoint `/api/staff/shifts`.
* Service validate `shift_type`, `shift_date`, `start_time`, `end_time` chưa nhất quán với dữ liệu Postman.
* Có lỗi ràng buộc database khi tạo ca làm.

### Đề xuất sửa

* Đảm bảo dữ liệu seed có nhân viên `staff_id = 20` hoặc đổi testcase dùng `staff_id` đang tồn tại.
* Nếu nhân viên không tồn tại, API phải trả `404` thay vì lỗi server.
* Nếu dữ liệu hợp lệ, API phải tạo ca làm và trả response đúng.

---

## 7.4 BUG-STAFF-04: Tạo ca làm với `staff_id = 0`

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-163 |
| Testcase | BVA-STAFF-SHIFT-01 |
| Method | POST |
| Endpoint | `/api/staff/shifts` |
| Dữ liệu đầu vào | `staff_id = 0` |
| Expected | 400 Bad Request |
| Actual | Testcase fail |
| Mức độ | Medium |

### Phân tích

`staff_id = 0` là giá trị không hợp lệ. API cần kiểm tra ID trước khi tạo ca làm.

### Đề xuất sửa

```python
if staff_id <= 0:
    return jsonify({"error": "staff_id phải lớn hơn 0"}), 400
```

---

## 7.5 BUG-STAFF-05: Tạo ca làm với `staff_id = 1`

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-164 |
| Testcase | BVA-STAFF-SHIFT-02 |
| Method | POST |
| Endpoint | `/api/staff/shifts` |
| Dữ liệu đầu vào | `staff_id = 1` |
| Expected | 201 Created hoặc 200 OK nếu staff tồn tại |
| Actual | Testcase fail |
| Mức độ | High |

### Phân tích

`staff_id = 1` là biên hợp lệ nhỏ nhất. Nếu nhân viên tồn tại thì API phải tạo ca làm thành công. Nếu fail, có thể do staff `1` không tồn tại, dữ liệu ca bị trùng, hoặc validate thời gian không phù hợp.

### Đề xuất sửa

* Kiểm tra seed database có nhân viên `id = 1`.
* Nếu không tồn tại, chỉnh expected thành `404` hoặc seed dữ liệu test.
* Nếu tồn tại, kiểm tra logic tạo ca làm.

---

## 7.6 BUG-STAFF-06: Xem lịch làm việc với `staff_id` hợp lệ

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-169 |
| Testcase | EP-STAFF-SCHEDULE-01 |
| Method | GET |
| Endpoint | `/api/staff/1/shifts` |
| Expected | 200 OK |
| Actual | Testcase fail |
| Mức độ | High |

### Phân tích

Testcase hợp lệ nhưng fail cho thấy endpoint lịch làm việc có thể chưa được đăng ký đúng, hoặc Postman đang gọi URL khác với route thực tế trong source code. Trong collection thường có API cũ `/api/shifts/?staff_id=1`, còn BVA lại dùng `/api/staff/1/shifts`. Cần thống nhất route.

### Đề xuất sửa

Chọn một thiết kế endpoint cố định:

```http
GET /api/staff/<staff_id>/shifts
```

hoặc

```http
GET /api/shifts/?staff_id=<staff_id>
```

Sau đó cập nhật cả controller và Postman cho thống nhất.

---

## 7.7 BUG-STAFF-07: Xem lịch làm việc với `staff_id = 0`

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-170 |
| Testcase | BVA-STAFF-SCHEDULE-01 |
| Method | GET |
| Endpoint | `/api/staff/0/shifts` |
| Expected | 400 Bad Request |
| Actual | Testcase fail |
| Mức độ | Medium |

### Phân tích

`staff_id = 0` là giá trị không hợp lệ. API cần validate trước khi query lịch làm.

---

## 7.8 BUG-STAFF-08: Giao việc với body hợp lệ nhưng fail

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-173 |
| Testcase | EP-STAFF-ASSIGN-01 |
| Method | POST |
| Endpoint | `/api/staff/assignments` |
| Body | `staff_id = 1`, `booking_id = 1`, `task_id = 1` |
| Expected | 201 Created hoặc 200 OK |
| Actual | Testcase fail |
| Mức độ | High |

### Phân tích

Body hợp lệ nhưng fail có thể do:

* `staff_id = 1` không tồn tại trong Staff Service.
* `booking_id = 1` hoặc `task_id = 1` không tồn tại ở Booking/Maintenance Service.
* Controller/service dùng tên field khác như `maintenance_id` thay vì `booking_id`/`task_id`.
* Endpoint Postman `/api/staff/assignments` khác với route đang đăng ký.

### Đề xuất sửa

* Thống nhất body request giữa Postman và controller.
* Nếu dùng `booking_id` và `task_id`, service phải validate và lưu đúng hai trường này.
* Nếu code dùng `maintenance_id`, cần sửa Postman hoặc sửa DTO API.

---

## 7.9 BUG-STAFF-09: Giao việc với `staff_id = 0`

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-174 |
| Testcase | BVA-STAFF-ASSIGN-01 |
| Method | POST |
| Endpoint | `/api/staff/assignments` |
| Dữ liệu đầu vào | `staff_id = 0` |
| Expected | 400 Bad Request |
| Actual | Testcase fail |
| Mức độ | Medium |

### Phân tích

API cần validate `staff_id > 0` trước khi tạo assignment.

---

## 7.10 BUG-STAFF-10: Giao việc với `staff_id = 1`

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-175 |
| Testcase | BVA-STAFF-ASSIGN-02 |
| Method | POST |
| Endpoint | `/api/staff/assignments` |
| Dữ liệu đầu vào | `staff_id = 1` |
| Expected | 201 Created hoặc 200 OK nếu dữ liệu liên quan tồn tại |
| Actual | Testcase fail |
| Mức độ | High |

### Phân tích

Nếu `staff_id = 1` tồn tại và `booking_id/task_id` tồn tại thì testcase phải pass. Nếu fail, cần kiểm tra dữ liệu seed hoặc mapping field.

---

## 7.11 BUG-STAFF-11: Giao việc thiếu `staff_id`

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-176 |
| Testcase | EP-STAFF-ASSIGN-02 |
| Method | POST |
| Endpoint | `/api/staff/assignments` |
| Body | Thiếu `staff_id` |
| Expected | 400 Bad Request |
| Actual | Testcase fail |
| Mức độ | Medium |

### Đề xuất sửa

```python
required_fields = ["staff_id", "booking_id", "task_id"]
missing = [field for field in required_fields if field not in data]
if missing:
    return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
```

---

## 7.12 BUG-STAFF-12: Thêm chứng chỉ với body hợp lệ nhưng fail

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-179 |
| Testcase | EP-STAFF-CERT-01 |
| Method | POST |
| Endpoint | `/api/staff/1/certificates` |
| Expected | 201 Created hoặc 200 OK |
| Actual | Testcase fail |
| Mức độ | High |

### Phân tích

Testcase hợp lệ fail có thể do:

* Route thực tế là `/api/certificates` nhưng Postman gọi `/api/staff/1/certificates`.
* Tên field trong body không khớp, ví dụ code dùng `name` nhưng testcase dùng `certificate_name`.
* `staff_id = 1` không tồn tại.

---

## 7.13 BUG-STAFF-13: Chứng chỉ với `staff_id = 0`

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-180 |
| Testcase | BVA-STAFF-CERT-01 |
| Method | POST |
| Endpoint | `/api/staff/1/certificates` theo collection, tên testcase ghi `staff_id = 0` |
| Expected | 400 Bad Request |
| Actual | Testcase fail |
| Mức độ | Medium |

### Phân tích

Cần kiểm tra lại Postman vì tên testcase ghi `staff_id = 0` nhưng URL trong collection đang có thể vẫn là `/api/staff/1/certificates`. Nếu dữ liệu test và URL không đồng nhất, testcase sẽ đánh giá sai.

---

## 7.14 BUG-STAFF-14: Chứng chỉ với `staff_id = 1`

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-181 |
| Testcase | BVA-STAFF-CERT-02 |
| Method | POST |
| Endpoint | `/api/staff/1/certificates` |
| Expected | 201 Created hoặc 200 OK nếu staff tồn tại |
| Actual | Testcase fail |
| Mức độ | High |

---

## 7.15 BUG-STAFF-15: Lấy rating với `staff_id` hợp lệ nhưng fail

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-185 |
| Testcase | EP-STAFF-RATING-01 |
| Method | GET |
| Endpoint | `/api/staff/1/rating` |
| Expected | 200 OK |
| Actual | Testcase fail |
| Mức độ | Medium |

### Phân tích

Có khả năng route thực tế trong Performance Controller là `/api/performance/staff/<staff_id>/current`, trong khi Postman gọi `/api/staff/<staff_id>/rating`. Nếu vậy cần bổ sung route alias hoặc chỉnh lại Postman.

---

## 7.16 BUG-STAFF-16: Lấy rating với `staff_id = 0`

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Jira Key | ESCT-186 |
| Testcase | BVA-STAFF-RATING-01 |
| Method | GET |
| Endpoint | `/api/staff/1/rating` theo collection, tên testcase ghi `staff_id = 0` |
| Expected | 400 Bad Request |
| Actual | Testcase fail |
| Mức độ | Medium |

### Phân tích

Tương tự nhóm chứng chỉ, cần kiểm tra Postman vì tên testcase và URL có thể không khớp. Nếu muốn test `staff_id = 0`, URL phải là:

```http
GET /api/staff/0/rating
```

---

# PHẦN A. BÀI LÀM

---

## Câu 1. Xác định lớp tương đương

### 1.1 Phân hoạch cho `staff_id`

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| `staff_id` | Số nguyên dương và tồn tại | V1 | `staff_id = 0` | X1 |
| | | | `staff_id < 0` | X2 |
| | | | `staff_id = 99999` không tồn tại | X3 |
| | | | Sai kiểu như `abc` | X4 |
| | | | Thiếu `staff_id` | X5 |

### 1.2 Phân hoạch cho token

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| Bearer Token | Token hợp lệ | V2 | Không có token | X6 |
| | | | Token sai | X7 |
| | | | Token hết hạn | X8 |

### 1.3 Phân hoạch cho ca làm

| Biến đầu vào | Lớp hợp lệ | Lớp không hợp lệ |
| ------------ | ---------- | ---------------- |
| `shift_date` | Ngày hợp lệ | Thiếu, sai định dạng |
| `shift_type` | Giá trị hợp lệ | Sai loại ca |
| `start_time/end_time` | `end_time > start_time` | `end_time <= start_time` |

### 1.4 Phân hoạch cho chứng chỉ

| Biến đầu vào | Lớp hợp lệ | Lớp không hợp lệ |
| ------------ | ---------- | ---------------- |
| `certificate_name` | Có giá trị | Thiếu hoặc rỗng |
| `issued_date` | Đúng định dạng | Sai định dạng |
| `expiry_date` | Đúng định dạng, sau ngày cấp | Sai định dạng hoặc trước ngày cấp |

---

## Câu 2. Phân tích giá trị biên

| Nhóm | Giá trị | Ý nghĩa | Kết quả mong đợi |
| ---- | ------- | ------- | ---------------- |
| Dưới biên | `-1` | ID âm | 400 Bad Request |
| Tại biên dưới không hợp lệ | `0` | ID không hợp lệ | 400 Bad Request |
| Biên hợp lệ nhỏ nhất | `1` | ID hợp lệ nhỏ nhất | 200/201 nếu tồn tại |
| Giá trị lớn không tồn tại | `99999` | Đúng kiểu nhưng không có dữ liệu | 404 Not Found |
| Sai kiểu | `abc` | Không phải số nguyên | 400 Bad Request hoặc route không match |

Các testcase Staff Service trong Jira chủ yếu tập trung vào hai giá trị biên quan trọng:

* `staff_id = 0`: kiểm tra dữ liệu dưới miền hợp lệ.
* `staff_id = 1`: kiểm tra biên hợp lệ nhỏ nhất.
* `staff_id = 99999`: kiểm tra dữ liệu đúng kiểu nhưng không tồn tại.

---

## Câu 3. Thiết kế test case

### 3.1 Test case Staff Update

| STT | Mã test case | Request | Dữ liệu | Expected | Trạng thái Jira |
| --: | ------------ | ------- | ------- | -------- | --------------- |
| 1 | EP-STAFF-UPD-01 | `PUT /api/staff/1` | Body hợp lệ | 200 OK | Không thấy BUG trong ảnh hiện tại |
| 2 | BVA-STAFF-UPD-01 | `PUT /api/staff/0` | `staff_id = 0` | 400/404 | BUG |
| 3 | BVA-STAFF-UPD-02 | `PUT /api/staff/99999` | ID không tồn tại | 404 | DONE |
| 4 | EP-STAFF-UPD-02 | `PUT /api/staff/1` | `status = deleted` | 400 | DONE |
| 5 | EP-STAFF-UPD-03 | `PUT /api/staff/1` | Body rỗng | 400 | BUG |
| 6 | EP-STAFF-UPD-04 | `PUT /api/staff/1` | Không token | 401 | DONE |

### 3.2 Test case Staff Shift

| STT | Mã test case | Request | Dữ liệu | Expected | Trạng thái Jira |
| --: | ------------ | ------- | ------- | -------- | --------------- |
| 1 | EP-STAFF-SHIFT-01 | `POST /api/staff/shifts` | Body hợp lệ | 201/200 | BUG |
| 2 | BVA-STAFF-SHIFT-01 | `POST /api/staff/shifts` | `staff_id = 0` | 400 | BUG |
| 3 | BVA-STAFF-SHIFT-02 | `POST /api/staff/shifts` | `staff_id = 1` | 201/200 nếu tồn tại | BUG |
| 4 | EP-STAFF-SHIFT-02 | `POST /api/staff/shifts` | Thiếu `shift_date` | 400 | DONE |
| 5 | EP-STAFF-SHIFT-03 | `POST /api/staff/shifts` | `shift_type` sai | 400 | DONE |
| 6 | EP-STAFF-SHIFT-04 | `POST /api/staff/shifts` | `end_time` trước `start_time` | 400 | DONE |
| 7 | EP-STAFF-SHIFT-05 | `POST /api/staff/shifts` | Không token | 401 | DONE |

### 3.3 Test case Staff Schedule

| STT | Mã test case | Request | Dữ liệu | Expected | Trạng thái Jira |
| --: | ------------ | ------- | ------- | -------- | --------------- |
| 1 | EP-STAFF-SCHEDULE-01 | `GET /api/staff/1/shifts` | `staff_id` hợp lệ | 200 | BUG |
| 2 | BVA-STAFF-SCHEDULE-01 | `GET /api/staff/0/shifts` | `staff_id = 0` | 400 | BUG |
| 3 | BVA-STAFF-SCHEDULE-02 | `GET /api/staff/99999/shifts` | ID không tồn tại | 404 hoặc empty list | DONE |
| 4 | EP-STAFF-SCHEDULE-02 | `GET /api/staff/0/shifts` | Không token | 401 | DONE |

### 3.4 Test case Staff Assignment

| STT | Mã test case | Request | Dữ liệu | Expected | Trạng thái Jira |
| --: | ------------ | ------- | ------- | -------- | --------------- |
| 1 | EP-STAFF-ASSIGN-01 | `POST /api/staff/assignments` | Body hợp lệ | 201/200 | BUG |
| 2 | BVA-STAFF-ASSIGN-01 | `POST /api/staff/assignments` | `staff_id = 0` | 400 | BUG |
| 3 | BVA-STAFF-ASSIGN-02 | `POST /api/staff/assignments` | `staff_id = 1` | 201/200 nếu dữ liệu tồn tại | BUG |
| 4 | EP-STAFF-ASSIGN-02 | `POST /api/staff/assignments` | Thiếu `staff_id` | 400 | BUG |
| 5 | EP-STAFF-ASSIGN-03 | `POST /api/staff/assignments` | `booking_id/task_id` không tồn tại | 404 | DONE |
| 6 | EP-STAFF-ASSIGN-04 | `POST /api/staff/assignments` | Không token | 401 | DONE |

### 3.5 Test case Staff Certificate

| STT | Mã test case | Request | Dữ liệu | Expected | Trạng thái Jira |
| --: | ------------ | ------- | ------- | -------- | --------------- |
| 1 | EP-STAFF-CERT-01 | `POST /api/staff/1/certificates` | Body hợp lệ | 201/200 | BUG |
| 2 | BVA-STAFF-CERT-01 | `POST /api/staff/0/certificates` | `staff_id = 0` | 400 | BUG |
| 3 | BVA-STAFF-CERT-02 | `POST /api/staff/1/certificates` | `staff_id = 1` | 201/200 nếu tồn tại | BUG |
| 4 | EP-STAFF-CERT-02 | `POST /api/staff/1/certificates` | Thiếu `certificate_name` | 400 | DONE |
| 5 | EP-STAFF-CERT-03 | `POST /api/staff/1/certificates` | Ngày hết hạn sai định dạng | 400 | DONE |
| 6 | EP-STAFF-CERT-04 | `POST /api/staff/1/certificates` | Không token | 401 | DONE |

### 3.6 Test case Staff Rating

| STT | Mã test case | Request | Dữ liệu | Expected | Trạng thái Jira |
| --: | ------------ | ------- | ------- | -------- | --------------- |
| 1 | EP-STAFF-RATING-01 | `GET /api/staff/1/rating` | `staff_id` hợp lệ | 200 | BUG |
| 2 | BVA-STAFF-RATING-01 | `GET /api/staff/0/rating` | `staff_id = 0` | 400 | BUG |
| 3 | BVA-STAFF-RATING-02 | `GET /api/staff/99999/rating` | ID không tồn tại | 404 | DONE |
| 4 | EP-STAFF-RATING-02 | `GET /api/staff/1/rating` | Không token | 401 | DONE |

---

## Câu 4. Bảng mô tả lỗi tổng hợp

| Mã lỗi | Nhóm chức năng | Testcase đại diện | Expected | Actual | Nguyên nhân nghi ngờ | Mức độ |
| ------ | -------------- | ----------------- | -------- | ------ | ------------------- | ------ |
| BUG-STAFF-01 | Update | BVA-STAFF-UPD-01 | 400/404 | Fail | Chưa validate `staff_id <= 0` | Medium |
| BUG-STAFF-02 | Update | EP-STAFF-UPD-03 | 400 | Fail | Body rỗng chưa được xử lý đúng | Medium |
| BUG-STAFF-03 | Shift | EP-STAFF-SHIFT-01 | 201/200 | Fail | Dữ liệu seed/route/validate chưa khớp | High |
| BUG-STAFF-04 | Shift | BVA-STAFF-SHIFT-01 | 400 | Fail | Chưa validate `staff_id = 0` | Medium |
| BUG-STAFF-05 | Shift | BVA-STAFF-SHIFT-02 | 201/200 | Fail | Biên hợp lệ không xử lý thành công | High |
| BUG-STAFF-06 | Schedule | EP-STAFF-SCHEDULE-01 | 200 | Fail | Route lịch làm việc chưa thống nhất | High |
| BUG-STAFF-07 | Schedule | BVA-STAFF-SCHEDULE-01 | 400 | Fail | Chưa validate `staff_id = 0` | Medium |
| BUG-STAFF-08 | Assignment | EP-STAFF-ASSIGN-01 | 201/200 | Fail | Field/route/dữ liệu liên quan chưa khớp | High |
| BUG-STAFF-09 | Assignment | EP-STAFF-ASSIGN-02 | 400 | Fail | Thiếu `staff_id` chưa xử lý đúng | Medium |
| BUG-STAFF-10 | Certificate | EP-STAFF-CERT-01 | 201/200 | Fail | Route hoặc field `certificate_name` chưa khớp code | High |
| BUG-STAFF-11 | Rating | EP-STAFF-RATING-01 | 200 | Fail | Route rating chưa khớp Performance API | Medium |

---

## Câu 5. Phân tích nguyên nhân trong source code

Dựa trên cấu trúc Staff Service trong project, Staff Service được tách thành nhiều controller:

```text
services/staff-service/controllers/staff_controller.py
services/staff-service/controllers/shift_controller.py
services/staff-service/controllers/assignment_controller.py
services/staff-service/controllers/certificate_controller.py
services/staff-service/controllers/performance_controller.py
```

Các route trong source code có xu hướng chia theo từng blueprint riêng như:

```text
/api/staff/
/api/shifts/
/api/assignments/
/api/certificates/
/api/performance/
```

Trong khi các testcase BVA trong Postman lại dùng dạng gom dưới prefix `/api/staff`, ví dụ:

```http
POST /api/staff/shifts
GET  /api/staff/1/shifts
POST /api/staff/assignments
POST /api/staff/1/certificates
GET  /api/staff/1/rating
```

Vì vậy một nhóm lỗi có khả năng không phải do logic nghiệp vụ, mà do **không thống nhất URL giữa Postman collection và controller thực tế**.

Ngoài ra, các lỗi biên như `staff_id = 0` cho thấy controller/service cần bổ sung validate đầu vào rõ ràng trước khi gọi database.

---

## Câu 6. Đề xuất hướng khắc phục

## 6.1 Chuẩn hóa route API

Chọn một trong hai hướng.

### Hướng 1: Giữ route theo từng module riêng

```http
POST /api/shifts/
GET  /api/shifts/?staff_id=1
POST /api/assignments/
POST /api/certificates/
GET  /api/performance/staff/1/current
```

Khi đó phải sửa lại Postman collection cho khớp source code.

### Hướng 2: Bổ sung route alias dưới `/api/staff`

```http
POST /api/staff/shifts
GET  /api/staff/<staff_id>/shifts
POST /api/staff/assignments
POST /api/staff/<staff_id>/certificates
GET  /api/staff/<staff_id>/rating
```

Hướng này phù hợp hơn với collection hiện tại vì các test case đã được đặt theo prefix `/api/staff`.

---

## 6.2 Validate `staff_id`

Áp dụng cho shift, schedule, assignment, certificate, rating:

```python
def validate_positive_id(value, field_name="staff_id"):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return None, f"{field_name} phải là số nguyên"

    if value <= 0:
        return None, f"{field_name} phải lớn hơn 0"

    return value, None
```

---

## 6.3 Validate body rỗng

Áp dụng cho update staff, create assignment, create certificate:

```python
if not data:
    return jsonify({"error": "Body không được rỗng"}), 400
```

---

## 6.4 Chuẩn hóa response lỗi

| Trường hợp | HTTP Status |
| ---------- | ----------- |
| Thiếu token | 401 |
| Không đủ quyền | 403 |
| Thiếu field bắt buộc | 400 |
| Sai kiểu dữ liệu | 400 |
| ID <= 0 | 400 |
| ID không tồn tại | 404 |
| Lỗi server/database | 500 |

---

# Câu 7. Thiết kế kiểm thử tự động

## 7.1 Unit test validate `staff_id`

```python
import unittest


def validate_positive_id(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return False
    return value > 0


class TestStaffIdValidation(unittest.TestCase):

    def test_staff_id_valid_1(self):
        self.assertTrue(validate_positive_id(1))

    def test_staff_id_zero(self):
        self.assertFalse(validate_positive_id(0))

    def test_staff_id_negative(self):
        self.assertFalse(validate_positive_id(-1))

    def test_staff_id_string(self):
        self.assertFalse(validate_positive_id("abc"))


if __name__ == "__main__":
    unittest.main()
```

## 7.2 API test bằng pytest

```python
def test_update_staff_with_empty_body_should_return_400(client, admin_token):
    response = client.put(
        "/api/staff/1",
        json={},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 400


def test_create_shift_with_staff_id_zero_should_return_400(client, admin_token):
    response = client.post(
        "/api/staff/shifts",
        json={
            "staff_id": 0,
            "shift_date": "2026-06-01",
            "shift_type": "morning",
            "start_time": "08:00:00",
            "end_time": "12:00:00"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 400


def test_create_assignment_missing_staff_id_should_return_400(client, admin_token):
    response = client.post(
        "/api/staff/assignments",
        json={
            "booking_id": 1,
            "task_id": 1,
            "note": "Giao việc sửa chữa cho kỹ thuật viên"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 400
```

---

# Câu 8. Kịch bản kiểm thử Postman

## 8.1 Chuẩn bị

1. Chạy toàn bộ Docker services.
2. Đăng nhập tài khoản admin để lấy token.
3. Trong Postman chọn Authorization → Bearer Token.
4. Gán biến môi trường:

```text
base_url = http://localhost
authorization_secret = <admin_token>
```

## 8.2 Chạy folder Staff Service

Trong Postman chạy folder:

```text
[Black-box] - BVA & Equivalence / [staff-service] - BVA & Equivalence
```

## 8.3 Các testcase cần chú ý

| Nhóm | Testcase cần kiểm tra lại |
| ---- | ------------------------- |
| Update | `BVA-STAFF-UPD-01`, `EP-STAFF-UPD-03` |
| Shift | `EP-STAFF-SHIFT-01`, `BVA-STAFF-SHIFT-01`, `BVA-STAFF-SHIFT-02` |
| Schedule | `EP-STAFF-SCHEDULE-01`, `BVA-STAFF-SCHEDULE-01` |
| Assignment | `EP-STAFF-ASSIGN-01`, `BVA-STAFF-ASSIGN-01`, `BVA-STAFF-ASSIGN-02`, `EP-STAFF-ASSIGN-02` |
| Certificate | `EP-STAFF-CERT-01`, `BVA-STAFF-CERT-01`, `BVA-STAFF-CERT-02` |
| Rating | `EP-STAFF-RATING-01`, `BVA-STAFF-RATING-01` |

---

# PHẦN B. KẾT QUẢ KIỂM THỬ

## 1. Tổng hợp kết quả

Dựa trên danh sách testcase Staff Service hiển thị trên Jira:

| Tổng số testcase quan sát | DONE | BUG |
| ------------------------- | ---- | --- |
| 32 | 16 | 16 |

## 2. Danh sách testcase fail

| Testcase | Nhóm | Dữ liệu chính | Expected |
| -------- | ---- | ------------- | -------- |
| BVA-STAFF-UPD-01 | Update | `staff_id = 0` | 400/404 |
| EP-STAFF-UPD-03 | Update | Body rỗng | 400 |
| EP-STAFF-SHIFT-01 | Shift | Body hợp lệ | 201/200 |
| BVA-STAFF-SHIFT-01 | Shift | `staff_id = 0` | 400 |
| BVA-STAFF-SHIFT-02 | Shift | `staff_id = 1` | 201/200 nếu tồn tại |
| EP-STAFF-SCHEDULE-01 | Schedule | `staff_id` hợp lệ | 200 |
| BVA-STAFF-SCHEDULE-01 | Schedule | `staff_id = 0` | 400 |
| EP-STAFF-ASSIGN-01 | Assignment | Body hợp lệ | 201/200 |
| BVA-STAFF-ASSIGN-01 | Assignment | `staff_id = 0` | 400 |
| BVA-STAFF-ASSIGN-02 | Assignment | `staff_id = 1` | 201/200 nếu tồn tại |
| EP-STAFF-ASSIGN-02 | Assignment | Thiếu `staff_id` | 400 |
| EP-STAFF-CERT-01 | Certificate | Body hợp lệ | 201/200 |
| BVA-STAFF-CERT-01 | Certificate | `staff_id = 0` | 400 |
| BVA-STAFF-CERT-02 | Certificate | `staff_id = 1` | 201/200 nếu tồn tại |
| EP-STAFF-RATING-01 | Rating | `staff_id` hợp lệ | 200 |
| BVA-STAFF-RATING-01 | Rating | `staff_id = 0` | 400 |

## 3. Đánh giá

Các lỗi không chỉ là lỗi validate dữ liệu biên mà còn có dấu hiệu không thống nhất giữa endpoint Postman và route backend. Những testcase hợp lệ nhưng fail như `EP-STAFF-SHIFT-01`, `EP-STAFF-ASSIGN-01`, `EP-STAFF-CERT-01`, `EP-STAFF-RATING-01` cần được ưu tiên kiểm tra vì chúng ảnh hưởng trực tiếp đến luồng nghiệp vụ chính.

---

# PHẦN C. KẾT LUẬN

Qua kiểm thử Staff Service, em đã áp dụng các kỹ thuật:

* Phân hoạch lớp tương đương.
* Phân tích giá trị biên.
* Thiết kế test case API.
* Kiểm thử bằng Postman.
* Theo dõi kết quả trên Jira.
* Phân tích nguyên nhân dựa vào source code và route API.

Kết quả kiểm thử cho thấy Staff Service còn các nhóm lỗi chính:

1. Chưa validate đầy đủ `staff_id = 0` ở nhiều endpoint.
2. Một số request body hợp lệ vẫn fail, có thể do dữ liệu seed hoặc route chưa khớp.
3. Một số testcase có dấu hiệu URL trong Postman chưa thống nhất với route thực tế của service.
4. Body rỗng và thiếu field bắt buộc cần được trả lỗi `400 Bad Request` rõ ràng.

Hướng xử lý đề xuất:

* Chuẩn hóa endpoint Staff Service theo một convention thống nhất.
* Bổ sung validate `staff_id`, `center_id`, body rỗng và field bắt buộc.
* Seed dữ liệu test ổn định cho các testcase hợp lệ.
* Chạy lại Postman collection và cập nhật trạng thái Jira từ BUG sang DONE sau khi fix.
