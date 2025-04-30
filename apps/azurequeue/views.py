from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from apps.azurequeue.azure_service_bus import AzureServiceBus
from apps.azurequeue.serializers import SendMessageSerializer
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from django.core.serializers import serialize
from apps.events.models import Event, EventCategory, EventReview
import json
import os

CONNECTION_STR = os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')
TOPIC_CACHE = "Cache"


class SendMessageView(APIView):
    """Endpoint para enviar mensajes a la cola"""

    @extend_schema(
        summary="Enviar mensaje a la cola",
        description="Envía un mensaje a Azure Service Bus",
        request=SendMessageSerializer,  # <--- Esto le dice a Swagger que espera un JSON con 'message'
    )
    def post(self, request):
        serializer = SendMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data["message"]
            bus = AzureServiceBus()
            bus.send_message(message)
            return Response({"message": "Mensaje enviado correctamente"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceiveMessagesView(APIView):
    """Endpoint para recibir mensajes de la cola"""

    @extend_schema(summary="Recibir mensajes de la cola",
                   description="Recibe y procesa mensajes desde Azure Service Bus")
    def get(self, request):
        bus = AzureServiceBus()
        messages = bus.receive_messages()
        return Response({"messages": messages}, status=status.HTTP_200_OK)


class ReprocessedMessageView(APIView):
    def post(self, request):
        try:
            raw_message = request.data.get("message", "")
            if not raw_message:
                return Response({"error": "No message provided"}, status=400)

            base_message = json.loads(raw_message)  # string a dict

            # Carga tus objetos de la BD
            events = serialize('json', Event.objects.all())
            categories = serialize('json', EventCategory.objects.all())
            reviews = serialize('json', EventReview.objects.all())

            base_message["events_data"] = {
                "events": json.loads(events),
                "event_categories": json.loads(categories),
                "event_reviews": json.loads(reviews),
            }

            # Enviar a Azure -> tópico
            with ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR) as client:
                sender = client.get_topic_sender(topic_name=TOPIC_CACHE)
                with sender:
                    final_msg = ServiceBusMessage(json.dumps(base_message))
                    sender.send_messages(final_msg)

            return Response({"status": "Message processed and sent to Cache"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
