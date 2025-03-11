from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.stores.models import Store
from apps.stores.serializers import StoreSerializer


# Create your views here.
class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    queryset = Store.objects.all()