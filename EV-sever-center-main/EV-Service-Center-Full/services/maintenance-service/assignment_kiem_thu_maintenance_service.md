# Assignment: Kiểm thử chức năng Maintenance Service

**Thời lượng:** 90 phút  
**Chủ đề:** Phân hoạch lớp tương đương, phân tích giá trị biên, thiết kế test case và kiểm thử API  
**Mức độ:** Cơ bản đến trung bình  
**Hình thức:** Cá nhân  
**Tổng điểm:** 10 điểm  

**Họ và tên:** Trần Anh Kiệt  
**MSSV:** 052205013377
**Lớp:** CN2301E
---

# 1. Mục tiêu bài tập

1. Xác định điều kiện kiểm thử cho chức năng quản lý công việc bảo trì trong Maintenance Service.
2. Áp dụng kỹ thuật phân hoạch lớp tương đương để chia dữ liệu đầu vào hợp lệ và không hợp lệ.
3. Áp dụng kỹ thuật phân tích giá trị biên cho tham số `task_id` hoặc `id` khi truy vấn công việc bảo trì.
4. Thiết kế test case cho API lấy danh sách, lấy chi tiết và kiểm tra lỗi khi truyền sai tham số.
5. Ghi nhận lỗi thực tế khi kiểm thử bằng Postman.
6. Đề xuất hướng xử lý lỗi và viết kiểm thử tự động để xác nhận hệ thống hoạt động đúng.

---

# 2. Nội dung tham khảo

Trong bài này em áp dụng các kỹ thuật kiểm thử sau:

* **Equivalence Partitioning:** chia dữ liệu đầu vào thành nhóm hợp lệ và không hợp lệ.
* **Boundary Value Analysis (BVA):** chọn dữ liệu tại vùng biên, ví dụ `task_id = 0`, `task_id = 1`, `task_id` không tồn tại.
* **API Testing:** kiểm thử endpoint bằng Postman với token xác thực.
* **Negative Testing:** kiểm thử các trường hợp dữ liệu sai như `id=abc`, `id=9999`.
* **Unit Test / Integration Test:** dùng code để kiểm tra logic validate dữ liệu và phản hồi API.

---

# 3. Mô tả bài toán

Hệ thống EV Service Center có **Maintenance Service** dùng để quản lý các công việc bảo trì xe điện.

Maintenance Service hỗ trợ các chức năng chính:

| Chức năng | Endpoint | Method | Mô tả |
| -------- | -------- | ------ | ----- |
| Tạo công việc bảo trì | `/api/maintenance/tasks` | POST | Admin tạo task từ booking và technician |
| Lấy danh sách task | `/api/maintenance/tasks` | GET | Admin lấy toàn bộ công việc bảo trì |
| Lấy task của người dùng hiện tại | `/api/maintenance/my-tasks` | GET | Customer hoặc technician xem task của mình |
| Lấy chi tiết task | `/api/maintenance/tasks/<task_id>` | GET | Admin, customer owner hoặc technician owner xem chi tiết task |
| Cập nhật trạng thái task | `/api/maintenance/tasks/<task_id>/status` | PUT | Cập nhật trạng thái công việc |
| Thêm phụ tùng vào task | `/api/maintenance/tasks/<task_id>/parts` | POST | Admin hoặc technician owner thêm phụ tùng |
| Lấy checklist của task | `/api/maintenance/tasks/<task_id>/checklist` | GET | Lấy danh sách hạng mục kiểm tra |

Trong bài assignment này, phạm vi kiểm thử tập trung vào chức năng:

```text
GET /api/maintenance/tasks
GET /api/maintenance/tasks/<task_id>
```

và hai lỗi thực tế khi truyền query parameter `id` vào endpoint lấy danh sách:

```text
GET /api/maintenance/tasks?id=abc
GET /api/maintenance/tasks?id=9999
```

---

# 4. Yêu cầu nghiệp vụ mong đợi

## 4.1 Quy tắc lấy danh sách task

Endpoint:

```http
GET /api/maintenance/tasks
```

Điều kiện hợp lệ:

* Người dùng phải đăng nhập.
* Token phải hợp lệ.
* Người dùng phải có role `admin`.
* Request không truyền tham số `id` nếu mục đích là lấy toàn bộ danh sách.

Kết quả mong đợi:

```text
HTTP 200 OK
Trả về mảng danh sách maintenance task
```

## 4.2 Quy tắc lấy chi tiết task theo ID

Endpoint đúng:

```http
GET /api/maintenance/tasks/<task_id>
```

Ví dụ:

```http
GET /api/maintenance/tasks/10
```

Điều kiện hợp lệ:

| Biến đầu vào | Ý nghĩa | Kiểu dữ liệu | Miền giá trị hợp lệ |
| ------------ | ------- | ------------ | ------------------- |
| `task_id` | Mã công việc bảo trì | Số nguyên dương | `task_id >= 1` và tồn tại trong database |
| `Authorization` | Bearer Token | Chuỗi token | Token hợp lệ, chưa hết hạn |
| `role` | Quyền người dùng | Chuỗi | `admin`, hoặc đúng customer/technician owner |

Kết quả mong đợi:

```text
HTTP 200 OK nếu task tồn tại và người dùng có quyền
HTTP 400 Bad Request nếu task_id sai kiểu dữ liệu
HTTP 404 Not Found nếu task_id đúng kiểu nhưng không tồn tại
HTTP 401 Unauthorized nếu thiếu token hoặc token sai
HTTP 403 Forbidden nếu không có quyền xem task
```

---

# 5. Mô tả lỗi phát hiện

## 5.1 Lỗi 1: Truyền `id=abc` nhưng API vẫn trả `200 OK`

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-MAINT-01 |
| Chức năng | Lấy công việc bảo trì theo ID |
| Method | GET |
| Endpoint được test | `/api/maintenance/tasks?id=abc` |
| Token | Bearer Token hợp lệ |
| Dữ liệu đầu vào | `id=abc` |
| Kết quả thực tế | API trả `200 OK` và danh sách task |
| Kết quả mong đợi | API phải báo lỗi `400 Bad Request` vì `abc` không phải số nguyên |
| Mức độ nghiêm trọng | Medium |
| Trạng thái | Failed |

### Request trên Postman

```http
GET http://localhost/api/maintenance/tasks?id=abc
Authorization: Bearer <token>
```

### Kết quả thực tế

API trả về:

```http
HTTP/1.1 200 OK
```

Body trả về là danh sách task, ví dụ:

```json
[
  {
    "booking_id": 5,
    "created_at": "2026-07-05T12:57:41.315772",
    "description": "battery_replacement",
    "status": "pending",
    "task_id": 10,
    "technician_id": 1,
    "updated_at": "2026-07-05T12:57:41.315772",
    "user_id": 7,
    "vehicle_vin": "VIN_5_admin1"
  }
]
```

### Kết quả mong đợi

Vì `id=abc` là dữ liệu sai kiểu, hệ thống phải trả:

```http
HTTP/1.1 400 Bad Request
```

Ví dụ body:

```json
{
  "error": "id phải là số nguyên dương"
}
```

### Nguyên nhân phân tích

Trong controller hiện tại có route:

```python
@maintenance_bp.route("/tasks", methods=["GET"])
@jwt_required()
@admin_required()
def get_all_tasks_route():
    tasks = service.get_all_tasks()
    return jsonify([t.to_dict() for t in tasks]), 200
```

Route này chỉ lấy toàn bộ task và không đọc query parameter `id`.

Do đó khi gọi:

```http
GET /api/maintenance/tasks?id=abc
```

Flask vẫn match vào route `/tasks`, bỏ qua query parameter `id`, sau đó gọi `service.get_all_tasks()` và trả về toàn bộ danh sách task.

### Ảnh hưởng

* API không validate dữ liệu đầu vào.
* Người test hoặc frontend có thể hiểu nhầm rằng hệ thống đã lọc theo ID.
* Dữ liệu trả về sai mục đích của request.
* Có nguy cơ làm sai luồng xử lý nếu frontend phụ thuộc vào query `id`.

---

## 5.2 Lỗi 2: Truyền `id=9999` không tồn tại nhưng API vẫn trả `200 OK`

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-MAINT-02 |
| Chức năng | Lấy công việc bảo trì theo ID |
| Method | GET |
| Endpoint được test | `/api/maintenance/tasks?id=9999` |
| Token | Bearer Token hợp lệ |
| Dữ liệu đầu vào | `id=9999` |
| Kết quả thực tế | API trả `200 OK` và danh sách task |
| Kết quả mong đợi | API phải trả `404 Not Found` vì task không tồn tại |
| Mức độ nghiêm trọng | Medium |
| Trạng thái | Failed |

### Request trên Postman

```http
GET http://localhost/api/maintenance/tasks?id=9999
Authorization: Bearer <token>
```

### Kết quả thực tế

API trả về:

```http
HTTP/1.1 200 OK
```

Body vẫn là danh sách task, không phải thông tin của task `9999`.

### Kết quả mong đợi

Vì `9999` là số nguyên hợp lệ về mặt kiểu dữ liệu nhưng không tồn tại trong database, hệ thống phải trả:

```http
HTTP/1.1 404 Not Found
```

Ví dụ body:

```json
{
  "error": "Không tìm thấy Công việc."
}
```

### Nguyên nhân phân tích

Nguyên nhân giống lỗi thứ nhất: endpoint `/api/maintenance/tasks` không xử lý query parameter `id`.

Khi truyền:

```http
GET /api/maintenance/tasks?id=9999
```

controller vẫn xem đây là request lấy toàn bộ danh sách task, không kiểm tra task `9999` có tồn tại hay không.

### Ảnh hưởng

* Hệ thống trả sai status code.
* Người dùng không nhận được thông báo task không tồn tại.
* Test case kiểm tra dữ liệu không tồn tại bị thất bại.
* API thiếu tính nhất quán vì endpoint `/tasks/<task_id>` có xử lý `404`, còn `/tasks?id=...` thì không.

---

# PHẦN A. BÀI LÀM

---

## Câu 1. Xác định lớp tương đương

### 1.1 Phân hoạch cho tham số `id` hoặc `task_id`

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| `task_id` / `id` | Số nguyên dương và tồn tại trong database | V1 | Không truyền ID khi muốn xem chi tiết | X1 |
| | | | Chuỗi chữ, ví dụ `abc` | X2 |
| | | | Số nguyên nhưng không tồn tại, ví dụ `9999` | X3 |
| | | | Số nhỏ hơn hoặc bằng 0, ví dụ `0`, `-1` | X4 |
| | | | Số thập phân, ví dụ `1.5` | X5 |
| | | | Ký tự đặc biệt, ví dụ `@#$` | X6 |
| | | | Chuỗi rỗng, ví dụ `id=` | X7 |

### 1.2 Phân hoạch cho token

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| Bearer Token | Token hợp lệ, chưa hết hạn | V2 | Không có token | X8 |
| | | | Token sai định dạng | X9 |
| | | | Token hết hạn | X10 |

### 1.3 Phân hoạch cho quyền người dùng

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| Role | `admin` khi xem toàn bộ danh sách | V3 | `customer` gọi API admin list | X11 |
| Owner | Customer owner hoặc technician owner khi xem chi tiết task | V4 | Người dùng không sở hữu task | X12 |

### Nhận xét

Các lớp dữ liệu quan trọng nhất trong bài này là:

* `id=abc`: thuộc lớp không hợp lệ X2 vì sai kiểu dữ liệu.
* `id=9999`: thuộc lớp không hợp lệ X3 vì đúng kiểu nhưng không tồn tại.

Hai trường hợp này đều phải trả lỗi, nhưng hệ thống thực tế lại trả `200 OK`.

---

## Câu 2. Phân tích giá trị biên

Với `task_id`, miền hợp lệ là số nguyên dương và tồn tại trong database.

Giả sử database hiện có một task với:

```text
task_id = 10
```

Ta chọn các giá trị kiểm thử như sau:

| Nhóm | Giá trị | Ý nghĩa | Kết quả mong đợi |
| ---- | ------- | ------- | ---------------- |
| Dưới biên | `-1` | ID âm | 400 Bad Request |
| Tại biên dưới không hợp lệ | `0` | ID không hợp lệ vì task_id phải >= 1 | 400 Bad Request hoặc 404 Not Found tùy thiết kế route |
| Biên hợp lệ nhỏ nhất | `1` | ID nguyên dương | 200 nếu tồn tại, 404 nếu không tồn tại |
| Giá trị tồn tại | `10` | Task đang có trong database | 200 OK |
| Giá trị không tồn tại | `9999` | ID hợp lệ về kiểu nhưng không có dữ liệu | 404 Not Found |
| Sai kiểu | `abc` | Không phải số nguyên | 400 Bad Request |
| Số thập phân | `1.5` | Không phải số nguyên | 400 Bad Request |
| Chuỗi rỗng | `id=` | Thiếu giá trị ID | 400 Bad Request |

### Nhận xét

Các giá trị biên giúp phát hiện lỗi validate đầu vào. Trong hai ảnh Postman, hai giá trị kiểm thử đại diện cho:

* `abc`: kiểm thử sai kiểu dữ liệu.
* `9999`: kiểm thử ID không tồn tại.

Cả hai đều không được hệ thống xử lý đúng.

---

## Câu 3. Thiết kế test case

### 3.1 Test case cho chức năng lấy danh sách task

| STT | Mã test case | Mô tả | Request | Dữ liệu đầu vào | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| --: | ------------ | ----- | ------- | --------------- | ---------------- | ---------------- | ---------- |
| 1 | TC-MAINT-LIST-01 | Admin lấy danh sách task | `GET /api/maintenance/tasks` | Token admin hợp lệ | 200 OK, trả danh sách task | 200 OK | Pass |
| 2 | TC-MAINT-LIST-02 | Không có token | `GET /api/maintenance/tasks` | Không truyền token | 401 Unauthorized | Chưa ghi nhận | Not run |
| 3 | TC-MAINT-LIST-03 | Token role customer gọi API admin | `GET /api/maintenance/tasks` | Token customer | 403 Forbidden | Chưa ghi nhận | Not run |
| 4 | TC-MAINT-LIST-04 | Token không hợp lệ | `GET /api/maintenance/tasks` | Token sai | 401 Unauthorized | Chưa ghi nhận | Not run |

### 3.2 Test case cho chức năng lấy chi tiết task

| STT | Mã test case | Mô tả | Request | Dữ liệu đầu vào | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| --: | ------------ | ----- | ------- | --------------- | ---------------- | ---------------- | ---------- |
| 1 | TC-MAINT-DETAIL-01 | Lấy chi tiết task tồn tại | `GET /api/maintenance/tasks/10` | `task_id=10` | 200 OK, trả chi tiết task | Chưa ghi nhận | Not run |
| 2 | TC-MAINT-DETAIL-02 | Task không tồn tại | `GET /api/maintenance/tasks/9999` | `task_id=9999` | 404 Not Found | Chưa ghi nhận | Not run |
| 3 | TC-MAINT-DETAIL-03 | Task ID sai kiểu | `GET /api/maintenance/tasks/abc` | `task_id=abc` | 404 theo Flask route hiện tại hoặc 400 nếu có custom validate | Chưa ghi nhận | Not run |
| 4 | TC-MAINT-DETAIL-04 | Không có quyền xem task | `GET /api/maintenance/tasks/10` | Token user không sở hữu task | 403 Forbidden | Chưa ghi nhận | Not run |

### 3.3 Test case phát hiện lỗi thực tế từ ảnh

| STT | Mã test case | Mô tả | Request | Dữ liệu đầu vào | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| --: | ------------ | ----- | ------- | --------------- | ---------------- | ---------------- | ---------- |
| 1 | TC-BUG-MAINT-01 | Kiểm tra query `id` sai kiểu | `GET /api/maintenance/tasks?id=abc` | `id=abc` | 400 Bad Request | 200 OK, trả danh sách task | Fail |
| 2 | TC-BUG-MAINT-02 | Kiểm tra query `id` không tồn tại | `GET /api/maintenance/tasks?id=9999` | `id=9999` | 404 Not Found | 200 OK, trả danh sách task | Fail |

### Nhận xét

Hai test case lỗi đều cho thấy hệ thống đang bỏ qua query parameter `id`.

Về mặt nghiệp vụ, nếu API cho phép truyền `id` bằng query string thì phải validate và lọc theo ID. Nếu API không hỗ trợ query `id`, hệ thống nên trả lỗi rõ ràng hoặc frontend/tester phải dùng đúng endpoint `/tasks/<task_id>`.

---

## Câu 4. Bảng mô tả lỗi

| Mã lỗi | Tên lỗi | Dữ liệu test | Expected | Actual | Nguyên nhân | Mức độ |
| ------ | ------- | ------------ | -------- | ------ | ----------- | ------ |
| BUG-MAINT-01 | Không validate query `id` sai kiểu | `id=abc` | 400 Bad Request | 200 OK + danh sách task | Controller `/tasks` không đọc `request.args.get("id")` | Medium |
| BUG-MAINT-02 | Không xử lý query `id` không tồn tại | `id=9999` | 404 Not Found | 200 OK + danh sách task | Controller `/tasks` bỏ qua query parameter và gọi `get_all_tasks()` | Medium |

---

## Câu 5. Phân tích nguyên nhân trong source code

File liên quan:

```text
EV-Service-Center-Full/services/maintenance-service/controllers/maintenance_controller.py
```

Đoạn code hiện tại:

```python
@maintenance_bp.route("/tasks", methods=["GET"])
@jwt_required()
@admin_required()
def get_all_tasks_route():
    tasks = service.get_all_tasks()
    return jsonify([t.to_dict() for t in tasks]), 200
```

Vấn đề:

* Hàm chỉ xử lý lấy toàn bộ danh sách.
* Không kiểm tra `request.args`.
* Không validate `id`.
* Không phân biệt request lấy danh sách và request lấy theo ID dạng query.

Trong khi đó, route lấy chi tiết task đã được định nghĩa riêng:

```python
@maintenance_bp.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task_details_route(task_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    task, is_authorized, _, _ = _check_task_permission(task_id, current_user_id, claims)
    
    if not task:
        return jsonify({"error": "Không tìm thấy Công việc."}), 404

    if not is_authorized:
        return jsonify(error="Unauthorized access to task"), 403

    return jsonify(task.to_dict()), 200
```

Endpoint đúng để lấy chi tiết task phải là:

```http
GET /api/maintenance/tasks/10
```

không phải:

```http
GET /api/maintenance/tasks?id=10
```

---

## Câu 6. Đề xuất hướng khắc phục

Có hai hướng sửa. Trong thực tế chỉ nên chọn một hướng để API nhất quán.

## Hướng 1: Không hỗ trợ query `id`, yêu cầu dùng path parameter

Nếu hệ thống chỉ thiết kế endpoint lấy chi tiết bằng `/tasks/<task_id>`, thì khi request `/tasks?id=...`, API nên trả lỗi rõ ràng.

Ví dụ:

```python
@maintenance_bp.route("/tasks", methods=["GET"])
@jwt_required()
@admin_required()
def get_all_tasks_route():
    if "id" in request.args:
        return jsonify({
            "error": "Không hỗ trợ query parameter id. Vui lòng dùng /api/maintenance/tasks/<task_id>."
        }), 400

    tasks = service.get_all_tasks()
    return jsonify([t.to_dict() for t in tasks]), 200
```

Ưu điểm:

* API rõ ràng.
* Không trộn chức năng list và detail trong một route.
* Ít thay đổi code.

Nhược điểm:

* Frontend hoặc tester phải sửa lại URL đang gọi.

## Hướng 2: Hỗ trợ query `id` trong endpoint `/tasks`

Nếu muốn `/tasks?id=10` cũng lấy được chi tiết task, có thể validate query `id`.

Ví dụ:

```python
@maintenance_bp.route("/tasks", methods=["GET"])
@jwt_required()
@admin_required()
def get_all_tasks_route():
    task_id = request.args.get("id")

    if task_id is not None:
        try:
            task_id = int(task_id)
        except ValueError:
            return jsonify({"error": "id phải là số nguyên dương"}), 400

        if task_id <= 0:
            return jsonify({"error": "id phải là số nguyên dương"}), 400

        task = service.get_task_by_id(task_id)
        if not task:
            return jsonify({"error": "Không tìm thấy Công việc."}), 404

        return jsonify(task.to_dict()), 200

    tasks = service.get_all_tasks()
    return jsonify([t.to_dict() for t in tasks]), 200
```

Ưu điểm:

* Giữ được URL tester đang sử dụng.
* Có thể vừa lấy danh sách vừa lọc chi tiết theo query.

Nhược điểm:

* API có hai cách lấy chi tiết task: `/tasks/<id>` và `/tasks?id=<id>`.
* Có thể gây không nhất quán nếu tài liệu API không ghi rõ.

### Hướng đề xuất

Em đề xuất chọn **Hướng 1** vì source code hiện tại đã có sẵn route lấy chi tiết:

```http
GET /api/maintenance/tasks/<task_id>
```

Do đó endpoint `/api/maintenance/tasks` chỉ nên dùng cho chức năng lấy danh sách. Nếu có query `id`, hệ thống nên báo lỗi `400 Bad Request` và hướng dẫn dùng đúng endpoint.

---

## Câu 7. Thiết kế kiểm thử tự động

### 7.1 Hàm validate ID

Có thể tách logic validate ID thành hàm riêng để dễ kiểm thử.

```python
def validate_positive_integer_id(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return False

    return value > 0
```

### 7.2 Unit test cho hàm validate ID

```python
import unittest


def validate_positive_integer_id(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return False

    return value > 0


class TestValidateTaskId(unittest.TestCase):

    def test_valid_id(self):
        self.assertTrue(validate_positive_integer_id("10"))

    def test_invalid_string_id(self):
        self.assertFalse(validate_positive_integer_id("abc"))

    def test_invalid_zero_id(self):
        self.assertFalse(validate_positive_integer_id("0"))

    def test_invalid_negative_id(self):
        self.assertFalse(validate_positive_integer_id("-1"))

    def test_invalid_empty_id(self):
        self.assertFalse(validate_positive_integer_id(""))


if __name__ == "__main__":
    unittest.main()
```

### 7.3 API test bằng pytest cho hai lỗi

Ví dụ test kỳ vọng nếu chọn hướng không hỗ trợ query `id`:

```python
def test_get_tasks_with_invalid_query_id_should_return_400(client, admin_token):
    response = client.get(
        "/api/maintenance/tasks?id=abc",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 400
    assert "id" in response.get_json()["error"]


def test_get_tasks_with_query_id_should_return_400(client, admin_token):
    response = client.get(
        "/api/maintenance/tasks?id=9999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 400
    assert "Không hỗ trợ query parameter id" in response.get_json()["error"]
```

Ví dụ test kỳ vọng nếu chọn hướng hỗ trợ query `id`:

```python
def test_get_tasks_with_invalid_query_id_should_return_400(client, admin_token):
    response = client.get(
        "/api/maintenance/tasks?id=abc",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "id phải là số nguyên dương"


def test_get_tasks_with_not_found_query_id_should_return_404(client, admin_token):
    response = client.get(
        "/api/maintenance/tasks?id=9999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Không tìm thấy Công việc."
```

---

## Câu 8. Kịch bản kiểm thử Postman

### 8.1 Chuẩn bị

1. Chạy hệ thống backend.
2. Đăng nhập bằng tài khoản admin.
3. Copy access token.
4. Trong Postman chọn tab **Authorization**.
5. Chọn **Bearer Token**.
6. Dán token vào ô Token.

### 8.2 Test case 1: Admin lấy danh sách task

Request:

```http
GET http://localhost/api/maintenance/tasks
```

Expected:

```text
Status: 200 OK
Body: Mảng danh sách task
```

### 8.3 Test case 2: Query `id=abc`

Request:

```http
GET http://localhost/api/maintenance/tasks?id=abc
```

Expected:

```text
Status: 400 Bad Request
Body có message báo id không hợp lệ
```

Actual theo ảnh:

```text
Status: 200 OK
Body trả về danh sách task
```

Đánh giá:

```text
Fail
```

### 8.4 Test case 3: Query `id=9999`

Request:

```http
GET http://localhost/api/maintenance/tasks?id=9999
```

Expected nếu API hỗ trợ query ID:

```text
Status: 404 Not Found
Body báo không tìm thấy Công việc
```

Expected nếu API không hỗ trợ query ID:

```text
Status: 400 Bad Request
Body báo không hỗ trợ query parameter id
```

Actual theo ảnh:

```text
Status: 200 OK
Body trả về danh sách task
```

Đánh giá:

```text
Fail
```

---

# PHẦN B. KẾT QUẢ KIỂM THỬ

## 1. Tổng hợp kết quả

| Tổng số test case | Pass | Fail | Not run |
| ----------------- | ---- | ---- | ------- |
| 9 | 1 | 2 | 6 |

## 2. Danh sách test case fail

| Mã test case | Lỗi | Expected | Actual |
| ------------ | --- | -------- | ------ |
| TC-BUG-MAINT-01 | `id=abc` sai kiểu nhưng vẫn trả danh sách | 400 Bad Request | 200 OK |
| TC-BUG-MAINT-02 | `id=9999` không tồn tại nhưng vẫn trả danh sách | 404 Not Found hoặc 400 nếu không hỗ trợ query ID | 200 OK |

## 3. Đánh giá

Hai lỗi trên thuộc nhóm lỗi validate đầu vào và thiết kế endpoint. Hệ thống không bị crash nhưng phản hồi sai về mặt nghiệp vụ, làm cho client hoặc người dùng hiểu nhầm dữ liệu trả về.

---

# PHẦN C. BỔ SUNG KIỂM THỬ TOÀN BỘ THƯ MỤC MAINTENANCE SERVICE

Phần trên tập trung vào lỗi query parameter `id` của endpoint lấy danh sách task. Phần bổ sung này mở rộng phạm vi kiểm thử cho toàn bộ thư mục:

```text
EV-Service-Center-Full/services/maintenance-service
```

Mục tiêu là mô tả đầy đủ kiến trúc, API, model, service, test case, rủi ro hiện có và hướng hoàn thiện kiểm thử tự động.

---

## C1. Cấu trúc thư mục và vai trò từng file

| Thành phần | File/thư mục | Vai trò |
| ---------- | ------------ | ------- |
| Flask app chính | `app.py` | Khởi tạo Flask app, cấu hình database, JWT, CORS, migration, register blueprint và health check |
| Public API controller | `controllers/maintenance_controller.py` | Định nghĩa các route `/api/maintenance/...` cho admin, customer, technician |
| Internal API controller | `controllers/internal_controller.py` | Định nghĩa các route `/internal/maintenance/...` cho service nội bộ như notification service |
| Business service | `services/maintenance_service.py` | Xử lý nghiệp vụ tạo task, cập nhật trạng thái, parts, checklist và gọi service khác |
| Data model | `models/maintenance_model.py` | Định nghĩa bảng `maintenance_tasks`, `task_parts`, `maintenance_checklists` |
| Test fixture | `test/conftest.py` | Tạo Flask test app, SQLite memory database và fixture dùng cho pytest |
| Unit test | `test/test_maintenance_service.py` | Kiểm thử service layer bằng pytest và mock |
| Báo cáo phụ | `MAINTENANCE_SERVICE_REPORT.md` | Báo cáo kiểm thử tổng quan, nhưng có một số endpoint cũ chưa khớp source hiện tại |
| Assignment chính | `assignment_kiem_thu_maintenance_service.md` | Tài liệu bài làm kiểm thử và phân tích lỗi |
| Docker | `Dockerfile` | Cấu hình container cho service |
| Dependencies | `requirements.txt` | Danh sách thư viện Python cần cài |

---

## C2. Kiến trúc xử lý của Maintenance Service

Luồng chính của service:

```text
Client/Postman/Frontend
        |
        v
controllers/maintenance_controller.py
        |
        v
services/maintenance_service.py
        |
        v
models/maintenance_model.py
        |
        v
Database
```

Luồng tạo maintenance task có gọi service khác:

```text
Admin tạo task
        |
        v
POST /api/maintenance/tasks
        |
        v
MaintenanceService.create_task_from_booking()
        |
        +--> Booking Service: lấy thông tin booking
        |
        +--> User Service: lấy thông tin user để tạo VIN
        |
        v
Tạo MaintenanceTask + checklist mặc định
```

Luồng thêm phụ tùng có gọi inventory:

```text
Admin/Technician thêm phụ tùng
        |
        v
POST /api/maintenance/tasks/<task_id>/parts
        |
        v
MaintenanceService.add_part_to_task()
        |
        +--> Inventory Service: kiểm tra tồn kho
        |
        v
Tạo hoặc tăng số lượng TaskPart
```

---

## C3. Cấu hình môi trường cần kiểm tra

Các biến môi trường được đọc trong `app.py`:

| Biến môi trường | Mục đích | Rủi ro nếu thiếu/sai |
| --------------- | -------- | -------------------- |
| `DATABASE_URL` | Kết nối database | App không tạo/kết nối được bảng |
| `JWT_SECRET_KEY` | Xác thực JWT | Token không verify được, API trả 401 |
| `INTERNAL_SERVICE_TOKEN` | Xác thực service nội bộ | Internal API hoặc gọi service khác bị 401 |
| `BOOKING_SERVICE_URL` | Gọi Booking Service | Không tạo được task từ booking |
| `USER_SERVICE_URL` | Gọi User Service | VIN fallback về `Unknown` hoặc tạo task thiếu dữ liệu |
| `INVENTORY_SERVICE_URL` | Gọi Inventory Service | Không thêm được phụ tùng vào task |

Test case cấu hình cần có:

| Mã test | Điều kiện | Expected |
| ------- | --------- | -------- |
| TC-CONFIG-01 | Đủ `DATABASE_URL`, `JWT_SECRET_KEY` | App start thành công |
| TC-CONFIG-02 | Thiếu `INTERNAL_SERVICE_TOKEN` | Gọi internal API trả 401 hoặc service báo lỗi cấu hình |
| TC-CONFIG-03 | Thiếu `BOOKING_SERVICE_URL` | Tạo task trả lỗi lấy booking |
| TC-CONFIG-04 | Thiếu `INVENTORY_SERVICE_URL` | Thêm phụ tùng trả lỗi cấu hình inventory |

---

## C4. Data model cần kiểm thử

### C4.1 Bảng `maintenance_tasks`

| Field | Kiểu | Bắt buộc | Ghi chú kiểm thử |
| ----- | ---- | -------- | ---------------- |
| `task_id` | Integer | Có | Primary key, dùng cho path `/tasks/<task_id>` |
| `booking_id` | Integer | Có | Dùng để liên kết booking, có thể có nhiều task theo technician |
| `user_id` | Integer | Có | Customer owner của task |
| `vehicle_vin` | String(100) | Có | Tạo từ booking/user profile |
| `description` | String(255) | Có | Lấy từ `service_type` của booking |
| `technician_id` | Integer | Có | Technician được phân công |
| `status` | Enum | Có | Hợp lệ: `pending`, `in_progress`, `completed`, `failed` |
| `created_at` | DateTime | Có | Tự sinh |
| `updated_at` | DateTime | Có | Tự cập nhật |

### C4.2 Bảng `task_parts`

| Field | Kiểu | Bắt buộc | Ghi chú kiểm thử |
| ----- | ---- | -------- | ---------------- |
| `id` | Integer | Có | Primary key của phụ tùng đã dùng |
| `task_id` | Integer | Có | Task liên quan |
| `item_id` | Integer | Có | ID phụ tùng từ Inventory Service |
| `quantity` | Integer | Có | Cần kiểm thử `0`, âm, vượt tồn kho, số lớn |
| `created_at` | DateTime | Có | Tự sinh |

### C4.3 Bảng `maintenance_checklists`

| Field | Kiểu | Bắt buộc | Ghi chú kiểm thử |
| ----- | ---- | -------- | ---------------- |
| `id` | Integer | Có | Primary key của checklist item |
| `task_id` | Integer | Có | Task liên quan |
| `item_name` | String(100) | Có | Không được rỗng |
| `status` | String(50) | Có | Nên thống nhất tập giá trị hợp lệ |
| `note` | String(255) | Không | Ghi chú tùy chọn |
| `created_at` | DateTime | Có | Tự sinh |
| `updated_at` | DateTime | Có | Tự cập nhật |

---

## C5. Danh sách API thực tế trong source code

### C5.1 Public API

| STT | Method | Endpoint | Controller | Quyền | Mục đích |
| --- | ------ | -------- | ---------- | ----- | -------- |
| 1 | `POST` | `/api/maintenance/tasks` | `create_maintenance_task` | Admin | Tạo task từ `booking_id` và `technician_id` |
| 2 | `GET` | `/api/maintenance/tasks` | `get_all_tasks_route` | Admin | Lấy toàn bộ task |
| 3 | `GET` | `/api/maintenance/my-tasks` | `get_my_tasks_route` | Đăng nhập | Lấy task của user hiện tại hoặc technician hiện tại |
| 4 | `GET` | `/api/maintenance/tasks/<task_id>` | `get_task_details_route` | Admin/customer owner/technician owner | Lấy chi tiết task |
| 5 | `PUT` | `/api/maintenance/tasks/<task_id>/status` | `update_task_status_route` | Admin/customer owner/technician owner | Cập nhật trạng thái |
| 6 | `POST` | `/api/maintenance/tasks/<task_id>/parts` | `add_part_to_task_route` | Admin/technician owner | Thêm phụ tùng vào task |
| 7 | `GET` | `/api/maintenance/tasks/<task_id>/parts` | `get_task_parts_route` | Đăng nhập | Lấy danh sách phụ tùng của task |
| 8 | `DELETE` | `/api/maintenance/parts/<part_id>` | `remove_part_route` | Admin/technician owner | Xóa phụ tùng khỏi task |
| 9 | `GET` | `/api/maintenance/completed-tasks-with-parts` | `get_completed_tasks_with_parts_route` | Admin | Lấy task completed kèm parts |
| 10 | `GET` | `/api/maintenance/bookings/<booking_id>/parts` | `get_booking_parts_route` | Internal token | Lấy parts theo booking cho Finance Service |
| 11 | `POST` | `/api/maintenance/tasks/<task_id>/checklist` | `add_checklist_item_route` | Admin/technician owner | Thêm checklist item |
| 12 | `GET` | `/api/maintenance/tasks/<task_id>/checklist` | `get_task_checklist_route` | Đăng nhập | Lấy checklist của task |
| 13 | `PUT` | `/api/maintenance/checklist/<item_id>` | `update_checklist_item_route` | Admin/technician owner | Cập nhật checklist item |
| 14 | `DELETE` | `/api/maintenance/checklist/<item_id>` | `remove_checklist_item_route` | Admin/technician owner | Xóa checklist item |

### C5.2 Internal API

| STT | Method | Endpoint | Controller | Quyền | Ghi chú |
| --- | ------ | -------- | ---------- | ----- | ------- |
| 1 | `GET` | `/internal/maintenance/due-soon` | `get_maintenance_due_soon` | `X-Internal-Token` | Lấy task sắp đến hạn |
| 2 | `GET` | `/internal/maintenance/task/<task_id>/info` | `get_task_info` | `X-Internal-Token` | Lấy thông tin task cho notification service |
| 3 | `GET` | `/internal/maintenance/technician/<technician_id>/stats` | `get_technician_stats` | `X-Internal-Token` | Thống kê task của technician |
| 4 | `GET` | `/internal/maintenance/health` | Không bắt token | Health check internal |

---

## C6. Ma trận phân quyền

| Chức năng | Admin | Customer owner | Technician owner | User khác | Internal service |
| --------- | ----- | -------------- | ---------------- | --------- | ---------------- |
| Tạo task | Được | Không | Không | Không | Không |
| Lấy toàn bộ task | Được | Không | Không | Không | Không |
| Lấy my-tasks | Được nếu có token | Được | Được | Được theo chính token của mình | Không |
| Xem chi tiết task | Được | Được nếu là owner | Được nếu được phân công | Không | Không |
| Cập nhật status | Được | Được nếu là owner theo code hiện tại | Được nếu được phân công | Không | Không |
| Thêm parts | Được | Không | Được nếu được phân công | Không | Không |
| Xem parts | Được nếu đăng nhập | Được nếu đăng nhập | Được nếu đăng nhập | Được nếu đăng nhập | Không |
| Xóa parts | Được | Không | Được nếu được phân công | Không | Không |
| Thêm checklist | Được | Không | Được nếu được phân công | Không | Không |
| Xem checklist | Được nếu đăng nhập | Được nếu đăng nhập | Được nếu đăng nhập | Được nếu đăng nhập | Không |
| Cập nhật checklist | Được | Không | Được nếu được phân công | Không | Không |
| Xóa checklist | Được | Không | Được nếu được phân công | Không | Không |
| Lấy parts theo booking | Không | Không | Không | Không | Được nếu có `X-Internal-Token` |

Ghi chú kiểm thử: một số route `GET parts` và `GET checklist` hiện chỉ yêu cầu đăng nhập, chưa kiểm tra owner task. Đây là điểm cần đánh giá lại về bảo mật dữ liệu.

---

## C7. Phân hoạch lớp tương đương mở rộng

### C7.1 Tạo task

| Input | Lớp hợp lệ | Lớp không hợp lệ |
| ----- | ---------- | ---------------- |
| `booking_id` | Số nguyên dương, tồn tại ở Booking Service | Thiếu, rỗng, chữ, `0`, âm, không tồn tại, Booking Service lỗi |
| `technician_id` | Số nguyên dương | Thiếu, rỗng, chữ, `0`, âm |
| Token | Admin hợp lệ | Không token, token sai, role không phải admin |
| Duplicate | Chưa có task cùng `booking_id` + `technician_id` | Đã tồn tại phân công trùng |

### C7.2 Cập nhật trạng thái

| Input | Lớp hợp lệ | Lớp không hợp lệ |
| ----- | ---------- | ---------------- |
| `task_id` | Số nguyên dương và tồn tại | `0`, âm, chữ, không tồn tại |
| `status` | `pending`, `in_progress`, `completed`, `failed` | Thiếu, rỗng, `cancelled`, `abc`, sai chữ hoa/thường |
| Quyền | Admin, customer owner, technician owner | User không liên quan |

### C7.3 Phụ tùng task

| Input | Lớp hợp lệ | Lớp không hợp lệ |
| ----- | ---------- | ---------------- |
| `task_id` | Task tồn tại | Task không tồn tại |
| `item_id` | Phụ tùng tồn tại trong inventory | Thiếu, không tồn tại, inventory service lỗi |
| `quantity` | Số nguyên dương, không vượt tồn kho | `0`, âm, chữ, vượt tồn kho |
| Quyền | Admin hoặc technician owner | Customer hoặc user khác |

### C7.4 Checklist

| Input | Lớp hợp lệ | Lớp không hợp lệ |
| ----- | ---------- | ---------------- |
| `item_name` | Chuỗi không rỗng | Thiếu, rỗng, quá dài |
| `status` | Giá trị được thống nhất như `pending`, `pass`, `fail`, `needs_repair`, `completed` | Rỗng, sai format, không thuộc danh sách cho phép |
| `note` | Có hoặc không có | Quá dài nếu vượt giới hạn database |
| Quyền | Admin hoặc technician owner | User không liên quan |

---

## C8. Boundary Value Analysis mở rộng

| Nhóm | Giá trị kiểm thử | Expected |
| ---- | ---------------- | -------- |
| `task_id` dưới biên | `-1` | 400 hoặc 404 tùy route, cần thống nhất |
| `task_id` tại biên không hợp lệ | `0` | 400 hoặc 404 tùy route, cần thống nhất |
| `task_id` nhỏ nhất hợp lệ | `1` | 200 nếu tồn tại, 404 nếu không tồn tại |
| `task_id` rất lớn | `999999999` | 404 |
| `booking_id` dưới biên | `0`, `-1` | 400 |
| `technician_id` dưới biên | `0`, `-1` | 400 |
| `quantity` dưới biên | `0`, `-1` | 400 |
| `quantity` tại biên hợp lệ | `1` | 201 nếu đủ tồn kho |
| `quantity` bằng tồn kho | `available_quantity` | 201 |
| `quantity` vượt tồn kho | `available_quantity + 1` | 400 |
| `item_name` rỗng | `""` | 400 |
| `item_name` dài 100 ký tự | 100 chars | 201 nếu DB cho phép |
| `item_name` dài 101 ký tự | 101 chars | 400 hoặc lỗi DB nếu chưa validate |
| `note` dài 255 ký tự | 255 chars | 200/201 |
| `note` dài 256 ký tự | 256 chars | 400 hoặc lỗi DB nếu chưa validate |

---

## C9. Bộ test case API đề xuất đầy đủ

### C9.1 Health check

| Mã test | Request | Expected |
| ------- | ------- | -------- |
| TC-HEALTH-01 | `GET /health` | 200, body có `Maintenance Service is running!` |
| TC-HEALTH-02 | `GET /internal/maintenance/health` | 200, body `success=true` |

### C9.2 Tạo task

| Mã test | Request/Input | Expected |
| ------- | ------------- | -------- |
| TC-CREATE-01 | Admin, `booking_id=1`, `technician_id=200` | 201, tạo task và checklist mặc định |
| TC-CREATE-02 | Thiếu `booking_id` | 400 |
| TC-CREATE-03 | Thiếu `technician_id` | 400 |
| TC-CREATE-04 | `booking_id=abc` | 400 |
| TC-CREATE-05 | `technician_id=abc` | 400 |
| TC-CREATE-06 | Booking Service lỗi | 400 |
| TC-CREATE-07 | Trùng `booking_id` + `technician_id` | 409 |
| TC-CREATE-08 | Customer gọi API tạo task | 403 |
| TC-CREATE-09 | Không token | 401 |

### C9.3 Lấy danh sách và chi tiết task

| Mã test | Request/Input | Expected |
| ------- | ------------- | -------- |
| TC-LIST-01 | Admin gọi `GET /api/maintenance/tasks` | 200, trả danh sách |
| TC-LIST-02 | Customer gọi list toàn bộ | 403 |
| TC-LIST-03 | Không token | 401 |
| TC-LIST-04 | `GET /api/maintenance/tasks?id=abc` | 400 nếu không hỗ trợ query `id` |
| TC-LIST-05 | `GET /api/maintenance/tasks?id=9999` | 400 nếu không hỗ trợ query `id`, hoặc 404 nếu có hỗ trợ |
| TC-DETAIL-01 | Admin xem task tồn tại | 200 |
| TC-DETAIL-02 | Customer owner xem task | 200 |
| TC-DETAIL-03 | Technician owner xem task | 200 |
| TC-DETAIL-04 | User không liên quan xem task | 403 |
| TC-DETAIL-05 | Task không tồn tại | 404 |
| TC-DETAIL-06 | `task_id=abc` | 404 theo Flask converter hiện tại hoặc 400 nếu custom validate |

### C9.4 My tasks

| Mã test | Request/Input | Expected |
| ------- | ------------- | -------- |
| TC-MYTASKS-01 | Customer token gọi `/my-tasks` | 200, trả task có `user_id` bằng identity |
| TC-MYTASKS-02 | Technician token gọi `/my-tasks` | 200, trả task có `technician_id` bằng identity |
| TC-MYTASKS-03 | Không token | 401 |
| TC-MYTASKS-04 | Token không có role | 200 hoặc 400 tùy yêu cầu, cần thống nhất |

### C9.5 Cập nhật trạng thái

| Mã test | Request/Input | Expected |
| ------- | ------------- | -------- |
| TC-STATUS-01 | Cập nhật `pending` -> `in_progress` | 200 |
| TC-STATUS-02 | Cập nhật `in_progress` -> `completed` | 200 |
| TC-STATUS-03 | Cập nhật `failed` | 200 |
| TC-STATUS-04 | Thiếu field `status` | 400 |
| TC-STATUS-05 | `status=abc` | 400 |
| TC-STATUS-06 | `status=cancelled` | 400 vì enum/service không hỗ trợ |
| TC-STATUS-07 | Task không tồn tại | 404 |
| TC-STATUS-08 | User không có quyền | 403 |

### C9.6 Parts

| Mã test | Request/Input | Expected |
| ------- | ------------- | -------- |
| TC-PART-01 | Admin thêm part hợp lệ | 201 |
| TC-PART-02 | Technician owner thêm part hợp lệ | 201 |
| TC-PART-03 | Customer thêm part | 403 |
| TC-PART-04 | Task không tồn tại | 404 |
| TC-PART-05 | Thiếu `item_id` | 400 |
| TC-PART-06 | `quantity=0` | 400 nếu bổ sung validate |
| TC-PART-07 | `quantity=-1` | 400 nếu bổ sung validate |
| TC-PART-08 | Inventory Service lỗi | 400 |
| TC-PART-09 | Phụ tùng không tồn tại trong inventory | 400 |
| TC-PART-10 | Quantity vượt tồn kho | 400 |
| TC-PART-11 | Thêm lại cùng `item_id` | 200/201, quantity được cộng dồn |
| TC-PART-12 | Xem parts của task | 200 |
| TC-PART-13 | Xóa part tồn tại | 200 |
| TC-PART-14 | Xóa part không tồn tại | 404 |
| TC-PART-15 | User không có quyền xóa part | 403 |

### C9.7 Checklist

| Mã test | Request/Input | Expected |
| ------- | ------------- | -------- |
| TC-CHECKLIST-01 | Admin thêm checklist item | 201 |
| TC-CHECKLIST-02 | Technician owner thêm checklist item | 201 |
| TC-CHECKLIST-03 | Thiếu `item_name` | 400 |
| TC-CHECKLIST-04 | Task không tồn tại | 404 |
| TC-CHECKLIST-05 | User không có quyền thêm checklist | 403 |
| TC-CHECKLIST-06 | Lấy checklist theo task | 200 |
| TC-CHECKLIST-07 | Cập nhật status/note checklist | 200 |
| TC-CHECKLIST-08 | Checklist item không tồn tại | 404 |
| TC-CHECKLIST-09 | Technician không phải owner cập nhật checklist | 403 |
| TC-CHECKLIST-10 | Xóa checklist item | 200 |
| TC-CHECKLIST-11 | Xóa checklist không tồn tại | 404 |

### C9.8 Internal API

| Mã test | Request/Input | Expected |
| ------- | ------------- | -------- |
| TC-INTERNAL-01 | Gọi internal API thiếu `X-Internal-Token` | 401 |
| TC-INTERNAL-02 | Gọi internal API sai token | 401 |
| TC-INTERNAL-03 | Gọi `/technician/<id>/stats` đúng token | 200, có thống kê |
| TC-INTERNAL-04 | Gọi `/task/<task_id>/info` với task không tồn tại | 404 |
| TC-INTERNAL-05 | Gọi `/bookings/<booking_id>/parts` đúng internal token | 200 nếu có task, 404 nếu không có |

---

## C10. Kiểm thử white-box cho service layer

Các hàm cần bao phủ trong `services/maintenance_service.py`:

| Hàm | Nhánh cần test |
| --- | -------------- |
| `_call_internal_api` | Thiếu config, HTTP 200/201, HTTP lỗi, exception kết nối |
| `_get_booking_details` | Gọi đúng endpoint booking |
| `_get_user_profile` | Gọi đúng endpoint user |
| `get_task_by_id` | Có task, không có task |
| `get_all_tasks` | Có dữ liệu, database rỗng, thứ tự `created_at desc` |
| `get_tasks_by_user` | Có task, không có task, user_id sai kiểu |
| `get_tasks_by_technician` | Có task, không có task, technician_id sai kiểu |
| `create_task_from_booking` | Thành công, duplicate, booking service lỗi, user service lỗi fallback, DB exception |
| `update_task_status` | Thành công, task không tồn tại, status sai, DB exception |
| `_check_inventory_stock` | Thiếu URL, inventory trả 200, inventory lỗi |
| `add_part_to_task` | Task không tồn tại, inventory lỗi, part không tồn tại, vượt tồn kho, thêm mới, cộng dồn |
| `get_task_parts` | Có parts, không có parts |
| `remove_part_from_task` | Part tồn tại, part không tồn tại |
| `get_completed_tasks_with_parts` | Task completed có parts, completed không parts, không có completed |
| `get_task_parts_by_booking_id` | Booking có task, booking không có task |
| `add_checklist_item` | Thành công, task không tồn tại |
| `get_task_checklist` | Có checklist, không có checklist |
| `update_checklist_item` | Thành công, item không tồn tại, không có quyền, user_id lỗi kiểu |
| `remove_checklist_item` | Thành công, item không tồn tại, không có quyền, DB exception |

---

## C11. Kết quả chạy pytest hiện tại

Lệnh đã chạy:

```bash
python -m pytest -q
```

Kết quả ghi nhận:

```text
24 test collected
18 passed
6 failed
```

Các nhóm lỗi hiện tại:

| Mã lỗi | Test fail | Nguyên nhân |
| ------ | --------- | ----------- |
| BUG-TEST-01 | `test_create_task_success` | Database test dùng chung theo session nên dữ liệu từ test trước còn tồn tại, làm case tạo task bị nhận là duplicate |
| BUG-TEST-02 | `test_create_task_booking_error` | Cũng bị ảnh hưởng bởi dữ liệu duplicate từ test trước, chưa đi được đến nhánh Booking Service lỗi |
| BUG-TEST-03 | `test_create_task_db_exception` | Cũng bị ảnh hưởng bởi dữ liệu duplicate từ test trước, chưa đi được đến nhánh DB exception |
| BUG-TEST-04 | `test_update_checklist_success` | Test gọi `item.item_id` nhưng model `MaintenanceChecklist` chỉ có field `id` |
| BUG-TEST-05 | `test_update_checklist_permission_denied` | Test gọi `item.item_id` sai field |
| BUG-TEST-06 | `test_remove_checklist_success` | Test gọi `item.item_id` sai field |

Ngoài ra pytest có cảnh báo:

| Cảnh báo | Ý nghĩa |
| -------- | ------- |
| `LegacyAPIWarning: Query.get()` | SQLAlchemy 2.x khuyến nghị dùng `db.session.get(Model, id)` thay cho `Model.query.get(id)` |
| Không ghi được `.pytest_cache` | Môi trường chạy test không có quyền ghi vào cache path hiện tại, không ảnh hưởng logic test nhưng nên xử lý quyền thư mục |

---

## C12. Bug/rủi ro source code cần ghi nhận thêm

| Mã bug | Vị trí | Mô tả | Ảnh hưởng | Đề xuất |
| ------ | ----- | ----- | --------- | ------- |
| BUG-SRC-01 | `get_all_tasks_route` | Bỏ qua query parameter `id` | `GET /tasks?id=abc` và `id=9999` trả sai `200 OK` | Chặn `id` bằng 400 hoặc hỗ trợ filter có validate |
| BUG-SRC-02 | `remove_part_route` và `remove_part_from_task` | Controller gọi `service.remove_part_from_task(part_id, current_user_id, is_admin)` nhưng service chỉ nhận `part_id` | Khi gọi DELETE part có thể phát sinh `TypeError` | Đồng bộ chữ ký hàm và bổ sung kiểm tra quyền |
| BUG-SRC-03 | `internal_controller.py` | Dùng các field không có trong `MaintenanceTask`: `id`, `license_plate`, `brand`, `model`, `task_type`, `priority`, `scheduled_date`, `completed_date` | Internal API `/due-soon` và `/task/<id>/info` có nguy cơ lỗi 500 | Sửa controller theo model hiện tại hoặc mở rộng model/migration |
| BUG-SRC-04 | `get_task_parts_route` | Chỉ yêu cầu đăng nhập, chưa check quyền owner | User đăng nhập có thể xem parts task không thuộc mình | Dùng `_check_task_permission` giống route detail |
| BUG-SRC-05 | `get_task_checklist_route` | Chỉ yêu cầu đăng nhập, chưa check quyền owner | User đăng nhập có thể xem checklist task không thuộc mình | Dùng `_check_task_permission` giống route detail |
| BUG-SRC-06 | `add_part_to_task` | Chưa validate `quantity` là số nguyên dương | Có thể thêm `0`, âm hoặc kiểu sai nếu request truyền không chuẩn | Validate `quantity` ở controller/service |
| BUG-SRC-07 | `add_checklist_item` và `update_checklist_item` | Chưa thống nhất tập giá trị `status` của checklist | Dữ liệu checklist có thể không đồng nhất | Định nghĩa danh sách status hợp lệ |
| BUG-SRC-08 | `conftest.py` | Database fixture scope session, không reset dữ liệu giữa từng test | Test phụ thuộc thứ tự chạy, dễ fail duplicate | Dọn bảng sau mỗi test hoặc đổi fixture scope |

---

## C13. Hướng hoàn thiện test tự động

### C13.1 Sửa fixture để test độc lập

Đề xuất trong `test/conftest.py`:

```python
@pytest.fixture(autouse=True)
def clean_database(app_context):
    yield
    db.session.rollback()
    MaintenanceChecklist.query.delete()
    TaskPart.query.delete()
    MaintenanceTask.query.delete()
    db.session.commit()
```

Mục tiêu:

* Mỗi test có database sạch.
* Không còn lỗi duplicate do dữ liệu test trước để lại.
* Test có thể chạy độc lập hoặc chạy theo thứ tự bất kỳ.

### C13.2 Sửa field checklist trong test

Các đoạn:

```python
item.item_id
```

nên đổi thành:

```python
item.id
```

vì model `MaintenanceChecklist` định nghĩa primary key là `id`.

### C13.3 Bổ sung test controller/API

Hiện test chủ yếu kiểm tra service layer. Cần bổ sung test route bằng Flask test client:

| Nhóm | Test cần bổ sung |
| ---- | ---------------- |
| Auth | Không token, token sai, role sai |
| Route list/detail | `GET /tasks`, `/tasks/<id>`, `/tasks?id=abc`, `/tasks?id=9999` |
| Status | PUT status hợp lệ/sai |
| Parts | POST/GET/DELETE parts |
| Checklist | POST/GET/PUT/DELETE checklist |
| Internal | Token đúng/sai cho internal API |

---

## C14. Gợi ý Postman collection đầy đủ

Nên tạo các folder trong Postman như sau:

```text
Maintenance Service
├── 00 Health
├── 01 Auth Setup
├── 02 Tasks
├── 03 My Tasks
├── 04 Status
├── 05 Parts
├── 06 Checklist
├── 07 Internal APIs
└── 99 Negative Cases
```

Biến môi trường Postman:

| Biến | Ví dụ |
| ---- | ----- |
| `base_url` | `http://localhost:5000` hoặc URL gateway |
| `admin_token` | JWT role admin |
| `customer_token` | JWT role customer |
| `technician_token` | JWT role technician |
| `other_user_token` | JWT user không sở hữu task |
| `internal_token` | Token nội bộ |
| `task_id` | ID task tồn tại |
| `missing_task_id` | `999999` |
| `booking_id` | ID booking test |
| `technician_id` | ID technician test |
| `part_id` | ID part test |
| `checklist_item_id` | ID checklist item test |

Ví dụ script Postman cho status code:

```javascript
pm.test("Status code is expected", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is JSON", function () {
    pm.response.to.be.json;
});
```

Ví dụ script lưu `task_id` sau khi tạo task:

```javascript
const body = pm.response.json();
if (body.task && body.task.task_id) {
    pm.environment.set("task_id", body.task.task_id);
}
```

---

## C15. Checklist hoàn thành kiểm thử Maintenance Service

| Hạng mục | Trạng thái đề xuất |
| -------- | ------------------ |
| Đọc source controller, service, model | Hoàn thành |
| Lập danh sách endpoint thực tế | Hoàn thành |
| Phân hoạch lớp tương đương cho task/status/parts/checklist | Hoàn thành |
| Phân tích giá trị biên | Hoàn thành |
| Ghi nhận lỗi query `id` | Hoàn thành |
| Chạy pytest hiện tại | Hoàn thành, 18 pass / 6 fail |
| Ghi nhận lỗi test và source risk | Hoàn thành |
| Bổ sung test controller/API | Cần thực hiện |
| Sửa fixture reset database | Cần thực hiện |
| Sửa test `item.item_id` thành `item.id` | Cần thực hiện |
| Sửa route xóa part để khớp service | Cần thực hiện |
| Sửa hoặc đồng bộ internal controller với model | Cần thực hiện |
| Chạy lại pytest sau khi sửa | Cần thực hiện |
| Xuất coverage HTML | Cần thực hiện |
| Tạo Postman collection đầy đủ | Cần thực hiện |

---

## C16. Tổng hợp phần bổ sung

Maintenance Service hiện đã có đủ nền tảng chức năng chính: quản lý task bảo trì, phân công technician, cập nhật trạng thái, ghi nhận phụ tùng, checklist và API nội bộ. Tuy nhiên để tài liệu kiểm thử đầy đủ hơn, cần mở rộng phạm vi từ hai lỗi `id=abc` và `id=9999` sang toàn bộ các nhóm nghiệp vụ:

* Task lifecycle: tạo, xem, cập nhật trạng thái.
* Phân quyền: admin, customer owner, technician owner, user không liên quan.
* Tích hợp service ngoài: Booking, User, Inventory, Finance, Notification.
* Dữ liệu con của task: parts và checklist.
* Internal API và token nội bộ.
* Test tự động, fixture database, coverage và regression test.

Kết quả chạy test hiện tại cho thấy service chưa thể xem là hoàn tất kiểm thử vì còn 6 test fail và một số rủi ro source code. Sau khi sửa fixture, sửa field checklist trong test, đồng bộ route xóa part và rà lại internal controller, cần chạy lại:

```bash
python -m pytest -q
python -m pytest --cov=. --cov-report=html
```

Khi toàn bộ test pass và các API negative case trả đúng status code, Maintenance Service mới đạt trạng thái kiểm thử đầy đủ hơn cho cả tài liệu assignment và kiểm thử thực tế.

---

# PHẦN D. KẾT LUẬN

Qua bài kiểm thử Maintenance Service, em đã áp dụng được các kỹ thuật:

* Phân hoạch lớp tương đương.
* Phân tích giá trị biên.
* Thiết kế test case.
* Kiểm thử API bằng Postman.
* Phân tích lỗi dựa trên source code.
* Đề xuất hướng sửa và kiểm thử tự động.

Kết quả kiểm thử ban đầu phát hiện 2 lỗi chính tại endpoint lấy danh sách:

1. Khi gọi `GET /api/maintenance/tasks?id=abc`, hệ thống không báo lỗi dữ liệu sai kiểu mà trả `200 OK`.
2. Khi gọi `GET /api/maintenance/tasks?id=9999`, hệ thống không báo lỗi task không tồn tại mà trả `200 OK`.

Nguyên nhân là route `/api/maintenance/tasks` đang bỏ qua query parameter `id` và luôn gọi hàm lấy toàn bộ danh sách task. Để khắc phục, hệ thống nên thống nhất thiết kế API:

* Nếu lấy danh sách thì dùng `GET /api/maintenance/tasks`.
* Nếu lấy chi tiết thì dùng `GET /api/maintenance/tasks/<task_id>`.
* Nếu client truyền `id` vào query string thì API cần trả lỗi `400 Bad Request` hoặc xử lý validate rõ ràng.

Sau khi mở rộng kiểm thử toàn bộ thư mục `maintenance-service`, bài làm cũng ghi nhận thêm các điểm cần hoàn thiện: test hiện tại chạy `24` case với `18` pass và `6` fail, route xóa phụ tùng chưa khớp chữ ký service, một số internal API đang tham chiếu field không có trong model, và một số route xem `parts`/`checklist` cần kiểm tra quyền chặt hơn.

Vì vậy, Maintenance Service chưa nên xem là hoàn tất kiểm thử cho đến khi sửa các lỗi đã ghi nhận, bổ sung test controller/API, chạy lại toàn bộ pytest và xuất coverage. Sau khi toàn bộ test pass và các negative case trả đúng status code, service mới đạt trạng thái ổn định hơn cho cả tài liệu assignment và kiểm thử thực tế.
