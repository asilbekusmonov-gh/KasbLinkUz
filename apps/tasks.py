from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_welcome_email(user_email, username):
    send_mail(
        subject='Welcome to KasbLink!',
        message=f'Hi {username}, welcome to KasbLink!',
        from_email='noreply@kasblink.com',
        recipient_list=[user_email],
    )
