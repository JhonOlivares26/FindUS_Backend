import asyncio
from azure.servicebus.aio import ServiceBusClient


class AzureQueueListenerAsync:
    def __init__(self, connection_str, queue_name):
        self.connection_str = connection_str
        self.queue_name = queue_name
        self.running = True

    async def listen(self):
        """Escucha continuamente mensajes de la cola en modo asíncrono."""
        async with ServiceBusClient.from_connection_string(self.connection_str) as client:
            receiver = client.get_queue_receiver(self.queue_name)
            async with receiver:
                while self.running:
                    messages = await receiver.receive_messages(max_message_count=5, max_wait_time=5)
                    for msg in messages:
                        print(f"📥 Mensaje recibido: {msg.body.decode('utf-8')}")
                        await receiver.complete_message(msg)

    def start_listener(self):
        """Inicia el listener en un hilo asíncrono."""
        loop = asyncio.get_event_loop()
        loop.create_task(self.listen())  # Ejecuta en background sin bloquear el loop principal
