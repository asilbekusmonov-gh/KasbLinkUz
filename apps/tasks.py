from celery import shared_task
from django.core.mail import send_mail

from apps.models import User, Order
from django.conf import settings


@shared_task
def send_welcome_email(user_id):
    user = User.objects.get(pk=user_id)
    send_mail(
        subject="Welcome to KasbLink!",
        message=f"Hi {user.username}, Welcome to KasbLink!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@shared_task
def send_order_placed_email(order_id):
    # order = Order.objects.select_related("client", "service__worker__user").get(pk=1)
    order = (
        Order.objects.select_related("service", "client", "service__worker", "service__worker__user")
        .only("service__name", "client__username", "service__worker__user__email")
        .filter(pk=order_id)
    ).first()

    worker_email = order.service.worker.user.email
    client_name = order.client.username
    service_title = order.service.name

    send_mail(
        subject="Welcome to KasbLink!",
        message=f"Hi {client_name} placed an order for {service_title}!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[worker_email],
    )


@shared_task
def send_order_status_email(order_id, new_status):
    order = Order.objects.select_related("client", "service").get(pk=order_id)

    message = {
        "accepted": f'Your order for "{order.service.name}" was accepted! The worker has started working on it',
        "completed": f'Your order for "{order.service.name}" is completed! Please leave a review',
        "cancelled": f'Your order for "{order.service.name}" was cancelled',
    }

    message = message.get(new_status, "Your order status has changed")

    send_mail(
        subject=f"Order {new_status.capitalize()}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.service.worker.user.email],
    )
