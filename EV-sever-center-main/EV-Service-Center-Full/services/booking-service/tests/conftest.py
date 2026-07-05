import os
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
# Use a longer test secret to avoid InsecureKeyLengthWarning and ensure HMAC decoding
os.environ["JWT_SECRET_KEY"] = "test-secret-with-length-at-least-32-chars-123"
os.environ["INTERNAL_SERVICE_TOKEN"] = "test-internal-token"
os.environ["USER_SERVICE_URL"] = "http://localhost"
os.environ["NOTIFICATION_SERVICE_URL"] = "http://localhost"

from app import create_app, db


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret-with-length-at-least-32-chars-123"
    app.config["INTERNAL_SERVICE_TOKEN"] = "test-internal-token"
    app.config["USER_SERVICE_URL"] = "http://localhost"

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user_token(app):
    from flask_jwt_extended import create_access_token
    with app.app_context():
        return create_access_token(identity=1, additional_claims={"role": "user"})


@pytest.fixture
def admin_token(app):
    from flask_jwt_extended import create_access_token
    with app.app_context():
        return create_access_token(identity=1, additional_claims={"role": "admin"})


# Autouse fixture to bypass JWT verification during route tests.
# This patches verify_jwt_in_request to a no-op and provides simple
# `get_jwt_identity` and `get_jwt` implementations so routes relying
# on them work in tests without full JWT decoding.
@pytest.fixture(autouse=True)
def bypass_jwt(monkeypatch):
    # Patch both the flask_jwt_extended internals and the names imported
    # directly into our controller module so routes see the patched values.
    import flask_jwt_extended.view_decorators as jwt_view
    import flask_jwt_extended.utils as jwt_utils
    import controllers.booking_controller as booking_ctrl

    monkeypatch.setattr(jwt_view, "verify_jwt_in_request", lambda *a, **kw: None)
    monkeypatch.setattr(jwt_utils, "get_jwt_identity", lambda: 1)
    monkeypatch.setattr(jwt_utils, "get_jwt", lambda: {"role": "admin"})

    # Also patch the symbols imported into the controller module
    monkeypatch.setattr(booking_ctrl, "verify_jwt_in_request", lambda *a, **kw: None)
    monkeypatch.setattr(booking_ctrl, "get_jwt_identity", lambda: 1)
    monkeypatch.setattr(booking_ctrl, "get_jwt", lambda: {"role": "admin"})
    yield


# Collect test outcomes and write a report when the session finishes.
_passed_tests = []
_failed_tests = []
_skipped_tests = []


def pytest_runtest_logreport(report):
    try:
        if report.when != "call":
            return

        if report.passed:
            _passed_tests.append(report.nodeid)
        elif report.failed:
            _failed_tests.append(report.nodeid)
        elif report.skipped:
            _skipped_tests.append(report.nodeid)
    except Exception:
        pass


def pytest_sessionfinish(session, exitstatus):
    try:
        import os
        import datetime

        out_dir = os.path.join(os.getcwd(), "test_results")
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        out_file = os.path.join(out_dir, f"pytest_report_{ts}.md")

        with open(out_file, "w", encoding="utf-8") as f:
            f.write("# Pytest Test Report\n\n")
            f.write(f"Timestamp (UTC): {ts}\n\n")
            try:
                total = len(session.items)
            except Exception:
                total = "unknown"
            f.write(f"Total collected tests: {total}\n")
            f.write(f"Passed: {len(_passed_tests)}\n")
            f.write(f"Failed: {len(_failed_tests)}\n")
            f.write(f"Skipped: {len(_skipped_tests)}\n")
            f.write(f"Exit status: {exitstatus}\n\n")

            f.write("## Passed Tests\n\n")
            for nodeid in _passed_tests:
                f.write(f"- {nodeid}\n")

            f.write("\n## Failed Tests\n\n")
            for nodeid in _failed_tests:
                f.write(f"- {nodeid}\n")

            f.write("\n## Skipped Tests\n\n")
            for nodeid in _skipped_tests:
                f.write(f"- {nodeid}\n")

        print(f"Saved pytest report: {out_file}")
    except Exception as e:
        print(f"Failed to write pytest report: {e}")
