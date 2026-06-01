from django.db.models import Model, CharField, SlugField, PositiveIntegerField, TextField, ForeignKey, CASCADE
from rest_framework.fields import BooleanField


class Category(Model):
    name = CharField(max_length=50)
    slug = SlugField(unique=True)


class Service(Model):
    name = CharField(max_length=50)
    min_price = PositiveIntegerField(null=True)
    max_price = PositiveIntegerField(null=True)
    active = BooleanField(default=True)
    description = TextField(null=True)
    worker = ForeignKey('apps.WorkerProfile', CASCADE, related_name='worker_services')
    category = ForeignKey('apps.Category', CASCADE, related_name='services')
