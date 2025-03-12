import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.serializers import UserSerializer

@pytest.mark.django_db
class TestUserViewSet(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            username="testuser",
            name="Test",
            last_name="User",
            phone="1234567890"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="admin123",
            username="adminuser"
        )
        self.client.force_authenticate(user=self.admin)

    def test_register_user(self):
        url = reverse("users:user-register")
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "name": "New",
            "last_name": "User",
            "phone": "0987654321"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_login_user(self):
        url = reverse("users:user-login")
        data = {
            "email": "test@example.com",
            "password": "password123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_logout_user(self):
        url = reverse("users:user-logout")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_recover_password(self):
        url = reverse("users:user-recover-password")
        data = {
            "email": "test@example.com",
            "password": "newpassword123",
            "re_password": "newpassword123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_update_profile(self):
        url = reverse("users:user-update-profile")
        data = {
            "name": "Updated",
            "last_name": "Name",
            "phone": "9876543210"
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Updated")

    def test_query_email(self):
        url = reverse("users:user-query-email")
        response = self.client.get(url, {"email": "test@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_query_username(self):
        url = reverse("users:user-query-username")
        response = self.client.get(url, {"username": "testuser"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)