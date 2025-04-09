from django.db import models


class QueueMessage(models.Model):
    """Modelo para registrar los mensajes enviados a la cola"""
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje enviado el {self.sent_at}: {self.content}"
