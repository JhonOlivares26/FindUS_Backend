from typing import List

from django.urls import include, path
from rest_framework import routers

from apps.stores.views import StoreViewSet

router = routers.DefaultRouter()
router.register(r"store", StoreViewSet, basename="store")

urlpatterns: List[str] = [
    path("", include(router.urls)),
]