# File: services/payment-service/run_tests.py

import sys
import os
import pytest

if __name__ == "__main__":
    # Đảm bảo đường dẫn tuyệt đối cho các tệp test
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Định nghĩa các tham số chạy pytest tích hợp báo cáo độ bao phủ (Coverage)
    args = [
        os.path.join(current_dir, "tests", "test_payment_service.py"),
        os.path.join(current_dir, "tests", "test_payment_controller.py"),
        "-v",
        f"--cov={os.path.join(current_dir, 'services')}",
        f"--cov={os.path.join(current_dir, 'controllers')}",
        f"--cov={os.path.join(current_dir, 'models')}",
        "--cov-report=term-missing",
    ]
    
    print("\n" + "="*70)
    print("=== AUTOMATIC TEST RUNNER & CODE COVERAGE REPORT ===")
    print("="*70 + "\n")
    
    # Thực thi pytest
    exit_code = pytest.main(args)
    
    # Trả về exit code cho hệ thống CI/CD (0 nếu thành công, 1 nếu thất bại)
    sys.exit(exit_code)
