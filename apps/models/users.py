from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField,
    TextChoices,
    Model,
    DecimalField,
    PositiveIntegerField,
    BooleanField,
    OneToOneField,
    CASCADE,
    ImageField,
    ForeignKey,
    TextField,
    DateTimeField,
)

from apps.models import TimeStampedModel

from apps.models.managers import CustomUserManager


class User(AbstractUser):
    class Role(TextChoices):
        WORKER = "worker", "WORKER"
        CUSTOMER = "customer", "CUSTOMER"
        ADMIN = "admin", "ADMIN"

    role = CharField(max_length=15, choices=Role.choices, default=Role.CUSTOMER)
    phone_number = CharField(unique=True, max_length=9)
    profile_image = ImageField(upload_to="users/%Y/%m/%d", null=True, blank=True)
    objects = CustomUserManager()

    @property
    def is_worker(self) -> bool:
        return self.role == User.Role.WORKER

    @property
    def is_client(self) -> bool:
        return self.role == User.Role.CUSTOMER

    @property
    def is_admin(self) -> bool:
        return self.role == User.Role.ADMIN


class WorkerProfile(Model):
    profile_image = ImageField(upload_to="users/%Y/%m/%d", null=True, blank=True)
    bio = CharField(max_length=255)
    work_start_time = DateTimeField()
    work_end_time = DateTimeField()
    rating = DecimalField(max_digits=2, decimal_places=1, default=0.0)
    completed_orders_count = PositiveIntegerField(default=0)
    is_available = BooleanField(default=True)
    user = OneToOneField(
        "apps.User", CASCADE, related_name="worker_profile", limit_choices_to={"role": User.Role.WORKER}
    )


class City(Model):
    name = CharField(max_length=100)
    worker = ForeignKey("apps.WorkerProfile", CASCADE, related_name="cities")

    def __str__(self):
        return self.name


class District(Model):
    name = CharField(max_length=100)

    city = ForeignKey("apps.City", CASCADE, related_name="districts")

    def __str__(self):
        return f"{self.city} - {self.name}"


class Portfolio(TimeStampedModel):
    worker = ForeignKey("apps.WorkerProfile", CASCADE, related_name="portfolio")

    title = CharField(max_length=150)

    description = TextField()
    image = ImageField(upload_to="portfolio/%Y/%m/%d")

    category = ForeignKey("apps.Category", CASCADE, related_name="portfolio_category")


class PortfolioImage(Model):
    portfolio = ForeignKey(
        "apps.Portfolio",
        CASCADE,
        related_name="portfolio_images",
    )

    image = ImageField(upload_to="portfolio/%Y/%m/%d")
