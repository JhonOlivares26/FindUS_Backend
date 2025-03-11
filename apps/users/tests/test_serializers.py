import pytest
from rest_framework.exceptions import ValidationError

from apps.users.models import User
from apps.users.serializers import (
    UserSerializer,
    RecoverPasswordSerializer,
    UpdateProfileSerializer,
    LoginUserSerializer
)

@pytest.mark.django_db
class TestUserSerializer:

    def test_create_user(self):
        data = {
            "email": "test@example.com",
            "password": "password123",
            "name": "Test",
            "last_name": "User",
            "phone": "1234567890"
        }
        serializer = UserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username is not None
        assert user.check_password("password123")

    def test_create_user_without_username(self):
        data = {
            "email": "test@example.com",
            "password": "password123",
            "name": "Test",
            "last_name": "User",
            "phone": "1234567890"
        }
        serializer = UserSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username is not None


@pytest.mark.django_db
class TestRecoverPasswordSerializer:

    def test_recover_password(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="oldpassword",
            username="testuser"
        )
        data = {
            "email": "test@example.com",
            "password": "newpassword123",
            "re_password": "newpassword123"
        }
        serializer = RecoverPasswordSerializer(user, data=data)
        assert serializer.is_valid()
        serializer.save()
        user.refresh_from_db()
        assert user.check_password("newpassword123")

    def test_recover_password_mismatch(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="oldpassword",
            username="testuser"
        )
        data = {
            "email": "test@example.com",
            "password": "newpassword123",
            "re_password": "wrongpassword"
        }
        serializer = RecoverPasswordSerializer(user, data=data)
        assert not serializer.is_valid()
        assert "Passwords do not match" in str(serializer.errors)


@pytest.mark.django_db
class TestUpdateProfileSerializer:

    def test_update_profile(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            username="testuser"
        )
        data = {
            "name": "Updated",
            "last_name": "Name",
            "phone": "9876543210"
        }
        serializer = UpdateProfileSerializer(user, data=data)
        assert serializer.is_valid()
        serializer.save()
        user.refresh_from_db()
        assert user.name == "Updated"


@pytest.mark.django_db
class TestLoginUserSerializer:

    def test_login_valid_credentials(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            username="testuser"
        )
        data = {
            "email": "test@example.com",
            "password": "password123"
        }
        serializer = LoginUserSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["user"] == user

    def test_login_invalid_credentials(self):
        data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        serializer = LoginUserSerializer(data=data)
        assert not serializer.is_valid()
        assert "Invalid Credentials" in str(serializer.errors)