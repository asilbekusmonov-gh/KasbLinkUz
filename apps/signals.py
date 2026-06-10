from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.models import Order


@receiver(post_save, sender=Order)
def update_worker_stats(sender, instance, **kwargs):
    if instance.status == "completed":
        worker_profile = instance.service.worker
        worker_profile.completed_orders_count += 1

        from apps.models import Review

        reviews = Review.objects.filter(order__service__worker=worker_profile)

        if reviews.exists():
            total = sum(r.rating for r in reviews)
            worker_profile.rating = round(total / reviews.count(), 1)

        worker_profile.save()
