from app import db
from models.invoice_model import Invoice, InvoiceItem


def create_invoice(booking_id=1, user_id=1, total_amount=500000, status="pending"):
    invoice = Invoice(
        booking_id=booking_id,
        user_id=user_id,
        total_amount=total_amount,
        status=status,
    )
    db.session.add(invoice)
    db.session.commit()
    return invoice


def create_invoice_item(invoice_id, item_type="service", description="Bảo dưỡng tổng quát", quantity=1, unit_price=500000):
    item = InvoiceItem(
        invoice_id=invoice_id,
        item_type=item_type,
        description=description,
        quantity=quantity,
        unit_price=unit_price,
        sub_total=quantity * unit_price,
    )
    db.session.add(item)
    db.session.commit()
    return item


def test_create_invoice_success(app):
    invoice = create_invoice()

    assert invoice.id is not None
    assert invoice.booking_id == 1
    assert invoice.user_id == 1
    assert invoice.total_amount == 500000
    assert invoice.status == "pending"


def test_create_invoice_item_success(app):
    invoice = create_invoice()
    item = create_invoice_item(invoice.id)

    assert item.id is not None
    assert item.invoice_id == invoice.id
    assert item.item_type == "service"
    assert item.quantity == 1
    assert item.unit_price == 500000
    assert item.sub_total == 500000


def test_calculate_invoice_total_from_items(app):
    invoice = create_invoice(total_amount=0)

    item1 = create_invoice_item(
        invoice.id,
        item_type="service",
        description="Công kiểm tra xe",
        quantity=1,
        unit_price=300000,
    )

    item2 = create_invoice_item(
        invoice.id,
        item_type="part",
        description="Lọc gió VF8",
        quantity=2,
        unit_price=150000,
    )

    total = item1.sub_total + item2.sub_total
    invoice.total_amount = total
    db.session.commit()

    assert invoice.total_amount == 600000


def test_get_invoice_by_id_success(app):
    invoice = create_invoice(booking_id=2, user_id=10)

    found_invoice = Invoice.query.get(invoice.id)

    assert found_invoice is not None
    assert found_invoice.id == invoice.id
    assert found_invoice.booking_id == 2
    assert found_invoice.user_id == 10


def test_get_invoice_by_id_not_found(app):
    invoice = Invoice.query.get(99999)

    assert invoice is None


def test_update_invoice_status_to_issued(app):
    invoice = create_invoice(status="pending")

    invoice.status = "issued"
    db.session.commit()

    assert invoice.status == "issued"


def test_update_invoice_status_to_paid(app):
    invoice = create_invoice(status="issued")

    invoice.status = "paid"
    db.session.commit()

    assert invoice.status == "paid"


def test_cancel_invoice_success(app):
    invoice = create_invoice(status="pending")

    invoice.status = "canceled"
    db.session.commit()

    assert invoice.status == "canceled"


def test_invoice_status_state_machine_valid(app):
    invoice = create_invoice(status="pending")

    invoice.status = "issued"
    db.session.commit()
    assert invoice.status == "issued"

    invoice.status = "paid"
    db.session.commit()
    assert invoice.status == "paid"


def test_invoice_items_relationship(app):
    invoice = create_invoice()

    create_invoice_item(invoice.id, item_type="service", quantity=1, unit_price=300000)
    create_invoice_item(invoice.id, item_type="part", quantity=2, unit_price=100000)

    items = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()

    assert len(items) == 2
    assert sum(item.sub_total for item in items) == 500000