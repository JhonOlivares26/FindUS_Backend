from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
import os


class AzureServiceBusSender:
    def __init__(self):
        self.connection_str = os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')

    async def send_message(self, message_body, source, destination):
        async with ServiceBusClient.from_connection_string(self.connection_str) as client:
            sender = client.get_topic_sender(topic_name=destination)
            async with sender:
                msg = ServiceBusMessage(message_body)
                msg.application_properties = {
                    "source": source,
                    "destination": destination
                }
                await sender.send_messages(msg)
