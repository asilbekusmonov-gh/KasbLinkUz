from django.db.models import Model
from django.db.models.fields import DateTimeField


class CreatedAt(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True
