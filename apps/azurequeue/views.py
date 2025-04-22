from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from apps.azurequeue.azure_service_bus import AzureServiceBus
from apps.azurequeue.serializers import SendMessageSerializer


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

    @extend_schema(summary="Recibir mensajes de la cola", description="Recibe y procesa mensajes desde Azure Service Bus")
    def get(self, request):
        bus = AzureServiceBus()
        messages = bus.receive_messages()
        return Response({"messages": messages}, status=status.HTTP_200_OK)

