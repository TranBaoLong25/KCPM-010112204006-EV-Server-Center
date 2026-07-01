from app import db
from models.invoice_model import Invoice


def test_get_invoice_not_found_fail_demo(app):
    invoice = Invoice.query.get(99999)

    assert invoice is not None


def test_invoice_status_fail_demo(app):
    invoice = Invoice(
        booking_id=1,
        user_id=1,
        total_amount=500000,
        status="pending",
    )

    db.session.add(invoice)
    db.session.commit()

    invoice.status = "paid"
    db.session.commit()

    assert invoice.status == "pending"


def test_invoice_total_fail_demo(app):
    invoice = Invoice(
        booking_id=2,
        user_id=1,
        total_amount=500000,
        status="pending",
    )

    db.session.add(invoice)
    db.session.commit()

    assert invoice.total_amount == 0