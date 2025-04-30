import os
from django.apps import AppConfig


class AzurequeueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.azurequeue'

    def ready(self):
        from .listener_async import AzureQueueListenerAsync  # <- importa aquí, no arriba

        connection_str = os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')
        queue_name = os.getenv('AZURE_SERVICE_BUS_QUEUE_NAME')

        if connection_str and queue_name:
            AzureQueueListenerAsync(connection_str, queue_name).start()
        else:
            print("⚠️  No se encontraron las variables de entorno para Azure Queue.")
