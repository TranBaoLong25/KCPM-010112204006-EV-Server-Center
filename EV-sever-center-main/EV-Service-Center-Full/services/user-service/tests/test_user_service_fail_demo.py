from services.services_refactored import UserService


def test_duplicate_email_fail_demo(app):
    """
    Email đã tồn tại nhưng cố tình kỳ vọng tạo thành công.
    Kết quả mong đợi của test: FAILED
    """
    UserService.create_user(
        "test@gmail.com",
        "user1",
        "123456"
    )

    user, error = UserService.create_user(
        "test@gmail.com",
        "user2",
        "123456"
    )

    assert user is not None


def test_duplicate_username_fail_demo(app):
    """
    Username đã tồn tại nhưng cố tình kỳ vọng tạo thành công.
    Kết quả mong đợi của test: FAILED
    """
    UserService.create_user(
        "user1@gmail.com",
        "sameuser",
        "123456"
    )

    user, error = UserService.create_user(
        "user2@gmail.com",
        "sameuser",
        "123456"
    )

    assert user is not None


def test_find_user_fail_demo(app):
    """
    User không tồn tại nhưng cố tình kỳ vọng tìm thấy.
    Kết quả mong đợi của test: FAILED
    """
    user = UserService.get_user_by_email_or_username(
        "khongtontai@gmail.com"
    )

    assert user is not None


def test_toggle_lock_fail_demo(app):
    """
    Khóa tài khoản không tồn tại nhưng cố tình kỳ vọng không có lỗi.
    Kết quả mong đợi của test: FAILED
    """
    user, error = UserService.toggle_user_lock(99999)

    assert error is None


def test_delete_user_fail_demo(app):
    """
    Xóa tài khoản không tồn tại nhưng cố tình kỳ vọng thành công.
    Kết quả mong đợi của test: FAILED
    """
    success, message = UserService.delete_user(99999)

    assert success is True