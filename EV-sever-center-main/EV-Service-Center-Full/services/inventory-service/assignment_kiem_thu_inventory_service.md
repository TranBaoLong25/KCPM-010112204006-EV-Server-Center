# Assignment: Kiểm thử chức năng Inventory Service

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

1. Xác định điều kiện kiểm thử cho chức năng quản lý kho vật tư trong Inventory Service.
2. Áp dụng kỹ thuật phân hoạch lớp tương đương cho dữ liệu đầu vào như `part_number`, `quantity`, `price`, `center_id`.
3. Áp dụng kỹ thuật phân tích giá trị biên cho các trường số như `quantity`, `price`, `item_id`, `center_id`.
4. Thiết kế test case cho API thêm, sửa, xóa, lấy danh sách và kiểm tra vật tư sắp hết hàng.
5. Ghi nhận lỗi thực tế khi kiểm thử bằng Postman.
6. Tích hợp kết quả kiểm thử với GitHub Actions và Jira để tự động ghi nhận bug.
7. Đề xuất hướng xử lý lỗi và viết kiểm thử tự động để xác nhận hệ thống hoạt động đúng.

---

# 2. Nội dung tham khảo

Trong bài này em áp dụng các kỹ thuật kiểm thử sau:

* **Equivalence Partitioning:** chia dữ liệu đầu vào thành nhóm hợp lệ và không hợp lệ.
* **Boundary Value Analysis (BVA):** chọn dữ liệu tại vùng biên như `quantity = -1`, `quantity = 0`, `quantity = 1`, `price = -1`, `price = 0`, `center_id = 0`.
* **API Testing:** kiểm thử endpoint bằng Postman với token xác thực.
* **Negative Testing:** kiểm thử các trường hợp thiếu token, body rỗng, giá trị âm, ID không tồn tại.
* **CI/CD Testing:** dùng GitHub Actions chạy Newman để thực thi Postman Collection tự động.
* **Jira Integration:** đồng bộ test case từ Postman sang Jira và tự động tạo bug khi testcase fail.

---

# 3. Mô tả bài toán

Hệ thống EV Service Center có **Inventory Service** dùng để quản lý kho vật tư, phụ tùng phục vụ bảo dưỡng xe điện.

Inventory Service hỗ trợ các chức năng chính:

| Chức năng | Endpoint | Method | Mô tả |
| -------- | -------- | ------ | ----- |
| Thêm vật tư | `/api/inventory/items` | POST | Thêm một vật tư/phụ tùng mới vào kho |
| Lấy danh sách vật tư | `/api/inventory/items` | GET | Lấy toàn bộ danh sách vật tư |
| Lấy chi tiết vật tư | `/api/inventory/items/<item_id>` | GET | Lấy thông tin chi tiết của một vật tư |
| Cập nhật vật tư | `/api/inventory/items/<item_id>` | PUT | Cập nhật số lượng, giá, tên, chi nhánh |
| Xóa vật tư | `/api/inventory/items/<item_id>` | DELETE | Xóa vật tư khỏi kho |
| Kiểm tra vật tư sắp hết | `/api/inventory/low-stock` | GET | Lấy danh sách vật tư có `quantity <= min_quantity` |
| Gợi ý phụ tùng | `/api/inventory/suggest-parts` | POST | Gợi ý phụ tùng theo model xe hoặc category |
| Nạp dữ liệu demo | `/api/inventory/seed-ai-data` | POST | Tạo dữ liệu mẫu phục vụ demo AI |

Trong bài assignment này, phạm vi kiểm thử tập trung vào các API chính:

```text
GET    /api/inventory/items
POST   /api/inventory/items
PUT    /api/inventory/items/<item_id>
DELETE /api/inventory/items/<item_id>
GET    /api/inventory/low-stock
```

---

# 4. Yêu cầu nghiệp vụ mong đợi

## 4.1 Quy tắc xác thực

Các API quản lý kho cần yêu cầu token hợp lệ:

```http
Authorization: Bearer <access_token>
```

Kết quả mong đợi:

```text
HTTP 200/201 nếu token hợp lệ và dữ liệu đúng
HTTP 401 Unauthorized nếu thiếu token hoặc token sai
```

Các API cần kiểm soát token:

```text
GET    /api/inventory/items
POST   /api/inventory/items
PUT    /api/inventory/items/<item_id>
DELETE /api/inventory/items/<item_id>
GET    /api/inventory/low-stock
```

## 4.2 Quy tắc thêm vật tư

Endpoint:

```http
POST /api/inventory/items
```

Điều kiện hợp lệ:

| Trường | Kiểu dữ liệu | Điều kiện |
| ------ | ------------ | --------- |
| `name` | string | Không rỗng |
| `part_number` | string | Không rỗng, không trùng trong cùng chi nhánh |
| `quantity` | integer | `quantity >= 0` |
| `min_quantity` | integer | `min_quantity >= 0` |
| `price` | number | `price > 0` |
| `center_id` | integer | `center_id >= 1` |

Kết quả mong đợi:

```text
HTTP 201 Created nếu dữ liệu hợp lệ
HTTP 400 Bad Request nếu dữ liệu sai kiểu hoặc sai miền giá trị
HTTP 409 Conflict nếu part_number bị trùng
HTTP 401 Unauthorized nếu thiếu token
```

## 4.3 Quy tắc cập nhật vật tư

Endpoint:

```http
PUT /api/inventory/items/<item_id>
```

Điều kiện hợp lệ:

| Trường | Điều kiện |
| ------ | --------- |
| `item_id` | Số nguyên dương và tồn tại trong database |
| Body | Không được rỗng |
| `quantity` | Cho phép `0`, `1`, số nguyên dương; không cho phép số âm |
| `price` | Phải lớn hơn 0 |
| `center_id` | Phải lớn hơn 0 |

Kết quả mong đợi:

```text
HTTP 200 OK nếu cập nhật hợp lệ
HTTP 400 Bad Request nếu body rỗng hoặc dữ liệu sai
HTTP 404 Not Found nếu vật tư không tồn tại
HTTP 401 Unauthorized nếu thiếu token
```

## 4.4 Quy tắc kiểm tra vật tư sắp hết

Endpoint:

```http
GET /api/inventory/low-stock?center_id=1
```

Điều kiện hợp lệ:

| Trường | Điều kiện |
| ------ | --------- |
| `center_id` | Nếu truyền thì phải là số nguyên dương |
| `quantity` | Vật tư được coi là sắp hết nếu `quantity <= min_quantity` |

Kết quả mong đợi:

```text
HTTP 200 OK nếu center_id hợp lệ
HTTP 400 Bad Request nếu center_id <= 0
HTTP 401 Unauthorized nếu thiếu token
```

---

# 5. Mô tả lỗi phát hiện

## 5.1 Lỗi 1: API Inventory chưa kiểm tra token ở một số endpoint

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-INV-01 |
| Chức năng | Xác thực API Inventory |
| Endpoint | `/api/inventory/items`, `/api/inventory/items/<id>`, `/api/inventory/low-stock` |
| Dữ liệu đầu vào | Request không có Bearer Token |
| Kết quả thực tế | Một số API vẫn xử lý request |
| Kết quả mong đợi | API phải trả `401 Unauthorized` |
| Mức độ nghiêm trọng | High |
| Trạng thái | Fixed |

### Testcase liên quan

| Mã testcase | Mô tả |
| ----------- | ----- |
| EP-INV-GET-02 | Không token khi lấy danh sách |
| EP-INV-ADD-05 | Không token khi thêm vật tư |
| EP-INV-UPD-03 | Không token khi cập nhật |
| EP-INV-DEL-01 | Không token khi xóa |
| EP-INV-LOW-01 | Có token hợp lệ khi lấy low-stock |

### Nguyên nhân phân tích

Một số route trong `inventory_controller.py` chưa được gắn decorator:

```python
@jwt_required()
```

Do đó API vẫn xử lý request dù thiếu token.

### Hướng xử lý

Thêm:

```python
from flask_jwt_extended import jwt_required
```

và gắn:

```python
@jwt_required()
```

cho các route cần bảo vệ.

---

## 5.2 Lỗi 2: Cho phép tạo vật tư với `quantity = -1`

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-INV-02 |
| Chức năng | Thêm vật tư |
| Method | POST |
| Endpoint | `/api/inventory/items` |
| Dữ liệu đầu vào | `quantity = -1` |
| Kết quả thực tế | API vẫn cho tạo hoặc xử lý không đúng |
| Kết quả mong đợi | `400 Bad Request` |
| Mức độ nghiêm trọng | Medium |
| Trạng thái | Fixed |

### Testcase liên quan

```text
BVA-INV-ADD-01 Quantity = -1
```

### Nguyên nhân phân tích

Service chưa validate miền giá trị của `quantity`.

### Hướng xử lý

Trong `create_item(data)` thêm kiểm tra:

```python
if quantity < 0:
    return None, "quantity không được nhỏ hơn 0"
```

---

## 5.3 Lỗi 3: Cho phép tạo vật tư với `price = -1` hoặc `price = 0`

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-INV-03 |
| Chức năng | Thêm vật tư |
| Method | POST |
| Endpoint | `/api/inventory/items` |
| Dữ liệu đầu vào | `price = -1`, `price = 0` |
| Kết quả mong đợi | `400 Bad Request` |
| Mức độ nghiêm trọng | Medium |
| Trạng thái | Fixed |

### Testcase liên quan

```text
BVA-INV-ADD-04 Price = -1
BVA-INV-ADD-05 Price = 0
```

### Hướng xử lý

Trong `create_item(data)` thêm:

```python
if price <= 0:
    return None, "price phải lớn hơn 0"
```

---

## 5.4 Lỗi 4: Cập nhật vật tư chưa validate body và quantity

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-INV-04 |
| Chức năng | Cập nhật vật tư |
| Method | PUT |
| Endpoint | `/api/inventory/items/<item_id>` |
| Kết quả thực tế | Body rỗng hoặc quantity biên xử lý chưa đúng |
| Kết quả mong đợi | Body rỗng trả 400; quantity 0 và 1 là hợp lệ |
| Mức độ nghiêm trọng | Medium |
| Trạng thái | Fixed |

### Testcase liên quan

```text
EP-INV-UPD-01 Body hợp lệ
EP-INV-UPD-02 Body rỗng
BVA-INV-UPD-04 Quantity = 0
BVA-INV-UPD-05 Quantity = 1
```

### Nguyên nhân phân tích

Hàm `update_item(item_id, data)` chưa phân biệt rõ:

* Body rỗng.
* Quantity âm.
* Quantity bằng 0 là hợp lệ.
* Quantity bằng 1 là hợp lệ.

### Hướng xử lý

Trong `update_item()` thêm:

```python
if not data:
    return None, "Body không được rỗng"
```

và validate quantity:

```python
if "quantity" in data:
    quantity = int(data["quantity"])
    if quantity < 0:
        return None, "quantity không được nhỏ hơn 0"
    item.quantity = quantity
```

---

## 5.5 Lỗi 5: Low-stock không validate `center_id = 0`

### Thông tin kiểm thử

| Thuộc tính | Giá trị |
| ---------- | ------- |
| Mã lỗi | BUG-INV-05 |
| Chức năng | Lấy danh sách vật tư sắp hết |
| Method | GET |
| Endpoint | `/api/inventory/low-stock?center_id=0` |
| Dữ liệu đầu vào | `center_id = 0` |
| Kết quả mong đợi | `400 Bad Request` |
| Mức độ nghiêm trọng | Medium |
| Trạng thái | Fixed |

### Testcase liên quan

```text
BVA-INV-LOW-01 Center ID = 0
```

### Hướng xử lý

Trong controller:

```python
if center_id is not None and center_id <= 0:
    return jsonify({"error": "center_id phải lớn hơn 0"}), 400
```

---

# PHẦN A. BÀI LÀM

---

## Câu 1. Xác định lớp tương đương

### 1.1 Phân hoạch cho `quantity`

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| `quantity` | Số nguyên >= 0 | V1 | Số âm, ví dụ `-1` | X1 |
| | | | Chuỗi chữ, ví dụ `abc` | X2 |
| | | | Giá trị rỗng không đúng kiểu | X3 |

### 1.2 Phân hoạch cho `price`

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| `price` | Số thực > 0 | V2 | `price = 0` | X4 |
| | | | `price < 0` | X5 |
| | | | Chuỗi chữ, ví dụ `abc` | X6 |

### 1.3 Phân hoạch cho `center_id`

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| `center_id` | Số nguyên dương | V3 | `center_id = 0` | X7 |
| | | | `center_id < 0` | X8 |
| | | | Sai kiểu dữ liệu | X9 |

### 1.4 Phân hoạch cho token

| Biến đầu vào | Lớp hợp lệ | Tag | Lớp không hợp lệ | Tag |
| ------------ | ---------- | --- | ---------------- | --- |
| Bearer Token | Token hợp lệ, chưa hết hạn | V4 | Không có token | X10 |
| | | | Token sai | X11 |
| | | | Token hết hạn | X12 |

---

## Câu 2. Phân tích giá trị biên

### 2.1 Giá trị biên cho `quantity`

| Giá trị | Ý nghĩa | Kết quả mong đợi |
| ------- | ------- | ---------------- |
| `-1` | Dưới biên | 400 Bad Request |
| `0` | Biên hợp lệ nhỏ nhất | 200/201 OK |
| `1` | Ngay trên biên | 200/201 OK |

### 2.2 Giá trị biên cho `price`

| Giá trị | Ý nghĩa | Kết quả mong đợi |
| ------- | ------- | ---------------- |
| `-1` | Dưới biên | 400 Bad Request |
| `0` | Tại biên không hợp lệ | 400 Bad Request |
| `1` | Giá hợp lệ nhỏ nhất | 200/201 OK |

### 2.3 Giá trị biên cho `center_id`

| Giá trị | Ý nghĩa | Kết quả mong đợi |
| ------- | ------- | ---------------- |
| `0` | Không hợp lệ | 400 Bad Request |
| `1` | Hợp lệ nhỏ nhất | 200 OK |
| `99999` | Giá trị lớn, có thể không có dữ liệu | 200 OK hoặc danh sách rỗng |

---

## Câu 3. Thiết kế test case

### 3.1 Test case lấy danh sách vật tư

| STT | Mã test case | Mô tả | Request | Expected | Actual | Trạng thái |
| --: | ------------ | ----- | ------- | -------- | ------ | ---------- |
| 1 | EP-INV-GET-01 | Có token hợp lệ | `GET /api/inventory/items` | 200 OK | 200 OK | Pass |
| 2 | EP-INV-GET-02 | Không token | `GET /api/inventory/items` | 401 Unauthorized | Đã phát hiện lỗi trước khi sửa | Fixed |

### 3.2 Test case thêm vật tư

| STT | Mã test case | Mô tả | Request | Expected | Actual | Trạng thái |
| --: | ------------ | ----- | ------- | -------- | ------ | ---------- |
| 1 | EP-INV-ADD-01 | Body hợp lệ | `POST /api/inventory/items` | 201 Created | 201 Created | Pass |
| 2 | BVA-INV-ADD-01 | Quantity = -1 | `POST /api/inventory/items` | 400 Bad Request | Fail trước khi sửa | Fixed |
| 3 | BVA-INV-ADD-04 | Price = -1 | `POST /api/inventory/items` | 400 Bad Request | Fail trước khi sửa | Fixed |
| 4 | BVA-INV-ADD-05 | Price = 0 | `POST /api/inventory/items` | 400 Bad Request | Fail trước khi sửa | Fixed |
| 5 | EP-INV-ADD-05 | Không token | `POST /api/inventory/items` | 401 Unauthorized | Fail trước khi sửa | Fixed |

### 3.3 Test case cập nhật vật tư

| STT | Mã test case | Mô tả | Request | Expected | Actual | Trạng thái |
| --: | ------------ | ----- | ------- | -------- | ------ | ---------- |
| 1 | EP-INV-UPD-01 | Body hợp lệ | `PUT /api/inventory/items/<id>` | 200 OK | Fail trước khi sửa | Fixed |
| 2 | EP-INV-UPD-02 | Body rỗng | `PUT /api/inventory/items/<id>` | 400 Bad Request | Fail trước khi sửa | Fixed |
| 3 | EP-INV-UPD-03 | Không token | `PUT /api/inventory/items/<id>` | 401 Unauthorized | Fail trước khi sửa | Fixed |
| 4 | BVA-INV-UPD-04 | Quantity = 0 | `PUT /api/inventory/items/<id>` | 200 OK | Fail trước khi sửa | Fixed |
| 5 | BVA-INV-UPD-05 | Quantity = 1 | `PUT /api/inventory/items/<id>` | 200 OK | Fail trước khi sửa | Fixed |

### 3.4 Test case xóa vật tư

| STT | Mã test case | Mô tả | Request | Expected | Actual | Trạng thái |
| --: | ------------ | ----- | ------- | -------- | ------ | ---------- |
| 1 | EP-INV-DEL-01 | Không token | `DELETE /api/inventory/items/<id>` | 401 Unauthorized | Fail trước khi sửa | Fixed |

### 3.5 Test case vật tư sắp hết

| STT | Mã test case | Mô tả | Request | Expected | Actual | Trạng thái |
| --: | ------------ | ----- | ------- | -------- | ------ | ---------- |
| 1 | EP-INV-LOW-01 | Có token hợp lệ | `GET /api/inventory/low-stock` | 200 OK | Fail trước khi sửa | Fixed |
| 2 | BVA-INV-LOW-01 | Center ID = 0 | `GET /api/inventory/low-stock?center_id=0` | 400 Bad Request | Fail trước khi sửa | Fixed |

---

## Câu 4. Bảng mô tả lỗi

| Mã lỗi | Testcase | Expected | Actual | Nguyên nhân | Mức độ |
| ------ | -------- | -------- | ------ | ----------- | ------ |
| BUG-INV-01 | EP-INV-GET-02, EP-INV-ADD-05, EP-INV-UPD-03, EP-INV-DEL-01 | 401 Unauthorized | API vẫn xử lý request | Chưa gắn `@jwt_required()` | High |
| BUG-INV-02 | BVA-INV-ADD-01 | 400 Bad Request | Cho phép quantity âm | Chưa validate `quantity < 0` | Medium |
| BUG-INV-03 | BVA-INV-ADD-04, BVA-INV-ADD-05 | 400 Bad Request | Cho phép price <= 0 | Chưa validate `price <= 0` | Medium |
| BUG-INV-04 | EP-INV-UPD-02 | 400 Bad Request | Body rỗng vẫn xử lý | Chưa validate body rỗng | Medium |
| BUG-INV-05 | BVA-INV-LOW-01 | 400 Bad Request | `center_id = 0` vẫn xử lý | Chưa validate `center_id <= 0` | Medium |

---

## Câu 5. Phân tích nguyên nhân trong source code

File liên quan:

```text
EV-Service-Center-Full/services/inventory-service/controllers/inventory_controller.py
EV-Service-Center-Full/services/inventory-service/services/inventory_service.py
```

Các nguyên nhân chính:

1. Controller chưa gắn `@jwt_required()` cho các endpoint cần xác thực.
2. Service chưa validate giá trị âm của `quantity`.
3. Service chưa validate `price <= 0`.
4. Hàm update chưa xử lý body rỗng.
5. Hàm low-stock chưa kiểm tra `center_id <= 0`.

---

## Câu 6. Đề xuất hướng khắc phục

### 6.1 Thêm xác thực JWT

```python
@inventory_bp.route("/items", methods=["GET"])
@jwt_required()
def get_all_items():
    ...
```

Áp dụng cho các endpoint thêm, sửa, xóa, lấy low-stock.

### 6.2 Validate khi thêm vật tư

```python
if quantity < 0:
    return None, "quantity không được nhỏ hơn 0"

if price <= 0:
    return None, "price phải lớn hơn 0"
```

### 6.3 Validate khi cập nhật vật tư

```python
if not data:
    return None, "Body không được rỗng"

if "quantity" in data:
    quantity = int(data["quantity"])
    if quantity < 0:
        return None, "quantity không được nhỏ hơn 0"
```

### 6.4 Validate low-stock center_id

```python
if center_id is not None and center_id <= 0:
    return jsonify({"error": "center_id phải lớn hơn 0"}), 400
```

---

## Câu 7. Thiết kế kiểm thử tự động

### 7.1 Unit test validate quantity

```python
def validate_quantity(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return False

    return value >= 0
```

```python
def test_quantity_negative():
    assert validate_quantity(-1) is False

def test_quantity_zero():
    assert validate_quantity(0) is True

def test_quantity_one():
    assert validate_quantity(1) is True
```

### 7.2 Unit test validate price

```python
def validate_price(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return False

    return value > 0
```

```python
def test_price_negative():
    assert validate_price(-1) is False

def test_price_zero():
    assert validate_price(0) is False

def test_price_positive():
    assert validate_price(1) is True
```

### 7.3 API test bằng pytest

```python
def test_create_inventory_with_negative_quantity_should_return_400(client, admin_token):
    response = client.post(
        "/api/inventory/items",
        json={
            "name": "Brake Pad",
            "part_number": "BRK-001",
            "quantity": -1,
            "price": 100000,
            "center_id": 1
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 400
```

```python
def test_low_stock_with_invalid_center_id_should_return_400(client, admin_token):
    response = client.get(
        "/api/inventory/low-stock?center_id=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 400
```

---

## Câu 8. Kịch bản kiểm thử Postman

### 8.1 Chuẩn bị

1. Chạy backend bằng Docker Compose.
2. Đăng nhập để lấy Bearer Token.
3. Trong Postman chọn Environment của EV Service Center.
4. Gắn token vào biến `admin_token`, `staff_token` hoặc `user_token`.
5. Chạy folder Inventory Service.

### 8.2 Test thêm vật tư hợp lệ

```http
POST http://localhost/api/inventory/items
Authorization: Bearer <token>
Content-Type: application/json
```

Body:

```json
{
  "name": "Má phanh VF8",
  "part_number": "BRK-VF8-TEST",
  "quantity": 10,
  "min_quantity": 2,
  "price": 2500000,
  "center_id": 1
}
```

Expected:

```text
201 Created
```

### 8.3 Test quantity âm

```json
{
  "name": "Má phanh VF8",
  "part_number": "BRK-VF8-NEG",
  "quantity": -1,
  "price": 2500000,
  "center_id": 1
}
```

Expected:

```text
400 Bad Request
```

### 8.4 Test price bằng 0

```json
{
  "name": "Má phanh VF8",
  "part_number": "BRK-VF8-ZERO",
  "quantity": 10,
  "price": 0,
  "center_id": 1
}
```

Expected:

```text
400 Bad Request
```

### 8.5 Test update body rỗng

```http
PUT http://localhost/api/inventory/items/1
Authorization: Bearer <token>
Content-Type: application/json
```

Body:

```json
{}
```

Expected:

```text
400 Bad Request
```

### 8.6 Test low-stock center_id = 0

```http
GET http://localhost/api/inventory/low-stock?center_id=0
Authorization: Bearer <token>
```

Expected:

```text
400 Bad Request
```

---

# PHẦN B. KẾT QUẢ KIỂM THỬ

## 1. Tổng hợp kết quả

| Nhóm chức năng | Tổng test | Pass | Fail trước sửa | Fixed |
| -------------- | --------- | ---- | -------------- | ----- |
| Authentication | 5 | 5 | 5 | 5 |
| Add Inventory | 5 | 5 | 3 | 3 |
| Update Inventory | 5 | 5 | 4 | 4 |
| Delete Inventory | 1 | 1 | 1 | 1 |
| Low Stock | 2 | 2 | 2 | 2 |

## 2. Danh sách test case đã fix

| Mã test case | Lỗi | Commit |
| ------------ | --- | ------ |
| EP-INV-GET-02 | Không token vẫn truy cập được | Add JWT authentication for Inventory API endpoints |
| EP-INV-ADD-05 | Không token vẫn thêm được vật tư | Add JWT authentication for Inventory API endpoints |
| EP-INV-UPD-03 | Không token vẫn update được vật tư | Add JWT authentication for Inventory API endpoints |
| EP-INV-DEL-01 | Không token vẫn xóa được vật tư | Add JWT authentication for Inventory API endpoints |
| BVA-INV-ADD-01 | Cho phép quantity âm | Validate inventory create request data |
| BVA-INV-ADD-04 | Cho phép price âm | Validate inventory create request data |
| BVA-INV-ADD-05 | Cho phép price bằng 0 | Validate inventory create request data |
| EP-INV-UPD-01 | Update hợp lệ xử lý chưa ổn định | Validate inventory update request data |
| EP-INV-UPD-02 | Body rỗng không trả 400 | Validate inventory update request data |
| BVA-INV-UPD-04 | Quantity = 0 không xử lý đúng | Validate inventory update request data |
| BVA-INV-UPD-05 | Quantity = 1 không xử lý đúng | Validate inventory update request data |
| EP-INV-LOW-01 | Low-stock chưa hoạt động đúng với token | Improve low stock API validation |
| BVA-INV-LOW-01 | center_id = 0 không trả 400 | Improve low stock API validation |

## 3. GitHub Actions

Dự án có workflow:

```text
Postman API Tests with Jira Bugs
```

Luồng hoạt động:

```text
Push code
↓
GitHub Actions chạy Docker Compose
↓
Newman chạy Postman Collection
↓
Nếu testcase fail thì tạo Jira Issue loại Bug
↓
Jira Automation chuyển Bug sang cột BUG
```

## 4. Jira Integration

Các testcase trong Postman được đồng bộ sang Jira bằng workflow:

```text
Postman to Jira Sync
```

Mỗi testcase được tạo thành một task:

```text
[POSTMAN TESTCASE] EP-INV-GET-02 Không token
[POSTMAN TESTCASE] BVA-INV-ADD-01 Quantity = -1
[POSTMAN TESTCASE] BVA-INV-LOW-01 Center ID = 0
```

Khi chạy kiểm thử tự động, nếu testcase fail, GitHub Actions tự tạo issue:

```text
[API BUG] BVA-INV-ADD-01 Quantity = -1
```

và Jira Automation chuyển issue này sang trạng thái:

```text
BUG
```

---

# PHẦN C. KẾT LUẬN

Qua bài kiểm thử Inventory Service, em đã áp dụng được các kỹ thuật kiểm thử:

* Phân hoạch lớp tương đương.
* Phân tích giá trị biên.
* Kiểm thử API bằng Postman.
* Kiểm thử negative case.
* Tích hợp GitHub Actions để chạy Postman Collection tự động.
* Tích hợp Jira để quản lý testcase và bug.

Kết quả kiểm thử phát hiện các nhóm lỗi chính:

1. API Inventory chưa kiểm tra token đầy đủ.
2. API thêm vật tư chưa validate `quantity < 0`.
3. API thêm vật tư chưa validate `price <= 0`.
4. API cập nhật chưa xử lý body rỗng.
5. API cập nhật cần cho phép `quantity = 0` và `quantity = 1`.
6. API low-stock chưa validate `center_id = 0`.

Các lỗi này đã được chia thành nhiều commit rõ ràng:

```text
Add JWT authentication for Inventory API endpoints
Validate inventory create request data
Validate inventory update request data
Improve low stock API validation
```

Sau khi sửa, cần chạy lại Postman Collection và GitHub Actions để xác nhận các testcase đã chuyển từ Fail sang Pass. Những testcase pass sẽ được đồng bộ trạng thái sang Jira, còn testcase fail sẽ tự động tạo Bug để nhóm tiếp tục xử lý.
