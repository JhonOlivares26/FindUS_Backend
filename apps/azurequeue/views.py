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
    """Endpoint para reprocesar un mensaje fallido y reenviarlo a la suscripción Cache del tópico main"""

    @extend_schema(
        summary="Reprocesar mensaje",
        description="Recibe un mensaje con error, agrega objetos reales y lo reenvía a la suscripción Cache del tópico main"
    )
    def post(self, request):
        try:
            raw_message = request.data.get("message")
            if not raw_message:
                return Response({"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Convertir el string JSON a diccionario
            base_message = json.loads(raw_message)

            # Consultar objetos reales desde la BD
            events = serialize('json', Event.objects.all())
            categories = serialize('json', EventCategory.objects.all())
            reviews = serialize('json', EventReview.objects.all())

            # Agregar datos al mensaje
            base_message["events_data"] = {
                "events": json.loads(events),
                "event_categories": json.loads(categories),
                "event_reviews": json.loads(reviews),
            }

            # Forzar que el mensaje vaya a la suscripción 'Cache'
            base_message["sendTo"] = "Cache"

            # Enviar el mensaje al tópico 'main'
            with ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR) as client:
                sender = client.get_topic_sender(topic_name="main")
                with sender:
                    final_message = ServiceBusMessage(json.dumps(base_message))

                    # ✅ Establecer las propiedades de aplicación necesarias para el filtrado
                    final_message.application_properties = {
                        "sendTo": "Cache",
                        "type": base_message.get("type", "event"),
                        "failOn": base_message.get("failOn", ""),
                        "error": base_message.get("error", "")
                    }

                    sender.send_messages(final_message)

            return Response({"status": "Mensaje reprocesado y enviado al tópico main"}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response({"error": "Formato de mensaje inválido. Debe ser JSON válido."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Ocurrió un error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

