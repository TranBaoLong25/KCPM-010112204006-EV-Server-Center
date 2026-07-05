from services.inventory_service import InventoryService


def test_create_item_success(app):
    item, error = InventoryService.create_item({
        "part_number": "INV001",
        "name": "Pin Lithium-ion VF8",
        "quantity": 10,
        "min_quantity": 5,
        "price": 1000000,
        "center_id": 1
    })

    assert error is None
    assert item is not None
    assert item.part_number == "INV001"
    assert item.quantity == 10
    assert item.center_id == 1


def test_create_item_duplicate_part_number(app):
    InventoryService.create_item({
        "part_number": "INV002",
        "name": "Má phanh VF8",
        "quantity": 5,
        "min_quantity": 2,
        "price": 500000,
        "center_id": 1
    })

    item, error = InventoryService.create_item({
        "part_number": "INV002",
        "name": "Má phanh VF8 Duplicate",
        "quantity": 3,
        "min_quantity": 1,
        "price": 400000,
        "center_id": 1
    })

    assert item is None
    assert error is not None


def test_get_item_by_id_success(app):
    item, _ = InventoryService.create_item({
        "part_number": "INV003",
        "name": "Lọc gió VF8",
        "quantity": 20,
        "min_quantity": 5,
        "price": 300000,
        "center_id": 1
    })

    found_item = InventoryService.get_item_by_id(item.id)

    assert found_item is not None
    assert found_item.id == item.id
    assert found_item.part_number == "INV003"


def test_get_item_by_id_not_found(app):
    item = InventoryService.get_item_by_id(99999)

    assert item is None


def test_get_all_items(app):
    InventoryService.create_item({
        "part_number": "INV004",
        "name": "Dầu phanh",
        "quantity": 10,
        "min_quantity": 3,
        "price": 250000,
        "center_id": 1
    })

    InventoryService.create_item({
        "part_number": "INV005",
        "name": "Cảm biến áp suất lốp",
        "quantity": 8,
        "min_quantity": 2,
        "price": 700000,
        "center_id": 1
    })

    items = InventoryService.get_all_items(center_id=1)

    assert len(items) == 2


def test_update_item_success(app):
    item, _ = InventoryService.create_item({
        "part_number": "INV006",
        "name": "Ắc quy 12V",
        "quantity": 10,
        "min_quantity": 2,
        "price": 1200000,
        "center_id": 1
    })

    updated_item, error = InventoryService.update_item(item.id, {
        "name": "Ắc quy 12V Updated",
        "quantity": 15,
        "min_quantity": 3,
        "price": 1300000,
        "center_id": 1
    })

    assert error is None
    assert updated_item is not None
    assert updated_item.name == "Ắc quy 12V Updated"
    assert updated_item.quantity == 15
    assert updated_item.price == 1300000


def test_update_item_not_found(app):
    item, error = InventoryService.update_item(99999, {
        "quantity": 10
    })

    assert item is None
    assert error == "Không tìm thấy vật tư"


def test_delete_item_success(app):
    item, _ = InventoryService.create_item({
        "part_number": "INV007",
        "name": "Cáp sạc",
        "quantity": 5,
        "min_quantity": 1,
        "price": 900000,
        "center_id": 1
    })

    success, message = InventoryService.delete_item(item.id)

    assert success is True
    assert InventoryService.get_item_by_id(item.id) is None


def test_delete_item_not_found(app):
    success, message = InventoryService.delete_item(99999)

    assert success is False
    assert message == "Không tìm thấy vật tư"


def test_get_low_stock_items(app):
    InventoryService.create_item({
        "part_number": "INV008",
        "name": "Lốp Michelin VF8",
        "quantity": 3,
        "min_quantity": 5,
        "price": 6800000,
        "center_id": 1
    })

    InventoryService.create_item({
        "part_number": "INV009",
        "name": "Pin VF8",
        "quantity": 10,
        "min_quantity": 5,
        "price": 1000000,
        "center_id": 1
    })

    low_stock_items = InventoryService.get_low_stock_items(center_id=1)

    assert len(low_stock_items) == 1
    assert low_stock_items[0].part_number == "INV008"