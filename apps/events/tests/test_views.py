from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.events.models import EventCategory, Event, EventRegisteredUser, EventReview, Interests

User = get_user_model()


class EventCategoryViewSetTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="password123"
        )
        self.organizer = User.objects.create_user(
            email="organizer@example.com", username="organizer", password="password123", user_type="3"
        )
        self.customer = User.objects.create_user(
            email="customer@example.com", username="customer", password="password123", user_type="1"
        )
        self.category = EventCategory.objects.create(name="Conferencia")

    def test_list_categories(self):
        url = reverse("events:eventcategory-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category_by_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse("events:eventcategory-list")
        data = {"name": "Taller"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_by_organizer_forbidden(self):
        self.client.force_authenticate(user=self.organizer)
        url = reverse("events:eventcategory-list")
        data = {"name": "Taller"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_by_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("events:eventcategory-list")
        data = {"name": "Taller"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EventViewSetTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="password123"
        )
        self.organizer = User.objects.create_user(
            email="organizer@example.com", username="organizer", password="password123", user_type="3"
        )
        self.customer = User.objects.create_user(
            email="customer@example.com", username="customer", password="password123", user_type="1"
        )
        self.category = EventCategory.objects.create(name="Conferencia")

    def test_create_event_by_organizer(self):
        self.client.force_authenticate(user=self.organizer)
        url = reverse("events:event-list")
        data = {
            "event_name": "Tech Talk",
            "event_category": self.category.id,
            "event_description": "Charla sobre IA",
            "event_location": "Medellín",
            "event_date": "2030-01-01T10:00:00Z",
            "paid": False,
            "has_limit": True,
            "limit": 100
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_event_by_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("events:event-list")
        data = {
            "event_name": "Tech Talk",
            "event_category": self.category.id,
            "event_description": "Charla sobre IA",
            "event_location": "Medellín",
            "event_date": "2030-01-01T10:00:00Z",
            "paid": False,
            "has_limit": True,
            "limit": 100
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class InterestsViewSetTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email="customer@example.com", username="customer", password="password123", user_type="1"
        )
        self.category1 = EventCategory.objects.create(name="Conferencia")
        self.category2 = EventCategory.objects.create(name="Taller")

    def test_create_interests(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("events:interests-list")
        data = {"event_categories": [self.category1.id, self.category2.id]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)