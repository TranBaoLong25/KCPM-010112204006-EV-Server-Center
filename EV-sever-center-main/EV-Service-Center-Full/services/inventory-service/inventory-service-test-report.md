# BÁO CÁO KIỂM THỬ INVENTORY SERVICE

## Dự án: EV Service Center Maintenance Management System

---

# 1. Giới thiệu

## 1.1 Mục tiêu

Kiểm thử Inventory Service nhằm đảm bảo các chức năng quản lý vật tư hoạt động đúng yêu cầu, bao gồm:

- Thêm vật tư mới
- Xem danh sách vật tư
- Xem chi tiết vật tư
- Cập nhật thông tin vật tư
- Xóa vật tư
- Kiểm tra vật tư trùng mã
- Kiểm tra vật tư tương thích với dòng xe
- Kiểm tra tồn kho thấp

---

## 1.2 Phạm vi kiểm thử

Các chức năng được kiểm thử:

- Quản lý danh sách vật tư
- Quản lý số lượng tồn kho
- Quản lý giá vật tư
- Quản lý mã vật tư `part_number`
- Quản lý vật tư theo trung tâm `center_id`
- Quản lý thông tin tương thích `compatible_models`

---

# 2. Môi trường kiểm thử

| Thành phần       | Công nghệ                           |
| ---------------- | ----------------------------------- |
| Backend          | Python Flask                        |
| Database         | PostgreSQL / SQLite memory khi test |
| API Testing      | Postman                             |
| Unit Testing     | pytest                              |
| Coverage         | pytest-cov                          |
| Frontend Testing | Playwright                          |
| CI/CD            | GitHub Actions                      |
| Version Control  | Git + GitHub                        |

---

# 3. Danh sách API kiểm thử

| STT    | API                       | Method | Mô tả                   |
| ------ | ------------------------- | ------ | ----------------------- |
| INV-01 | /api/inventory/items      | GET    | Lấy danh sách vật tư    |
| INV-02 | /api/inventory/items      | POST   | Thêm vật tư             |
| INV-03 | /api/inventory/items/{id} | GET    | Lấy chi tiết vật tư     |
| INV-04 | /api/inventory/items/{id} | PUT    | Cập nhật vật tư         |
| INV-05 | /api/inventory/items/{id} | DELETE | Xóa vật tư              |
| INV-06 | /api/inventory/low-stock  | GET    | Xem vật tư tồn kho thấp |

---

# 4. Black-box Testing

## 4.1 Phân hoạch lớp tương đương

### Part Number

Lớp hợp lệ:

- `part_number` không rỗng
- `part_number` chưa tồn tại trong cùng `center_id`

Lớp không hợp lệ:

- `part_number` rỗng
- `part_number` đã tồn tại trong cùng `center_id`

---

### Quantity

Lớp hợp lệ:

- `quantity >= 0`

Lớp không hợp lệ:

- `quantity < 0`
- Thiếu trường `quantity`

---

### Price

Lớp hợp lệ:

- `price > 0`

Lớp không hợp lệ:

- `price = 0`
- `price < 0`
- Thiếu trường `price`

---

### Center ID

Lớp hợp lệ:

- `center_id` tồn tại
- `center_id` là số nguyên

Lớp không hợp lệ:

- `center_id` rỗng
- `center_id` sai kiểu dữ liệu

---

# 4.2 Boundary Value Analysis

## Quantity

| Test Case  | Input         | Ý nghĩa        | Expected     |
| ---------- | ------------- | -------------- | ------------ |
| BVA-INV-01 | quantity = -1 | Dưới biên      | 400          |
| BVA-INV-02 | quantity = 0  | Đúng biên dưới | 201 hoặc 200 |
| BVA-INV-03 | quantity = 1  | Trên biên      | 201 hoặc 200 |

---

## Min Quantity

| Test Case  | Input             | Ý nghĩa   | Expected     |
| ---------- | ----------------- | --------- | ------------ |
| BVA-INV-04 | min_quantity = -1 | Dưới biên | 400          |
| BVA-INV-05 | min_quantity = 0  | Đúng biên | 201 hoặc 200 |
| BVA-INV-06 | min_quantity = 1  | Trên biên | 201 hoặc 200 |

---

## Price

| Test Case  | Input      | Ý nghĩa                 | Expected     |
| ---------- | ---------- | ----------------------- | ------------ |
| BVA-INV-07 | price = -1 | Dưới biên               | 400          |
| BVA-INV-08 | price = 0  | Biên không hợp lệ       | 400          |
| BVA-INV-09 | price = 1  | Giá trị hợp lệ nhỏ nhất | 201 hoặc 200 |

---

## Item ID

| Test Case  | Input      | Ý nghĩa             | Expected        |
| ---------- | ---------- | ------------------- | --------------- |
| BVA-INV-10 | id = 0     | Dưới biên ID hợp lệ | 400 hoặc 404    |
| BVA-INV-11 | id = 1     | ID nhỏ nhất hợp lệ  | 200 nếu tồn tại |
| BVA-INV-12 | id = 99999 | ID không tồn tại    | 404             |

---

# 5. Thiết kế Test Case

| Test Case | Chức năng                                 | Dữ liệu kiểm thử                 | Expected                     |
| --------- | ----------------------------------------- | -------------------------------- | ---------------------------- |
| TC-INV-01 | Thêm vật tư hợp lệ                        | part_number mới, quantity hợp lệ | Tạo thành công               |
| TC-INV-02 | Thêm vật tư trùng part_number cùng center | part_number đã tồn tại           | Báo lỗi                      |
| TC-INV-03 | Thêm vật tư cùng part_number khác center  | center_id khác nhau              | Tạo thành công               |
| TC-INV-04 | Lấy vật tư theo ID hợp lệ                 | id tồn tại                       | Trả về vật tư                |
| TC-INV-05 | Lấy vật tư không tồn tại                  | id = 99999                       | Trả về None hoặc 404         |
| TC-INV-06 | Lấy danh sách vật tư                      | center_id = 1                    | Trả về danh sách             |
| TC-INV-07 | Cập nhật vật tư hợp lệ                    | name, quantity, price mới        | Cập nhật thành công          |
| TC-INV-08 | Cập nhật vật tư không tồn tại             | id = 99999                       | Báo lỗi                      |
| TC-INV-09 | Xóa vật tư hợp lệ                         | id tồn tại                       | Xóa thành công               |
| TC-INV-10 | Xóa vật tư không tồn tại                  | id = 99999                       | Báo lỗi                      |
| TC-INV-11 | Tạo vật tư có compatibility               | compatible_models, category      | Tạo compatibility thành công |

---

# 6. White-box Testing

## 6.1 Công cụ sử dụng

- pytest
- SQLite memory database
- Flask test app
- Unit test trực tiếp tầng service

---

## 6.2 Cấu trúc thư mục test

```text
services/inventory-service/tests/
├── conftest.py
├── test_inventory_service.py
└── test_inventory_service_fail_demo.py
```

---

## 6.3 Vai trò từng file

### conftest.py

Dùng để:

- Cấu hình môi trường test
- Khởi tạo Flask app
- Tạo database tạm bằng SQLite memory
- Tạo và xóa bảng trước/sau mỗi test

---

### test_inventory_service.py

Chứa các test case PASS, kiểm tra các nhánh xử lý đúng của Inventory Service:

- Tạo vật tư thành công
- Kiểm tra trùng `part_number`
- Tạo vật tư cùng `part_number` nhưng khác `center_id`
- Lấy vật tư theo ID
- Lấy danh sách vật tư
- Cập nhật vật tư
- Xóa vật tư
- Tạo compatibility cho vật tư

---

### test_inventory_service_fail_demo.py

Chứa các test FAIL có chủ đích nhằm chứng minh pytest có thể phát hiện sai lệch giữa Expected Result và Actual Result.

Các test fail demo gồm:

- Duplicate part_number nhưng cố tình kỳ vọng tạo thành công
- Get item không tồn tại nhưng cố tình kỳ vọng có dữ liệu
- Update item không tồn tại nhưng cố tình kỳ vọng thành công
- Delete item không tồn tại nhưng cố tình kỳ vọng thành công
- Same part_number cùng center nhưng cố tình kỳ vọng không lỗi

---

## 6.4 Danh sách Unit Test chính

| Test Case                                          | Mục tiêu                                    |
| -------------------------------------------------- | ------------------------------------------- |
| test_create_item_success                           | Kiểm tra tạo vật tư thành công              |
| test_create_item_duplicate_part_number_same_center | Kiểm tra trùng part_number cùng center      |
| test_create_item_same_part_number_different_center | Kiểm tra cùng part_number nhưng khác center |
| test_get_item_by_id_success                        | Kiểm tra lấy vật tư theo ID hợp lệ          |
| test_get_item_by_id_not_found                      | Kiểm tra lấy vật tư không tồn tại           |
| test_get_all_items                                 | Kiểm tra lấy danh sách vật tư               |
| test_update_item_success                           | Kiểm tra cập nhật vật tư thành công         |
| test_update_item_not_found                         | Kiểm tra cập nhật vật tư không tồn tại      |
| test_delete_item_success                           | Kiểm tra xóa vật tư thành công              |
| test_delete_item_not_found                         | Kiểm tra xóa vật tư không tồn tại           |
| test_create_item_with_compatibility                | Kiểm tra tạo vật tư có compatibility        |

---

## 6.5 Cách chạy White-box Test

Chạy toàn bộ test:

```bash
cd services/inventory-service
pytest -v
```

Chạy riêng test PASS:

```bash
pytest -v tests/test_inventory_service.py
```

Chạy cả PASS và FAIL demo:

```bash
pytest -v
```

Kết quả dự kiến:

```text
11 passed, 5 failed
```

Trong đó:

- `passed`: test đúng với kết quả mong đợi.
- `failed`: test fail có chủ đích để chứng minh framework phát hiện sai lệch.

---

# 7. Frontend Testing

## 7.1 Công cụ

- Playwright

---

## 7.2 Kịch bản kiểm thử frontend

| Test Case | Mô tả                          |
| --------- | ------------------------------ |
| FE-INV-01 | Mở được trang danh sách vật tư |
| FE-INV-02 | Hiển thị danh sách vật tư      |
| FE-INV-03 | Thêm vật tư hợp lệ             |
| FE-INV-04 | Thêm vật tư thiếu tên          |
| FE-INV-05 | Xem cảnh báo tồn kho thấp      |

---

## 7.3 Cách chạy frontend test

```bash
cd frontend-tests
node ./node_modules/@playwright/test/cli.js test tests/inventory.spec.js
```

Xem HTML report:

```bash
node ./node_modules/@playwright/test/cli.js show-report
```

---

# 8. Coverage Testing

## 8.1 Công cụ

- pytest-cov

---

## 8.2 Lệnh thực hiện

```bash
pytest --cov=. --cov-report=html
```

---

## 8.3 Kết quả

Sau khi chạy lệnh trên, hệ thống sinh:

- File `.coverage`
- Thư mục `htmlcov`
- Báo cáo HTML hiển thị tỷ lệ bao phủ mã nguồn

---

## 8.4 Ý nghĩa

Coverage cho biết bộ test đã chạy qua bao nhiêu phần trăm mã nguồn.

Coverage không phải số lượng lỗi.  
Coverage cao hơn nghĩa là test đã thực thi được nhiều dòng code hơn.

---

# 9. CI/CD

## 9.1 Công cụ

- GitHub Actions
- Docker

---

## 9.2 Workflow

```text
Push code
↓
GitHub Actions
↓
Install dependencies
↓
Run pytest
↓
Run coverage
↓
Build Docker image
↓
Success hoặc Failed
```

---

## 9.3 File workflow

```text
.github/workflows/inventory-service-ci-cd.yml
```

---

## 9.4 Ý nghĩa

CI/CD giúp tự động kiểm thử Inventory Service mỗi khi có thay đổi mã nguồn. Nếu test fail, workflow sẽ báo lỗi và quá trình build sẽ dừng. Nếu test pass, Docker image của Inventory Service sẽ được build thành công.

---

# 10. Kết luận

Inventory Service đã được kiểm thử bằng nhiều kỹ thuật khác nhau:

- Black-box Testing
- Equivalence Partitioning
- Boundary Value Analysis
- White-box Testing bằng pytest
- Frontend Testing bằng Playwright
- Coverage Testing bằng pytest-cov
- CI/CD bằng GitHub Actions
