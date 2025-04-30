from django.urls import path
from .views import SendMessageView, ReceiveMessagesView, ReprocessedMessageView

urlpatterns = [
    path("send/", SendMessageView.as_view(), name="send-message"),
    path("receive/", ReceiveMessagesView.as_view(), name="receive-messages"),
    path('messages/publish', ReprocessedMessageView.as_view(), name='reprocessed-publish'),
]
