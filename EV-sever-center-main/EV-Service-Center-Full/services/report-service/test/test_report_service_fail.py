from unittest.mock import patch

from services.report_service import ReportService


# ==========================================================
# TC_FAIL_01 - Demo FAIL Revenue Report
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_demo_fail_total_revenue(mock_call, app_context):

    mock_call.return_value = (
        [
            {
                "status": "success",
                "amount": 100,
                "method": "cash",
                "created_at": "2025-01-01T10:00:00"
            }
        ],
        None
    )

    report, error = ReportService.get_revenue_report()

    assert error is None

    # Cố tình sai để demo FAIL
    assert report["total_revenue"] == 200


# ==========================================================
# TC_FAIL_02 - Demo FAIL Inventory Report
# ==========================================================
@patch("services.report_service.ReportService._call_internal_api")
def test_demo_fail_inventory(mock_call, app_context):

    mock_call.return_value = (
        [
            {
                "quantity": 5,
                "price": 100
            }
        ],
        None
    )

    report, error = ReportService.get_inventory_report()

    assert error is None

    # Cố tình sai để demo FAIL
    assert report["total_parts"] == 5