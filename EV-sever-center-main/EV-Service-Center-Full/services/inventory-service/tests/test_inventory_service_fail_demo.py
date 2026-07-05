from services.inventory_service import InventoryService


def test_duplicate_part_number_fail_demo(app):
    InventoryService.create_item({
        "part_number": "FAIL001",
        "name": "Pin VF8",
        "quantity": 10,
        "min_quantity": 5,
        "price": 1000000,
        "center_id": 1
    })

    item, error = InventoryService.create_item({
        "part_number": "FAIL001",
        "name": "Pin VF8 Duplicate",
        "quantity": 5,
        "min_quantity": 2,
        "price": 900000,
        "center_id": 1
    })

    assert item is not None


def test_get_item_not_found_fail_demo(app):
    item = InventoryService.get_item_by_id(99999)

    assert item is not None


def test_update_item_not_found_fail_demo(app):
    item, error = InventoryService.update_item(99999, {
        "quantity": 10
    })

    assert item is not None


def test_delete_item_not_found_fail_demo(app):
    success, message = InventoryService.delete_item(99999)

    assert success is True


def test_same_part_number_same_center_should_not_error_fail_demo(app):
    InventoryService.create_item({
        "part_number": "FAIL002",
        "name": "Lốp VF8",
        "quantity": 10,
        "min_quantity": 2,
        "price": 2000000,
        "center_id": 1
    })

    item2, error2 = InventoryService.create_item({
        "part_number": "FAIL002",
        "name": "Lốp VF8 Duplicate",
        "quantity": 10,
        "min_quantity": 2,
        "price": 2000000,
        "center_id": 1
    })

    assert error2 is None
