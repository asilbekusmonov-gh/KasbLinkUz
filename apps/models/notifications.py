from django.db import models
from django.conf import settings
from django.db.models.fields import TextField, CharField

from apps.models.base import TimeStampedModel


class Notification(TimeStampedModel):
    class Type(models.TextChoices):
        ORDER_STATUS = "order_status", "Order Status Update"
        NEW_MESSAGE = "new_message", "New Chat Message"
        NEW_ORDER = "new_order", "New Order Request"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="sent_notifications"
    )
    notification_type = CharField(max_length=20, choices=Type.choices)
    title = CharField(max_length=150)
    description = TextField()  # Now using models.TextField
    is_read = models.BooleanField(default=False)  # Now using models.BooleanField

    class Meta:
        ordering = ["-created_at"]
