from services.services_refactored import UserService, ProfileService
from models.user import User
from models.profile import Profile
from app import db


def test_create_user_success(app):
    user, error = UserService.create_user(
        email="test1@gmail.com",
        username="testuser1",
        password="123456"
    )

    assert error is None
    assert user is not None
    assert user.email == "test1@gmail.com"
    assert user.username == "testuser1"
    assert user.role == "user"
    assert user.status == "active"
    assert user.check_password("123456") is True


def test_create_user_duplicate_email(app):
    UserService.create_user("test2@gmail.com", "user1", "123456")

    user, error = UserService.create_user(
        email="test2@gmail.com",
        username="user2",
        password="123456"
    )

    assert user is None
    assert error == "Email đã được sử dụng"


def test_create_user_duplicate_username(app):
    UserService.create_user("user1@gmail.com", "sameuser", "123456")

    user, error = UserService.create_user(
        email="user2@gmail.com",
        username="sameuser",
        password="123456"
    )

    assert user is None
    assert error == "Tên đăng nhập đã được sử dụng"


def test_create_user_auto_create_profile(app):
    user, error = UserService.create_user(
        email="profile@gmail.com",
        username="profileuser",
        password="123456"
    )

    profile = Profile.query.filter_by(user_id=user.user_id).first()

    assert error is None
    assert profile is not None
    assert profile.user_id == user.user_id


def test_get_user_by_email_or_username(app):
    UserService.create_user("find@gmail.com", "finduser", "123456")

    user_by_email = UserService.get_user_by_email_or_username("find@gmail.com")
    user_by_username = UserService.get_user_by_email_or_username("finduser")

    assert user_by_email is not None
    assert user_by_username is not None
    assert user_by_email.user_id == user_by_username.user_id


def test_toggle_user_lock(app):
    user, _ = UserService.create_user("lock@gmail.com", "lockuser", "123456")

    locked_user, error = UserService.toggle_user_lock(user.user_id)

    assert error is None
    assert locked_user.status == "locked"

    unlocked_user, error = UserService.toggle_user_lock(user.user_id)

    assert error is None
    assert unlocked_user.status == "active"


def test_toggle_user_lock_not_found(app):
    user, error = UserService.toggle_user_lock(99999)

    assert user is None
    assert error == "Không tìm thấy người dùng"


def test_update_profile_success(app):
    user, _ = UserService.create_user("update@gmail.com", "updateuser", "123456")

    profile, error = ProfileService.update_profile(user.user_id, {
        "full_name": "Nguyen Van A",
        "phone_number": "0912345678",
        "address": "TP HCM",
        "vehicle_model": "VinFast VF8",
        "vin_number": "VIN123456"
    })

    assert error is None
    assert profile.full_name == "Nguyen Van A"
    assert profile.phone_number == "0912345678"
    assert profile.vehicle_model == "VinFast VF8"
    assert profile.vin_number == "VIN123456"


def test_delete_user_success(app):
    user, _ = UserService.create_user("delete@gmail.com", "deleteuser", "123456")

    success, message = UserService.delete_user(user.user_id)

    assert success is True
    assert message == "Xóa người dùng thành công"
    assert User.query.get(user.user_id) is None