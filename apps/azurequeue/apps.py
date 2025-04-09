from django.apps import AppConfig
import asyncio
import os


class AzurequeueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.azurequeue'

    def ready(self):
        """Lanza el listener de Azure Service Bus en segundo plano al iniciar Django."""
        if os.environ.get('RUN_MAIN', None) != 'true':
            from .listener_async import AzureQueueListenerAsync  # Import aquí para evitar errores en migraciones
            from django.conf import settings

            # Leer desde settings o .env
            connection_str = settings.AZURE_SERVICE_BUS_CONNECTION_STR
            queue_name = settings.AZURE_QUEUE_NAME

            listener = AzureQueueListenerAsync(connection_str, queue_name)
            loop = asyncio.get_event_loop()
            loop.create_task(listener.listen())  # Ejecuta el listener asíncrono
