from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views import UserViewSet

router = DefaultRouter()
router.register(r"user", UserViewSet, "user")

urlpatterns = [
    path("", include(router.urls)),
]
