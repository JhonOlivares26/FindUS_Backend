import asyncio
import json
import threading
import datetime
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from apps.azurequeue.azure_service_bus_sender import AzureServiceBusSender  # Crear este sender como tu compañero
from apps.events.models import Event, EventCategory, EventReview  # Ajusta al nombre real de tus modelos
from django.core.serializers import serialize


class AzureQueueListenerAsync(threading.Thread):
    def __init__(self, connection_str, queue_name):
        super().__init__()
        self.connection_str = connection_str
        self.queue_name = queue_name

    def run(self):
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=self.connection_str, logging_enable=True)
        with servicebus_client:
            sender = servicebus_client.get_queue_sender(queue_name=self.queue_name)
            with sender:
                # Aquí es donde vas a consultar objetos reales
                event = Event.objects.first()
                category = EventCategory.objects.first()
                review = EventReview.objects.first()

                if event and category and review:
                    message_body = {
                        "type": "new_event",
                        "event": {
                            "id": event.id,
                            "name": event.event_name,  # Ajusta a tus campos reales
                            "description": event.event_description,
                            "location": event.event_location,
                            "date": event.event_date.isoformat(),  # Convertir datetime a string
                        },
                        "category": {
                            "id": category.id,
                            "name": category.name,
                            "description": category.description,
                        },
                        "review": {
                            "id": review.id,
                            "rating": review.rating,
                            "review_text": review.review_text,
                        },
                        "sendTo": "another_service",
                        "failOn": None,
                        "error": None
                    }
                    print(message_body)
                    message = ServiceBusMessage(json.dumps(message_body))
                    sender.send_messages(message)
                    print("✅ Mensaje enviado con datos reales.")
                else:
                    print("⚠️ No se encontraron datos para enviar.")
