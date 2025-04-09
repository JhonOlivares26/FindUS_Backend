from rest_framework import serializers
from .models import QueueMessage


class QueueMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueMessage
        fields = ["id", "content", "sent_at"]


class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
