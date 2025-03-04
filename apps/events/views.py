from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.base.permissions import IsCustomerUser, IsOrganizerUser
from apps.events.models import Event, EventCategory, EventRegisteredUser, EventReview, Interests
from apps.events.serializers import (
    EventCategorySerializer,
    EventRegisteredUserSerializer,
    EventRegisteredUserWriteSerializer,
    EventReviewSerializer,
    EventReviewWriteSerializer,
    EventSerializer,
    EventWriteSerializer,
    InterestsSerializer,
    InterestsWriteSerializer,
)


class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOrganizerUser()]
        return [IsAuthenticatedOrReadOnly()]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOrganizerUser()]
        elif self.action == "list_by_interests":
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_class(self):
        """Devuelve el serializer correcto según la acción."""
        if self.action in ["create", "update", "partial_update"]:
            return EventWriteSerializer
        return EventSerializer

    def perform_create(self, serializer):
        if self.request.user.is_superuser and "event_organizer" in self.request.data:
            organizer = self.request.data.get("event_organizer")
            serializer.save(event_organizer=organizer)
        else:
            serializer.save(event_organizer=self.request.user)

    def update(self, request, *args, **kwargs):
        event = self.get_object()
        if request.user.is_superuser or event.event_organizer == request.user:
            return super().update(request, *args, **kwargs)
        raise PermissionDenied("Solo el organizador puede editar este evento.")

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        if request.user.is_superuser or event.event_organizer == request.user:
            return super().destroy(request, *args, **kwargs)
        raise PermissionDenied("Solo el organizador puede eliminar este evento.")

    @action(detail=False, methods=["get"])
    def list_by_interests(self, request):
        try:
            user_interests = request.user.interests
        except ObjectDoesNotExist:
            return Response([])  # Lista vacía en lugar de todos los eventos

        queryset = Event.objects.filter(
            Q(event_category=user_interests.interest_1) |
            Q(event_category=user_interests.interest_2) |
            Q(event_category=user_interests.interest_3),
            event_date__gte=timezone.now()  # Solo eventos futuros
        )
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)


class EventRegisteredUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = EventRegisteredUser.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return EventRegisteredUserWriteSerializer
        return EventRegisteredUserSerializer

    def perform_create(self, serializer):
        event = serializer.validated_data["event"]
        user = self.request.user

        if EventRegisteredUser.objects.filter(event=event, user=user).exists():
            raise PermissionDenied("Ya estás registrado en este evento.")

        serializer.save(user=user)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if user.user == request.user:
            return super().update(request, *args, **kwargs)
        raise PermissionDenied("Solo el autor puede editar esta inscripción.")

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.is_superuser or user.user == request.user:
            return super().destroy(request, *args, **kwargs)
        raise PermissionDenied("Solo el autor puede eliminar esta inscripción.")


class EventReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = EventReview.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return EventReviewWriteSerializer
        return EventReviewSerializer

    def perform_create(self, serializer):
        event = serializer.validated_data["event"]
        user = self.request.user

        if EventReview.objects.filter(event=event, user=user).exists():
            raise PermissionDenied("Ya has reseñado este evento.")

        serializer.save(user=user)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user == request.user:
            return super().update(request, *args, **kwargs)
        raise PermissionDenied("Solo el autor puede editar esta reseña.")

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if request.user.is_superuser or review.user == request.user:
            return super().destroy(request, *args, **kwargs)
        raise PermissionDenied("Solo el autor puede eliminar esta reseña.")


class InterestsViewSet(viewsets.ModelViewSet):
    queryset = Interests.objects.all()
    serializer_class = InterestsSerializer
    permission_classes = [IsCustomerUser]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return InterestsWriteSerializer
        return InterestsSerializer

    def perform_create(self, serializer):
        if Interests.objects.filter(user=self.request.user).exists():
            raise PermissionDenied("Ya tienes intereses registrados. Actualízalos en lugar de crear nuevos.")
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if user.user == request.user:
            return super().update(request, *args, **kwargs)
        raise PermissionDenied("Solo el usuario puede editar sus intereses.")

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.is_superuser or user.user == request.user:
            return super().destroy(request, *args, **kwargs)
        raise PermissionDenied("Solo el usuario puede eliminar sus intereses.")
