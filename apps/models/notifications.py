from django.db import models
from django.conf import settings
from django.db.models import ForeignKey
from django.db.models.enums import TextChoices
from redis.commands.search.field import TextField
from rest_framework.fields import CharField, BooleanField

from apps.models.base import TimeStampedModel


class Notification(TimeStampedModel):
    class Type(TextChoices):
        ORDER_STATUS = "order_status", "Order Status Update"
        NEW_MESSAGE = "new_message", "New Chat Message"
        NEW_ORDER = "new_order", "New Order Request"

    recipient = ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    sender = ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="sent_notifications"
    )
    notification_type = CharField(max_length=20, choices=Type.choices)
    title = CharField(max_length=150)
    description = TextField()
    is_read = BooleanField(default=False)

    class Meta:
        app_label = "apps"
        ordering = ["-created_at"]
