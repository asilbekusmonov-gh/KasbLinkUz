from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.models import Order, Message, Notification, Review


@receiver(post_save, sender=Order)
def update_worker_stats(sender, instance, created, **kwargs):
    if not created and instance.status == "completed":
        worker_profile = instance.service.worker
        worker_profile.completed_orders_count += 1

        reviews = Review.objects.filter(order__service__worker=worker_profile)

        if reviews.exists():
            total = sum(r.rating for r in reviews)
            worker_profile.rating = round(total / reviews.count(), 1)

        worker_profile.save()

    if created:
        Notification.objects.create(
            recipient=instance.service.worker.user,
            sender=instance.client,
            notification_type=Notification.Type.NEW_ORDER,
            title="New Order Request",
            description=f"You received a new order request for '{instance.service.name}' from {instance.client.username}.",
        )
    else:
        status_titles = {"accepted": "Order Accepted", "completed": "Order Completed", "cancelled": "Order Cancelled"}
        status_descs = {
            "accepted": f"Your order for '{instance.service.name}' was accepted by {instance.service.worker.user.username}.",
            "completed": f"Your order '{instance.title}' has been marked as completed. Please leave a review!",
            "cancelled": f"Your order for '{instance.service.name}' was cancelled.",
        }

        title = status_titles.get(instance.status)
        desc = status_descs.get(instance.status)

        if title and desc:
            Notification.objects.create(
                recipient=instance.client,
                sender=instance.service.worker.user,
                notification_type=Notification.Type.ORDER_STATUS,
                title=title,
                description=desc,
            )


@receiver(post_save, sender=Message)
def message_created_notification(sender, instance, created, **kwargs):
    if created:
        conversation = instance.conversation
        recipient = conversation.worker if instance.sender == conversation.client else conversation.client

        sender_name = instance.sender.first_name or instance.sender.username
        msg_preview = instance.message if instance.message_type == "text" else f"Sent an {instance.message_type}"

        Notification.objects.create(
            recipient=recipient,
            sender=instance.sender,
            notification_type=Notification.Type.NEW_MESSAGE,
            title=f"New message from {sender_name}",
            description=msg_preview,
        )
