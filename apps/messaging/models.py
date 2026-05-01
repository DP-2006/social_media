from django.db import models

# Create your models here.
# apps/messaging/models.py

from django.db import models
from django.conf import settings
from core.models.base_model import BaseModel


class Conversation(BaseModel):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    last_message_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_message_at']

    def __str__(self):
        participants_list = self.participants.values_list('phone', flat=True)[:2]
        return f"Conversation: {', '.join(participants_list)}"


class Message(BaseModel):#PV
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', '-created_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"