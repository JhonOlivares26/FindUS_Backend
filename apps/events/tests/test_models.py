import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from apps.events.models import EventCategory, Interests, Event, EventRegisteredUser, EventReview
from apps.users.models import User


@pytest.mark.django_db
class TestEventCategory:

    def test_create_event_category(self):
        category = EventCategory.objects.create(name="Conferencia", description="Charlas de tecnología")
        assert category.name == "Conferencia"
        assert category.description == "Charlas de tecnología"

    def test_str(self):
        category = EventCategory(name="Música")
        assert str(category) == "Música"

    def test_event_category_unique_name(self):
        EventCategory.objects.create(name="Conferencia")
        with pytest.raises(ValidationError):
            duplicate = EventCategory(name="Conferencia")
            duplicate.full_clean()

    def test_name_max_length(self):
        category = EventCategory(name="A" * 101)
        with pytest.raises(ValidationError):
            category.full_clean()

    def test_description_max_length(self):
        category = EventCategory(name="Conferencia", description="A" * 501)
        category.full_clean()  # No debería lanzar excepción

    def test_name_required(self):
        with pytest.raises(ValidationError):
            category = EventCategory(name="")
            category.full_clean()

    def test_description_blank(self):
        category = EventCategory(name="Conferencia", description="")
        category.full_clean()  # No debería lanzar excepción


@pytest.mark.django_db
class TestInterests:

    def test_interests_validation(self, django_user_model):
        user = django_user_model.objects.create_user(email="test@test.com", password="123456", username="testuser")
        category1 = EventCategory.objects.create(name="Deportes")
        category2 = EventCategory.objects.create(name="Música")
        category3 = EventCategory.objects.create(name="Tecnología")
        category4 = EventCategory.objects.create(name="Arte")

        interests = Interests.objects.create(user=user)
        interests.event_categories.set([category1, category2, category3, category4])

        with pytest.raises(ValidationError):
            interests.clean()

    def test_str(self, django_user_model):
        user = django_user_model.objects.create_user(email="test@test.com", password="123456", username="testuser", name="Test User")
        interests = Interests(user=user)
        assert str(interests) == "Test User"

    def test_interests_with_valid_data(self, django_user_model):
        user = django_user_model.objects.create_user(email="test@test.com", password="123456", username="testuser")
        category1 = EventCategory.objects.create(name="Deportes")
        category2 = EventCategory.objects.create(name="Música")
        interests = Interests.objects.create(user=user)
        interests.event_categories.set([category1, category2])
        interests.full_clean()  # No debería lanzar excepciones

    def test_interests_with_no_categories(self, django_user_model):
        user = django_user_model.objects.create_user(email="test@test.com", password="123456", username="testuser")
        interests = Interests.objects.create(user=user)
        interests.full_clean()  # No debería lanzar excepción

    def test_interests_with_three_categories(self, django_user_model):
        user = django_user_model.objects.create_user(email="test@test.com", password="123456", username="testuser")
        category1 = EventCategory.objects.create(name="Deportes")
        category2 = EventCategory.objects.create(name="Música")
        category3 = EventCategory.objects.create(name="Tecnología")
        interests = Interests.objects.create(user=user)
        interests.event_categories.set([category1, category2, category3])
        interests.full_clean()  # No debería lanzar excepción

    def test_interests_with_four_categories(self, django_user_model):
        user = django_user_model.objects.create_user(email="test@test.com", password="123456", username="testuser")
        category1 = EventCategory.objects.create(name="Deportes")
        category2 = EventCategory.objects.create(name="Música")
        category3 = EventCategory.objects.create(name="Tecnología")
        category4 = EventCategory.objects.create(name="Arte")
        interests = Interests.objects.create(user=user)
        interests.event_categories.set([category1, category2, category3, category4])
        with pytest.raises(ValidationError):
            interests.full_clean()


@pytest.mark.django_db
class TestEvent:

    def test_event_validation(self, django_user_model):
        user = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Conferencia")

        # Caso: Fecha en el pasado
        event = Event(
            event_name="Evento Pasado",
            event_category=category,
            event_organizer=user,
            event_description="Descripción del evento",
            event_location="Salón A",
            event_date=timezone.now() - timedelta(days=1),
            paid=False,
            has_limit=False
        )

        with pytest.raises(ValidationError):
            event.clean()

        # Caso: Evento pago sin precio
        event.event_date = timezone.now() + timedelta(days=1)
        event.paid = True
        event.price = None

        with pytest.raises(ValidationError):
            event.clean()

        # Caso: Evento gratis con precio
        event.paid = False
        event.price = 100

        with pytest.raises(ValidationError):
            event.clean()

        # Caso: Evento con cupo sin límite válido
        event.has_limit = True
        event.limit = 0

        with pytest.raises(ValidationError):
            event.clean()

    def test_event_name_max_length(self, django_user_model):
        user = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Conferencia")
        event = Event(
            event_name="A" * 101,
            event_category=category,
            event_organizer=user,
            event_description="Descripción del evento",
            event_location="Salón A",
            event_date=timezone.now() + timedelta(days=1),
            paid=False,
            has_limit=False
        )
        with pytest.raises(ValidationError):
            event.full_clean()

    def test_event_picture_optional(self, django_user_model):
        user = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Conferencia")
        event = Event(
            event_name="Evento sin imagen",
            event_category=category,
            event_organizer=user,
            event_description="Descripción del evento",
            event_location="Salón A",
            event_date=timezone.now() + timedelta(days=1),
            paid=False,
            has_limit=False,
            event_picture=None  # Imagen opcional
        )
        event.full_clean()  # No debería lanzar excepción

    def test_event_without_limit(self, django_user_model):
        user = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Conferencia")
        event = Event(
            event_name="Evento sin límite",
            event_category=category,
            event_organizer=user,
            event_description="Descripción del evento",
            event_location="Salón A",
            event_date=timezone.now() + timedelta(days=1),
            paid=False,
            has_limit=False,
            limit=None  # Sin límite
        )
        event.full_clean()  # No debería lanzar excepción

    def test_str(self):
        event = Event(event_name="Taller de Python")
        assert str(event) == "Taller de Python"

    def test_event_with_valid_data(self, django_user_model):
        user = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Conferencia")
        event = Event(
            event_name="Evento Válido",
            event_category=category,
            event_organizer=user,
            event_description="Descripción del evento",
            event_location="Salón A",
            event_date=timezone.now() + timedelta(days=1),
            paid=True,
            price=100,
            has_limit=True,
            limit=50
        )
        event.full_clean()  # No debería lanzar excepciones

    def test_event_paid_without_price(self, django_user_model):
        user = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Conferencia")
        event = Event(
            event_name="Evento sin precio",
            event_category=category,
            event_organizer=user,
            event_description="Descripción del evento",
            event_location="Salón A",
            event_date=timezone.now() + timedelta(days=1),
            paid=True,
            price=None  # Falta el precio
        )
        with pytest.raises(ValidationError):
            event.full_clean()


@pytest.mark.django_db
class TestEventRegisteredUser:

    def test_unique_constraint(self, django_user_model):
        user = django_user_model.objects.create_user(email="user@test.com", password="123456", username="user")
        organizer = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Tecnología")
        event = Event.objects.create(
            event_name="Conferencia Django",
            event_category=category,
            event_organizer=organizer,
            event_description="Descripción del evento",
            event_location="Online",
            event_date=timezone.now() + timedelta(days=5),
            paid=False,
            has_limit=False
        )
        EventRegisteredUser.objects.create(event=event, user=user)

        with pytest.raises(ValidationError):
            duplicate = EventRegisteredUser(event=event, user=user)
            duplicate.full_clean()

    def test_registration_status_default(self, django_user_model):
        user = django_user_model.objects.create_user(email="user@test.com", password="123456", username="user")
        organizer = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Tecnología")
        event = Event.objects.create(
            event_name="Conferencia Django",
            event_category=category,
            event_organizer=organizer,
            event_description="Descripción del evento",
            event_location="Online",
            event_date=timezone.now() + timedelta(days=5),
            paid=False,
            has_limit=False
        )
        registration = EventRegisteredUser(event=event, user=user)
        registration.full_clean()
        assert registration.registration_status == "1"  # Estado por defecto es "Pendiente"

    def test_clean_with_limit(self, django_user_model):
        user1 = django_user_model.objects.create_user(email="user1@test.com", password="123456", username="user1")
        user2 = django_user_model.objects.create_user(email="user2@test.com", password="123456", username="user2")
        organizer = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Tecnología")

        event = Event.objects.create(
            event_name="Evento con cupo",
            event_category=category,
            event_organizer=organizer,
            event_description="Descripción del evento",
            event_location="Online",
            event_date=timezone.now() + timedelta(days=5),
            paid=False,
            has_limit=True,
            limit=1
        )

        EventRegisteredUser.objects.create(event=event, user=user1)

        with pytest.raises(ValidationError):
            reg_user = EventRegisteredUser(event=event, user=user2)
            reg_user.clean()


@pytest.mark.django_db
class TestEventReview:

    def test_unique_constraint(self, django_user_model):
        user = django_user_model.objects.create_user(email="reviewer@test.com", password="123456", username="reviewer")
        organizer = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Tecnología")

        event = Event.objects.create(
            event_name="Conferencia IA",
            event_category=category,
            event_organizer=organizer,
            event_description="Descripción del evento",
            event_location="Virtual",
            event_date=timezone.now() + timedelta(days=10),
            paid=False,
            has_limit=False
        )

        EventReview.objects.create(user=user, event=event, rating=5, review_text="Excelente evento")

        with pytest.raises(ValidationError):
            duplicate_review = EventReview(user=user, event=event, rating=4, review_text="Muy bueno")
            duplicate_review.full_clean()

    def test_str(self, django_user_model):
        user = django_user_model.objects.create_user(email="reviewer@test.com", password="123456", username="reviewer")
        review = EventReview(user=user, rating=5)
        assert str(review) == "reviewer@test.com - 5"

    def test_review_text_max_length(self, django_user_model):
        user = django_user_model.objects.create_user(email="reviewer@test.com", password="123456", username="reviewer")
        organizer = django_user_model.objects.create_user(email="organizer@test.com", password="123456", username="organizer")
        category = EventCategory.objects.create(name="Tecnología")
        event = Event.objects.create(
            event_name="Conferencia IA",
            event_category=category,
            event_organizer=organizer,
            event_description="Descripción del evento",
            event_location="Virtual",
            event_date=timezone.now() + timedelta(days=10),
            paid=False,
            has_limit=False
        )
        review = EventReview(
            user=user,
            event=event,
            rating=5,
            review_text="A" * 501  # Excede el límite de 500 caracteres
        )
        with pytest.raises(ValidationError):
            review.full_clean()

    def test_event_review_str(self, django_user_model):
        user = django_user_model.objects.create_user(email="reviewer@test.com", password="123456", username="reviewer")
        review = EventReview(user=user, rating=5)
        assert str(review) == "reviewer@test.com - 5"