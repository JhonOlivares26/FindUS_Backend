from azure.servicebus import ServiceBusClient, ServiceBusMessage
import os


class AzureServiceBus:
    def __init__(self):
        self.connection_str = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")
        self.queue_name = os.getenv("AZURE_SERVICE_BUS_QUEUE_NAME")

    def send_message(self, message: str):
        """Envía un mensaje a la cola de Azure Service Bus"""
        with ServiceBusClient.from_connection_string(self.connection_str) as client:
            sender = client.get_queue_sender(self.queue_name)
            with sender:
                sender.send_messages(ServiceBusMessage(message))
        print("Mensaje enviado:", message)

    def receive_messages(self):
        """Recibe mensajes de la cola de Azure Service Bus"""
        received_messages = []
        with ServiceBusClient.from_connection_string(self.connection_str) as client:
            receiver = client.get_queue_receiver(self.queue_name)
            with receiver:
                for msg in receiver.receive_messages(max_message_count=5, max_wait_time=5):
                    # Deserializar correctamente el cuerpo del mensaje
                    if isinstance(msg.body, bytes):
                        message_content = msg.body.decode("utf-8")  # Convertir bytes a string
                    elif isinstance(msg.body, list):
                        message_content = "".join(
                            b.decode("utf-8") if isinstance(b, bytes) else str(b) for b in msg.body
                        )  # Convertir lista de partes en string
                    elif hasattr(msg.body, '__iter__'):
                        message_content = "".join(str(part) for part in msg.body)  # Convertir generador a string
                    else:
                        message_content = str(msg.body)  # Fallback

                    # 🛠 Eliminar prefijo b'' o comillas extrañas
                    message_content = message_content.strip("b'").strip('"')

                    received_messages.append({"message": message_content})

                    # NO eliminar el mensaje de la cola
                    # receiver.complete_message(msg)  # No llamar esto para que los mensajes sigan en la cola

        return received_messages







