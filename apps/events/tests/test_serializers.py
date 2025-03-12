import pytest
from apps.events.serializers import EventWriteSerializer
from apps.events.models import EventCategory
from apps.users.models import User

@pytest.mark.django_db
class TestEventSerializer:

    def test_event_serializer_valid_data(self):
        user = User.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Conferencia")
        data = {
            "event_name": "Tech Talk",
            "event_category": category.id,
            "event_organizer": user.id,
            "event_description": "Charla sobre IA",
            "event_location": "Medellín",
            "event_date": "2030-01-01T10:00:00Z",
            "paid": False,
            "has_limit": True,
            "limit": 100
        }
        serializer = EventWriteSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_event_serializer_invalid_data(self):
        data = {
            "event_name": "",
            "event_category": 999,
            "event_organizer": 999,
            "event_description": "Descripción",
            "event_location": "Medellín",
            "event_date": "2020-01-01T10:00:00Z",
            "paid": True,
            "price": None,
            "has_limit": True,
            "limit": 0
        }
        serializer = EventWriteSerializer(data=data)
        assert not serializer.is_valid()