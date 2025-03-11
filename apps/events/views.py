from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        # Solo los superusuarios pueden crear, actualizar o eliminar categorías
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_permissions(self):
        # Solo los organizadores pueden crear, actualizar o eliminar eventos
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
        # Solo los organizadores pueden crear eventos
        if self.request.user.user_type == "3":  # "3" es el valor para ORGANIZER
            serializer.save(event_organizer=self.request.user)
        else:
            raise PermissionDenied("Solo los organizadores pueden crear eventos.")

    def update(self, request, *args, **kwargs):
        event = self.get_object()
        # Solo el organizador o el superusuario pueden editar el evento
        if request.user.is_superuser or event.event_organizer == request.user:
            return super().update(request, *args, **kwargs)
        raise PermissionDenied("Solo el organizador puede editar este evento.")

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        # Solo el organizador o el superusuario pueden eliminar el evento
        if request.user.is_superuser or event.event_organizer == request.user:
            return super().destroy(request, *args, **kwargs)
        raise PermissionDenied("Solo el organizador puede eliminar este evento.")

    @action(detail=False, methods=["get"])
    def list_by_interests(self, request):
        try:
            user_interests = request.user.interests
        except ObjectDoesNotExist:
            return Response([])  # Lista vacía si el usuario no tiene intereses

        # Filtra eventos basados en los intereses del usuario
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

        # Evita doble registro
        if EventRegisteredUser.objects.filter(event=event, user=user).exists():
            raise PermissionDenied("Ya estás registrado en este evento.")

        serializer.save(user=user)

    def update(self, request, *args, **kwargs):
        registration = self.get_object()
        # Solo el usuario registrado puede editar su registro
        if registration.user == request.user:
            return super().update(request, *args, **kwargs)
        raise PermissionDenied("Solo el autor puede editar esta inscripción.")

    def destroy(self, request, *args, **kwargs):
        registration = self.get_object()
        # Solo el usuario registrado o el superusuario pueden eliminar el registro
        if request.user.is_superuser or registration.user == request.user:
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

        # Evita doble reseña
        if EventReview.objects.filter(event=event, user=user).exists():
            raise PermissionDenied("Ya has reseñado este evento.")

        serializer.save(user=user)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        # Solo el autor de la reseña puede editarla
        if review.user == request.user:
            return super().update(request, *args, **kwargs)
        raise PermissionDenied("Solo el autor puede editar esta reseña.")

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        # Solo el autor de la reseña o el superusuario pueden eliminarla
        if request.user.is_superuser or review.user == request.user:
            return super().destroy(request, *args, **kwargs)
        raise PermissionDenied("Solo el autor puede eliminar esta reseña.")


class InterestsViewSet(viewsets.ModelViewSet):
    queryset = Interests.objects.all()
    serializer_class = InterestsSerializer
    permission_classes = [IsAuthenticated, IsCustomerUser]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return InterestsWriteSerializer
        return InterestsSerializer

    def perform_create(self, serializer):
        user = self.request.user

        # Evita doble creación de intereses
        if Interests.objects.filter(user=user).exists():
            raise PermissionDenied("Ya tienes intereses registrados. Actualízalos en lugar de crear nuevos.")

        serializer.save(user=user)

    def update(self, request, *args, **kwargs):
        interests = self.get_object()
        # Solo el usuario puede editar sus intereses
        if interests.user == request.user:
            return super().update(request, *args, **kwargs)
        raise PermissionDenied("Solo el usuario puede editar sus intereses.")

    def destroy(self, request, *args, **kwargs):
        interests = self.get_object()
        # Solo el usuario o el superusuario pueden eliminar los intereses
        if request.user.is_superuser or interests.user == request.user:
            return super().destroy(request, *args, **kwargs)
        raise PermissionDenied("Solo el usuario puede eliminar sus intereses.")