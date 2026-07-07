import os
import sys
from datetime import datetime
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = BASE_DIR / "test_results"
REPORT_FILE = REPORT_DIR / "pytest_report.md"
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["INTERNAL_SERVICE_TOKEN"] = "test-internal-token"

from app import create_app, db


def pytest_configure(config):
    config._notification_report = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "tests": [],
    }
    REPORT_DIR.mkdir(exist_ok=True)


def pytest_runtest_logreport(report):
    if report.when != "call":
        return

    outcome = report.outcome
    data = getattr(report, "config", None)
    if data is None or not hasattr(data, "_notification_report"):
        return

    data = data._notification_report
    if outcome == "passed":
        data["passed"] += 1
    elif outcome == "failed":
        data["failed"] += 1
    elif outcome == "skipped":
        data["skipped"] += 1
    elif outcome == "xfailed":
        data["xfailed"] += 1
    elif outcome == "xpassed":
        data["xpassed"] += 1

    data["tests"].append({"nodeid": report.nodeid, "outcome": outcome})


def pytest_sessionfinish(session, exitstatus):
    data = session.config._notification_report
    lines = [
        "# Pytest Report",
        f"- Generated at: {datetime.now().isoformat()}",
        f"- Exit status: {exitstatus}",
        f"- Passed: {data['passed']}",
        f"- Failed: {data['failed']}",
        f"- Skipped: {data['skipped']}",
        f"- XFailed: {data['xfailed']}",
        f"- XPassed: {data['xpassed']}",
        "",
        "## Test results",
    ]

    for item in data["tests"]:
        lines.append(f"- [{item['outcome']}] {item['nodeid']}")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["INTERNAL_SERVICE_TOKEN"] = "test-internal-token"

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
