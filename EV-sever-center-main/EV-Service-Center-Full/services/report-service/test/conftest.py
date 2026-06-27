import pytest
from app import create_app


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()

    app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret-key",
        "INTERNAL_SERVICE_TOKEN": "test-token",

        "FINANCE_SERVICE_URL": "http://finance-service",
        "PAYMENT_SERVICE_URL": "http://payment-service",
        "INVENTORY_SERVICE_URL": "http://inventory-service",
        "BOOKING_SERVICE_URL": "http://booking-service",
        "MAINTENANCE_SERVICE_URL": "http://maintenance-service",
    })

    yield app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Application context."""
    with app.app_context():
        yield app