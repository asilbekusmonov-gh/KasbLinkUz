from django.db.models import *


class Conversation(Model):
    client = ForeignKey(
        "apps.User",
        CASCADE,
        related_name="client_conversations"
    )

    worker = ForeignKey(
        "apps.User",
        CASCADE,
        related_name="worker_conversations"
    )


class Message(Model):
    class MessageType(TextChoices):
        TEXT = 'text', 'TEXT'
        IMAGE = 'image', 'IMAGE'
        VIDEO = 'video', 'VIDEO'
        LOCATION = 'location', 'LOCATION'

    conversation = ForeignKey(
        Conversation,
        CASCADE,
        related_name="messages"
    )

    sender = ForeignKey(
        "apps.User",
        CASCADE,
        related_name="messages"
    )

    message_type = CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.TEXT
    )

    message = TextField(blank=True, null=True)

    image = ImageField(
        upload_to='messages/images/',
        blank=True,
        null=True
    )

    video = FileField(
        upload_to='messages/videos/',
        blank=True,
        null=True
    )

    latitude = DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    longitude = DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    is_read = BooleanField(default=False)

    created_at = DateTimeField(auto_now_add=True)
