from django.urls import path
from .views import SendMessageView, ReceiveMessagesView

urlpatterns = [
    path("send/", SendMessageView.as_view(), name="send-message"),
    path("receive/", ReceiveMessagesView.as_view(), name="receive-messages"),
]
