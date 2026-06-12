from django.db.models import Model, CharField, TextField, DecimalField, OneToOneField, CASCADE, ForeignKey, ImageField
from django.db.models.enums import TextChoices

from apps.models import TimeStampedModel


class Order(TimeStampedModel):
    class Status(TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    title = CharField(max_length=100)
    description = TextField()
    address = CharField(max_length=100)
    status = CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    client = ForeignKey("apps.User", on_delete=CASCADE, related_name="client_orders")
    worker = ForeignKey("apps.WorkerProfile", on_delete=CASCADE, related_name="worker_orders")
    service = ForeignKey("apps.Service", on_delete=CASCADE, related_name="orders")


class OrderImage(Model):
    order = ForeignKey("apps.Order", on_delete=CASCADE, related_name="order_images")
    image = ImageField(upload_to="users/%Y/%m/%d")


class Review(TimeStampedModel):
    order = OneToOneField("apps.Order", CASCADE, related_name="reviews")

    client = ForeignKey("apps.User", on_delete=CASCADE, related_name="reviews")
    rating = DecimalField(max_digits=5, decimal_places=2)

    comment = TextField()


class ReviewImage(Model):
    review = ForeignKey("apps.Review", on_delete=CASCADE, related_name="review_images")
    image = ImageField(upload_to="users/%Y/%m/%d")


class Favourite(Model):
    client = ForeignKey("apps.User", on_delete=CASCADE, related_name="favourites")
    worker = ForeignKey("apps.WorkerProfile", on_delete=CASCADE, related_name="favourites")

    class Meta:
        unique_together = (("client", "worker"),)
