import requests
from unittest.mock import patch, MagicMock

from services.report_service import ReportService


# ==========================================================
# TC01 - _call_internal_api thành công (HTTP 200)
# ==========================================================
@patch("services.report_service.requests.request")
def test_call_internal_api_success(mock_request, app_context):

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "success"}

    mock_request.return_value = mock_response

    data, error = ReportService._call_internal_api(
        "http://service",
        "/test"
    )

    assert error is None
    assert data == {"message": "success"}


# ==========================================================
# TC02 - _call_internal_api thành công (HTTP 201)
# ==========================================================
@patch("services.report_service.requests.request")
def test_call_internal_api_created(mock_request, app_context):

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"created": True}

    mock_request.return_value = mock_response

    data, error = ReportService._call_internal_api(
        "http://service",
        "/test"
    )

    assert error is None
    assert data["created"] is True


# ==========================================================
# TC03 - Service trả về lỗi HTTP 404
# ==========================================================
@patch("services.report_service.requests.request")
def test_call_internal_api_http_error(mock_request, app_context):

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {
        "error": "Not Found"
    }

    mock_request.return_value = mock_response

    data, error = ReportService._call_internal_api(
        "http://service",
        "/test"
    )

    assert data is None
    assert error == "Not Found"


# ==========================================================
# TC04 - Thiếu Service URL
# ==========================================================
def test_call_internal_api_missing_service_url(app_context):

    data, error = ReportService._call_internal_api(
        None,
        "/test"
    )

    assert data is None
    assert error == "Lỗi cấu hình Service URL hoặc Internal Token"


# ==========================================================
# TC05 - Thiếu Internal Token
# ==========================================================
def test_call_internal_api_missing_token(app_context):

    from flask import current_app

    current_app.config["INTERNAL_SERVICE_TOKEN"] = None

    data, error = ReportService._call_internal_api(
        "http://service",
        "/test"
    )

    assert data is None
    assert error == "Lỗi cấu hình Service URL hoặc Internal Token"


# ==========================================================
# TC06 - RequestException
# ==========================================================
@patch("services.report_service.requests.request")
def test_call_internal_api_request_exception(mock_request, app_context):

    mock_request.side_effect = requests.exceptions.RequestException(
        "Connection Error"
    )

    data, error = ReportService._call_internal_api(
        "http://service",
        "/test"
    )

    assert data is None
    assert "Lỗi kết nối Service" in error
# ==========================================================
# TC07 - get_revenue_report: Internal API trả lỗi
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_revenue_report_api_error(mock_call, app_context):

    mock_call.return_value = (None, "API Error")

    report, error = ReportService.get_revenue_report()

    assert report is None
    assert error == "API Error"


# ==========================================================
# TC08 - get_revenue_report: Không có giao dịch thành công
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_revenue_report_empty(mock_call, app_context):

    mock_call.return_value = ([
        {
            "status": "failed",
            "amount": 100,
            "method": "cash",
            "created_at": "2025-01-01T10:00:00"
        }
    ], None)

    report, error = ReportService.get_revenue_report()

    assert error is None
    assert report["total_revenue"] == 0
    assert report["transaction_count"] == 0
    assert report["avg_transaction_value"] == 0
    assert report["payment_methods"] == {}


# ==========================================================
# TC09 - get_revenue_report: Có giao dịch thành công
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_revenue_report_success(mock_call, app_context):

    mock_call.return_value = ([
        {
            "status": "success",
            "amount": 100,
            "method": "cash",
            "created_at": "2025-01-01T10:00:00"
        },
        {
            "status": "success",
            "amount": 200,
            "method": "card",
            "created_at": "2025-01-02T10:00:00"
        }
    ], None)

    report, error = ReportService.get_revenue_report()

    assert error is None
    assert report["total_revenue"] == 300
    assert report["transaction_count"] == 2
    assert report["avg_transaction_value"] == 150


# ==========================================================
# TC10 - get_revenue_report: Lọc theo khoảng thời gian
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_revenue_report_filter_date(mock_call, app_context):

    mock_call.return_value = ([
        {
            "status": "success",
            "amount": 100,
            "method": "cash",
            "created_at": "2025-01-01T10:00:00"
        },
        {
            "status": "success",
            "amount": 500,
            "method": "card",
            "created_at": "2025-02-01T10:00:00"
        }
    ], None)

    report, error = ReportService.get_revenue_report(
        "2025-01-01",
        "2025-01-31"
    )

    assert error is None
    assert report["transaction_count"] == 1
    assert report["total_revenue"] == 100


# ==========================================================
# TC11 - get_revenue_report: Thống kê payment method
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_revenue_report_payment_methods(mock_call, app_context):

    mock_call.return_value = ([
        {
            "status": "success",
            "amount": 100,
            "method": "cash",
            "created_at": "2025-01-01T10:00:00"
        },
        {
            "status": "success",
            "amount": 200,
            "method": "cash",
            "created_at": "2025-01-02T10:00:00"
        },
        {
            "status": "success",
            "amount": 300,
            "method": "card",
            "created_at": "2025-01-03T10:00:00"
        }
    ], None)

    report, error = ReportService.get_revenue_report()

    assert error is None
    assert report["payment_methods"]["cash"]["count"] == 2
    assert report["payment_methods"]["cash"]["amount"] == 300
    assert report["payment_methods"]["card"]["count"] == 1
    assert report["payment_methods"]["card"]["amount"] == 300


# ==========================================================
# TC12 - get_revenue_report: amount mặc định = 0
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_revenue_report_default_amount(mock_call, app_context):

    mock_call.return_value = ([
        {
            "status": "success",
            "method": "cash",
            "created_at": "2025-01-01T10:00:00"
        }
    ], None)

    report, error = ReportService.get_revenue_report()

    assert error is None
    assert report["total_revenue"] == 0
    assert report["transaction_count"] == 1
    assert report["avg_transaction_value"] == 0
# ==========================================================
# TC13 - get_inventory_report: Internal API trả lỗi
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_inventory_report_api_error(mock_call, app_context):

    mock_call.return_value = (None, "Inventory API Error")

    report, error = ReportService.get_inventory_report()

    assert report is None
    assert error == "Inventory API Error"


# ==========================================================
# TC14 - get_inventory_report: Kho rỗng
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_inventory_report_empty(mock_call, app_context):

    mock_call.return_value = ([], None)

    report, error = ReportService.get_inventory_report()

    assert error is None
    assert report["total_parts"] == 0
    assert report["total_quantity"] == 0
    assert report["total_inventory_value"] == 0
    assert report["low_stock_count"] == 0
    assert report["out_of_stock_count"] == 0


# ==========================================================
# TC15 - get_inventory_report: Có dữ liệu bình thường
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_inventory_report_success(mock_call, app_context):

    mock_call.return_value = ([
        {
            "name": "Oil Filter",
            "quantity": 20,
            "price": 100
        },
        {
            "name": "Brake Pad",
            "quantity": 15,
            "price": 200
        }
    ], None)

    report, error = ReportService.get_inventory_report()

    assert error is None
    assert report["total_parts"] == 2
    assert report["total_quantity"] == 35
    assert report["total_inventory_value"] == 5000
    assert report["low_stock_count"] == 0
    assert report["out_of_stock_count"] == 0


# ==========================================================
# TC16 - get_inventory_report: Low stock và Out of stock
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_inventory_report_low_stock(mock_call, app_context):

    mock_call.return_value = ([
        {
            "name": "Battery",
            "quantity": 5,
            "price": 100
        },
        {
            "name": "Spark Plug",
            "quantity": 0,
            "price": 50
        },
        {
            "name": "Engine Oil",
            "quantity": 30,
            "price": 20
        }
    ], None)

    report, error = ReportService.get_inventory_report()

    assert error is None
    assert report["low_stock_count"] == 2
    assert report["out_of_stock_count"] == 1

    assert len(report["low_stock_parts"]) == 2
    assert len(report["out_of_stock_parts"]) == 1


# ==========================================================
# TC17 - get_inventory_report: Thiếu quantity và price
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_get_inventory_report_missing_fields(mock_call, app_context):

    mock_call.return_value = ([
        {
            "name": "Unknown Part"
        }
    ], None)

    report, error = ReportService.get_inventory_report()

    assert error is None
    assert report["total_parts"] == 1
    assert report["total_quantity"] == 0
    assert report["total_inventory_value"] == 0
    assert report["low_stock_count"] == 1
    assert report["out_of_stock_count"] == 1
# ==========================================================
# TC18 - get_dashboard_overview thành công
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
@patch("services.report_service.ReportService.get_inventory_report")
@patch("services.report_service.ReportService.get_revenue_report")
def test_get_dashboard_overview_success(
    mock_revenue,
    mock_inventory,
    mock_booking,
    app_context
):

    mock_revenue.side_effect = [
        (
            {
                "total_revenue": 1000,
                "transaction_count": 2
            },
            None
        ),
        (
            {
                "total_revenue": 5000,
                "transaction_count": 10
            },
            None
        )
    ]

    mock_inventory.return_value = (
        {
            "total_parts": 20,
            "low_stock_count": 2,
            "out_of_stock_count": 1
        },
        None
    )

    mock_booking.return_value = (
        [
            {"status": "pending"},
            {"status": "confirmed"},
            {"status": "completed"},
            {"status": "completed"}
        ],
        None
    )

    dashboard, error = ReportService.get_dashboard_overview()

    assert error is None
    assert dashboard["revenue"]["today"]["total_revenue"] == 1000
    assert dashboard["revenue"]["month"]["total_revenue"] == 5000
    assert dashboard["inventory"]["total_parts"] == 20
    assert dashboard["bookings"]["total"] == 4
    assert dashboard["bookings"]["completed"] == 2


# ==========================================================
# TC19 - get_dashboard_overview không có booking
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
@patch("services.report_service.ReportService.get_inventory_report")
@patch("services.report_service.ReportService.get_revenue_report")
def test_get_dashboard_overview_no_booking(
    mock_revenue,
    mock_inventory,
    mock_booking,
    app_context
):

    mock_revenue.return_value = (
        {
            "total_revenue": 0,
            "transaction_count": 0
        },
        None
    )

    mock_inventory.return_value = (
        {
            "total_parts": 0,
            "low_stock_count": 0,
            "out_of_stock_count": 0
        },
        None
    )

    mock_booking.return_value = (None, None)

    dashboard, error = ReportService.get_dashboard_overview()

    assert error is None
    assert dashboard["bookings"]["total"] == 0
    assert dashboard["bookings"]["pending"] == 0
    assert dashboard["bookings"]["confirmed"] == 0
    assert dashboard["bookings"]["completed"] == 0


# ==========================================================
# TC20 - get_dashboard_overview revenue = None
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
@patch("services.report_service.ReportService.get_inventory_report")
@patch("services.report_service.ReportService.get_revenue_report")
def test_get_dashboard_overview_revenue_none(
    mock_revenue,
    mock_inventory,
    mock_booking,
    app_context
):

    mock_revenue.return_value = (None, "error")

    mock_inventory.return_value = (
        {
            "total_parts": 5,
            "low_stock_count": 1,
            "out_of_stock_count": 0
        },
        None
    )

    mock_booking.return_value = ([], None)

    dashboard, error = ReportService.get_dashboard_overview()

    assert error is None
    assert dashboard["revenue"]["today"]["total_revenue"] == 0
    assert dashboard["revenue"]["month"]["total_revenue"] == 0


# ==========================================================
# TC21 - get_dashboard_overview inventory = None
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
@patch("services.report_service.ReportService.get_inventory_report")
@patch("services.report_service.ReportService.get_revenue_report")
def test_get_dashboard_overview_inventory_none(
    mock_revenue,
    mock_inventory,
    mock_booking,
    app_context
):

    mock_revenue.return_value = (
        {
            "total_revenue": 100,
            "transaction_count": 1
        },
        None
    )

    mock_inventory.return_value = (None, "error")

    mock_booking.return_value = ([], None)

    dashboard, error = ReportService.get_dashboard_overview()

    assert error is None
    assert dashboard["inventory"]["total_parts"] == 0
    assert dashboard["inventory"]["low_stock_count"] == 0
    assert dashboard["inventory"]["out_of_stock_count"] == 0


# ==========================================================
# TC22 - get_dashboard_overview booking nhiều trạng thái
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
@patch("services.report_service.ReportService.get_inventory_report")
@patch("services.report_service.ReportService.get_revenue_report")
def test_get_dashboard_overview_booking_statistics(
    mock_revenue,
    mock_inventory,
    mock_booking,
    app_context
):

    mock_revenue.return_value = (
        {
            "total_revenue": 100,
            "transaction_count": 1
        },
        None
    )

    mock_inventory.return_value = (
        {
            "total_parts": 1,
            "low_stock_count": 0,
            "out_of_stock_count": 0
        },
        None
    )

    mock_booking.return_value = (
        [
            {"status": "pending"},
            {"status": "pending"},
            {"status": "confirmed"},
            {"status": "completed"},
            {"status": "completed"},
            {"status": "completed"}
        ],
        None
    )

    dashboard, error = ReportService.get_dashboard_overview()

    assert error is None
    assert dashboard["bookings"]["total"] == 6
    assert dashboard["bookings"]["pending"] == 2
    assert dashboard["bookings"]["confirmed"] == 1
    assert dashboard["bookings"]["completed"] == 3