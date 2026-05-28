# 🛠️ Dự Án Hệ Thống Quản Lý & Bảo Trì Xe Điện (EV Service Center Management Platform)

## 📖 1. Giới Thiệu Dự Án & Mục Tiêu Kiểm Chứng
Dự án **EV-Server-Center** là một hệ thống quản lý chuỗi trung tâm dịch vụ, điều phối bảo dưỡng, sửa chữa và thay thế vật tư/pin cho các dòng xe điện toàn diện. Hệ thống được phát triển theo kiến trúc **Microservices** hiện đại, phân tách độc lập các nghiệp vụ lõi để tối ưu khả năng mở rộng, phân tải và nâng cao độ ổn định cao.

Vì đây là đồ án thực hành thuộc môn **Kiểm chứng phần mềm (KCPM)**, mục tiêu cốt lõi của dự án là áp dụng các kỹ nghệ test nâng cao: xây dựng bộ kịch bản **Kiểm thử tự động (Automation Testing)**, thiết lập quy trình **CI/CD** kiểm thử ngầm, tích hợp công cụ giám sát chất lượng và tự động hóa quy trình báo lỗi **(Jira Automation via Webhooks)** nhằm phát hiện bug sớm, quản lý tiến độ phân việc chặt chẽ và đảm bảo tính toàn vẹn dữ liệu giữa các dịch vụ độc lập.

---

## 👥 2. Phân Quyền Người Dùng & Luồng Nghiệp Vụ Chính (Actors & Use Cases)

Hệ thống phân quyền nghiêm ngặt thành 3 nhóm đối tượng truy cập (Actors) tương ứng với các luồng chức năng:

### A. Khách hàng (Customer / User)
* **Quản lý tài khoản:** Đăng ký, đăng nhập hệ thống bảo mật bằng token (JWT), cập nhật hồ sơ cá nhân và yêu cầu khôi phục mật khẩu thông qua mã OTP gửi về Mail.
* **Đặt lịch hẹn:** Tra cứu danh sách các trung tâm dịch vụ (Centers) còn trống ca, chọn thời gian, khai báo thông tin xe (Model xe, số khung/số VIN) và gửi yêu cầu đặt lịch hẹn.
* **Theo dõi tiến độ:** Xem danh sách lịch hẹn cá nhân, thực hiện hủy lịch hẹn từ xa, và theo dõi thời gian thực trạng thái xe đang được xử lý tại xưởng.
* **Thanh toán & Hóa đơn:** Tiếp nhận hóa đơn điện tử được xuất tự động, thực hiện thanh toán trực tuyến qua cổng giao dịch (QR MoMo/Chuyển khoản Bank) và tra cứu lịch sử giao dịch.
* **Hỗ trợ trực tuyến:** Kết nối vào phòng chat thời gian thực để trao đổi trực tiếp với nhân viên điều phối về tình trạng lỗi của xe.

### B. Nhân viên & Kỹ thuật viên (Staff & Technician)
* **Nhân viên điều phối (Staff):** Tiếp nhận danh sách lịch hẹn của khách hàng, kiểm tra tính hợp lệ, phê duyệt xác nhận lịch hẹn và phân phối ca trực, điều phối công việc cho kỹ thuật viên phù hợp.
* **Kỹ thuật viên sửa chữa (Technician):** Tiếp nhận xe tại xưởng, lập phiếu bảo trì (Maintenance Ticket), cập nhật trạng thái sửa chữa theo checklist công việc (Đang xử lý, Hoàn thành) và tạo lệnh xuất linh kiện, phụ tùng thay thế từ kho vật tư.
* **Kế toán / Thu ngân:** Kiểm tra phiếu nghiệm thu kỹ thuật của KTV, hệ thống tự động tính toán tổng chi phí (tiền công + tiền linh kiện phụ tùng) để xuất hóa đơn (Invoice) gửi cho khách hàng, kiểm tra trạng thái khớp toán.

### C. Quản trị viên (Admin)
* **Quản trị hệ thống:** Toàn quyền kiểm soát danh sách tài khoản, phê duyệt cấp quyền nội bộ (Staff/Technician/Admin) hoặc thực hiện khóa/mở khóa các tài khoản vi phạm.
* **Quản lý Kho (Inventory):** Nhập thêm thiết bị, xe điện, linh kiện mới vào kho; điều chỉnh số lượng vật tư và thiết lập định mức cảnh báo tồn kho tối thiểu (Low Stock Warning).
* **Báo cáo & Thống kê:** Quét dữ liệu liên dịch vụ để hiển thị dashboard thống kê tổng doanh thu, số lượng lịch hẹn theo tháng, hiệu suất làm việc của nhân viên và tỷ lệ hao hụt linh kiện vật tư.

---

## 🏗️ 3. Danh Mục Microservices & Kịch Bản API Cần Kiểm Thử (What to Test?)

Toàn bộ các API Public (`/api/...`) đều được định tuyến tập trung qua cổng Nginx API Gateway ở cổng 80. Dưới đây là danh sách đầy đủ tất cả các API thuộc 8 dịch vụ thành phần và các ca kiểm thử bắt buộc phải thực hiện kiểm chứng trên Postman:

### 🔑 3.1. User Service (Cổng 5000 / API Xác thực & Hồ sơ tài khoản)
* **Chức năng chính:** Quản lý đăng ký, cấp phát mã token JWT khi đăng nhập, mã hóa mật khẩu, quản lý phân quyền và thông tin hồ sơ tài khoản.
* **Các kịch bản cần kiểm thử (Test Cases):**
    * `POST /api/register`: Kiểm thử tạo tài khoản mới thành công (Mã trả về 201 Created); Kiểm thử chặn trùng lặp email hoặc thiếu trường bắt buộc.
    * `POST /api/login`: Kiểm thử đăng nhập thông tin hợp lệ (Trả về mã 200 OK và chuỗi `access_token`); Kiểm thử chặn truy cập khi nhập sai mật khẩu hoặc tài khoản bị khóa.
    * `POST /api/send-otp`: Kiểm thử gọi dịch vụ sinh mã OTP khôi phục tài khoản và gửi yêu cầu sang dịch vụ thông báo.
    * `GET /api/profile`: Kiểm thử lấy thông tin hồ sơ cá nhân (Yêu cầu truyền Bearer Token hợp lệ); Kiểm thử chặn quyền truy cập trái phép (Lỗi 401 Unauthorized).
    * `PUT /api/profile`: Kiểm thử cập nhật thông tin cá nhân (Họ tên, Số điện thoại) của tài khoản.
    * `GET /api/admin/users`: [Admin Quyền] Kiểm thử lấy toàn bộ danh sách tài khoản trong hệ thống để quản trị.
    * `PUT /api/admin/users/<id>/status`: [Admin Quyền] Kiểm thử lệnh khóa hoặc mở khóa một tài khoản người dùng cụ thể.

### 📅 3.2. Booking Service (Cổng 8001 / API Quản lý Đặt lịch hẹn)
* **Chức năng chính:** Điều phối luồng đặt chỗ, thiết lập lịch hẹn sửa chữa, chọn trung tâm (Center) và xử lý cập nhật trạng thái vòng đời lịch hẹn.
* **Các kịch bản cần kiểm thử (Test Cases):**
    * `POST /api/bookings`: Kiểm thử đặt lịch hẹn sửa chữa xe điện mới (Yêu cầu điền: Tên khách hàng, Số điện thoại, Model xe, Số VIN, loại dịch vụ, ngày giờ hẹn).
    * `GET /api/bookings`: Kiểm thử lấy danh sách toàn bộ lịch hẹn cá nhân của khách hàng đang đăng nhập.
    * `GET /api/bookings/<id>`: Kiểm thử lấy thông tin chi tiết của một lịch hẹn cụ thể theo ID để kiểm tra dữ liệu dòng xe và ghi chú lỗi.
    * `PUT /api/bookings/<id>/cancel`: Kiểm thử khách hàng thực hiện yêu cầu hủy lịch hẹn đã đặt.
    * `GET /api/admin/bookings`: [Staff Quyền] Kiểm thử nhân viên lấy toàn bộ danh sách lịch hẹn trên toàn hệ thống kèm bộ lọc trạng thái (`pending`, `confirmed`, `completed`, `cancelled`).
    * `PUT /api/admin/bookings/<id>/status`: [Staff Quyền] Kiểm thử tiếp nhận, phê duyệt xác nhận lịch hẹn và phân công mã ID của Kỹ thuật viên phụ trách xử lý xe thực tế.

### ⚙️ 3.3. Maintenance Service (Cổng 8003 / API Bảo trì & Sửa chữa)
* **Chức năng chính:** Số hóa quy trình sửa chữa thực tế tại xưởng, quản lý phiếu kỹ thuật, lập checklist lỗi và ghi nhận vật tư tiêu hao.
* **Các kịch bản cần kiểm thử (Test Cases):**
    * `POST /api/maintenance/tickets`: Kiểm thử Kỹ thuật viên khởi tạo một phiếu bảo trì/sửa chữa xe mới dựa trên mã lịch hẹn (`booking_id`) hợp lệ.
    * `GET /api/maintenance/tickets`: Kiểm thử lấy danh sách toàn bộ các phiếu bảo trì đang được xử lý tại xưởng sửa chữa.
    * `GET /api/maintenance/tickets/<id>`: Kiểm thử xem chi tiết tiến độ sửa chữa, thông tin KTV phụ trách và mô tả tình trạng hỏng hóc cụ thể của một chiếc xe.
    * `PUT /api/maintenance/tickets/<id>/status`: [Technician Quyền] Kiểm thử cập nhật trạng thái tiến độ sửa xe (`pending` -> `in_progress` -> `completed`).
    * `POST /api/maintenance/tickets/<id>/parts`: Kiểm thử KTV cập nhật danh sách các mã linh kiện phụ tùng và số lượng cụ thể đã thay thế cho xe vào phiếu bảo trì để đồng bộ dữ liệu tính tiền.
    * `DELETE /api/maintenance/tickets/<id>`: Kiểm thử xóa hoặc hủy bỏ một phiếu sửa chữa lập lỗi ra khỏi hệ thống.

### 📦 3.4. Inventory Service (Cổng 8000 / API Quản lý Kho xe & Phụ tùng)
* **Chức năng chính:** Kiểm soát số lượng hàng tồn kho vật tư, linh kiện thiết bị, xe điện, pin thay thế và xử lý các lệnh xuất/nhập kho.
* **Các kịch bản cần kiểm thử (Test Cases):**
    * `GET /api/inventory/inventory`: Kiểm thử lấy danh sách và số lượng tồn kho của toàn bộ thiết bị, phụ tùng, pin trong kho vật tư.
    * `GET /api/inventory/inventory/<id>`: Kiểm thử lấy thông tin chi tiết, đơn giá và xuất xứ của một mặt hàng linh kiện cụ thể theo mã ID.
    * `POST /api/inventory/inventory`: [Admin Quyền] Kiểm thử thêm mới một loại thiết bị hoặc vật tư phụ tùng vào kho (Tên phụ tùng, mã part_number, số lượng ban đầu, đơn giá).
    * `PUT /api/inventory/inventory/<id>`: Kiểm thử cập nhật thông số vật tư hoặc điều chỉnh giảm số lượng tồn kho khi có lệnh lấy đồ đi thay thế sửa chữa.
    * `DELETE /api/inventory/inventory/<id>`: [Admin Quyền] Kiểm thử loại bỏ một mặt hàng hoặc thiết bị cũ lỗi mốt ra khỏi danh mục quản lý kho.
    * `GET /api/inventory/low-stock`: Kiểm thử API quét danh sách các linh kiện phụ tùng có số lượng tồn kho giảm xuống dưới mức tối thiểu định sẵn để đưa ra cảnh báo nhập hàng gấp.

### 💳 3.5. Finance & Payment Service (Cổng 8002 & 8004 / API Hóa đơn & Cổng Thanh toán)
* **Chức năng chính:** Quét phiếu sửa chữa để tự động tính tiền, xuất hóa đơn tài chính, kết nối API cổng ngân hàng/ví điện tử để xử lý luồng giao dịch trực tuyến và hoàn tiền giao dịch lỗi.
* **Các kịch bản cần kiểm thử (Test Cases):**
    * `POST /api/finance/invoices`: Kiểm thử lệnh khởi tạo hóa đơn dịch vụ mới dựa trên dữ liệu nghiệm thu từ Maintenance Service (Tự động tổng hợp tiền công + tiền linh kiện phụ tùng).
    * `GET /api/finance/invoices`: Kiểm thử khách hàng lấy danh sách toàn bộ các hóa đơn cá nhân cần phải thanh toán.
    * `GET /api/finance/invoices/<id>`: Kiểm thử lấy thông tin chi tiết một hóa đơn (Danh sách mục tính tiền, thuế suất VAT, tổng tiền, trạng thái thanh toán).
    * `POST /api/payment/charge`: Kiểm thử khởi tạo giao dịch tài chính, kết nối với bên thứ ba để sinh mã QR thanh toán tương ứng cho hóa đơn.
    * `GET /api/payment/status/<tx_id>`: Kiểm thử API tra cứu trạng thái giao dịch tiền tệ (Đang chờ, Thành công, Thất bại) dựa trên mã giao dịch.
    * `POST /api/payment/webhook`: Kiểm thử hệ thống tiếp nhận phản hồi kết quả tự động dữ liệu từ Ngân hàng truyền về để tự động cập nhật trạng thái hóa đơn sang "Paid" (Đã thanh toán).
    * `POST /api/payment/refund`: [Staff Quyền] Kiểm thử API xử lý hoàn lại tiền cho khách hàng khi giao dịch bị lỗi hệ thống hoặc hủy phiếu.

### 🔔 3.6. Notification Service (Cổng 8005 / API Quản lý Thông báo & Email)
* **Chức năng chính:** Lập lịch chạy ngầm, quản lý các mẫu HTML template để gửi email tự động xác nhận đặt lịch, gửi mã OTP hoặc gửi biên lai hóa đơn điện tử cho người dùng.
* **Các kịch bản cần kiểm thử (Test Cases):**
    * `POST /api/notifications/send-email`: Kiểm thử gọi lệnh nội bộ gửi email xác nhận đặt lịch hẹn thành công kèm thông tin ngày giờ đến trung tâm sửa chữa.
    * `POST /api/notifications/send-otp`: Kiểm thử gọi lệnh gửi email chứa mã OTP bảo mật gồm 6 số phục vụ luồng khôi phục mật khẩu.
    * `POST /api/notifications/remind-service`: Kiểm thử chạy tiến trình gửi email tự động nhắc nhở khách hàng mang xe đi bảo dưỡng định kỳ khi đến hạn.
    * `GET /api/notifications/my-notifications`: Kiểm thử khách hàng lấy danh sách thông báo hiển thị trên ứng dụng cá nhân.
    * `PUT /api/notifications/<id>/read`: Kiểm thử cập nhật trạng thái đã đọc đối với một thông báo cụ thể.

### 📊 3.7. Report Service (Cổng 8006 / API Báo cáo & Thống kê Quản trị)
* **Chức năng chính:** Thu thập, tổng hợp dữ liệu liên dịch vụ (Cross-service data aggregation) để phục vụ xuất file báo cáo doanh thu và hiển thị Dashboard phân tích chiến lược cho Admin.
* **Các kịch bản cần kiểm thử (Test Cases):**
    * `GET /api/reports/revenue`: [Admin Quyền] Kiểm thử truy xuất dữ liệu báo cáo tổng doanh thu theo mốc thời gian tùy chọn (Theo ngày, khoảng ngày, tháng, năm) và theo từng trung tâm cụ thể.
    * `GET /api/reports/bookings`: [Admin Quyền] Kiểm thử lấy số liệu thống kê mật độ đặt lịch, tỷ lệ hủy lịch hẹn để đánh giá mức độ quá tải của các trạm sửa chữa.
    * `GET /api/reports/inventory-analytics`: [Admin Quyền] Kiểm thử lấy dữ liệu phân tích tần suất tiêu hao của từng loại linh kiện phụ tùng để tối ưu hóa dòng tiền nhập hàng kho.

### 👥 3.8. Staff Service (Cổng 8008 / API Quản lý Nhân sự & Phân ca)
* **Chức năng chính:** Quản trị hồ sơ nhân sự, phân chia ca trực nhật hệ thống (Shifts) và điều phối lệnh phân công KTV tiếp nhận sửa chữa xe (Assignments).
* **Các kịch bản cần kiểm thử (Test Cases):**
    * `GET /api/staff/members`: Kiểm thử lấy danh sách toàn bộ đội ngũ nhân sự nội bộ thuộc trung tâm dịch vụ kèm theo vai trò (Staff, Technician).
    * `POST /api/staff/shifts`: [Admin Quyền] Kiểm thử thiết lập và tạo lịch phân ca làm việc mới (Ca sáng, Ca chiều) cho nhân viên nội bộ.
    * `PUT /api/staff/assignments/<id>`: Kiểm thử điều phối viên thực hiện lệnh gán phiếu bảo trì sửa chữa cho một kỹ thuật viên cụ thể; Kiểm thử chặn gán việc nếu KTV đó đang bận xử lý xe khác hoặc đang ngoài ca trực hệ thống.

---

## 🧪 4. Mô Hình Kiểm Chứng Nâng Cao (Xương Sống Đồ Án KCPM)
Dự án áp dụng các mô hình kiểm chứng phần mềm thực tế doanh nghiệp nhằm đảm bảo chất lượng vận hành hệ thống Microservices:

1. **API Functional Testing (Postman):** Kiểm thử hộp đen toàn bộ các API endpoint, bắt buộc xây dựng kịch bản kiểm tra cho cả trường hợp dữ liệu chuẩn đầu vào (Positive) và các trường hợp dữ liệu sai/thiếu trường/sai định quyền (Negative).
2. **Jira Test Automation via Webhooks:** Tích hợp luồng phát hiện lỗi tự động. Khi thực thi kiểm thử trên Postman, nếu một kịch bản test trả về kết quả lỗi (`FAIL` - không khớp mã trạng thái mong đợi), hệ thống Script Postman sẽ lập tức kích hoạt gửi lệnh HTTP POST Webhook chứa cấu trúc JSON chuẩn hóa (`summary` và `description`) truyền thẳng sang Jira Cloud để tự động khởi tạo một thẻ lỗi (`Bug`) nằm ngoài cột TO DO giúp team 7 người lập tức phát hiện và sửa chữa code backend.
3. **Local Log Harvesting & AI Analysis (RAG/LLM Ready):** Toàn bộ dữ liệu log kiểm thử chi tiết bao gồm Request, Response status code, nội dung Body lỗi đều được trích xuất tự động và lưu trữ có cấu trúc JSON cục bộ. Nguồn dữ liệu này được thiết kế để nạp trực tiếp vào cơ sở dữ liệu Vector (RAG) giúp LLM phân tích chuyên sâu, tự động phân biệt giữa lỗi hệ thống cũ (lỗi đã biết) và lỗi phát sinh mới trong quá trình kiểm thử.

---

## 👥 5. Thành Viên Nhóm Thực Hiện & Phân Công Nhiệm Vụ
* **Trần Bảo Long** - *Trưởng nhóm phụ trách kiến trúc hệ thống, Quản trị quy trình Jira Board, Thiết lập luồng Test Automation & Cấu hình Docker Gateway.*
* *(Vui lòng điền họ tên 6 thành viên còn lại của nhóm bồ kèm các service mà các bạn phụ trách viết kịch bản test vào đây)*

---
💻 *Đồ án được thực hiện phục vụ công tác nghiên cứu, học tập và thực hành các phương pháp kiểm chứng phần mềm nâng cao.*
