from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_booking_confirmation_email(user_email, booking_details):
    subject = 'Booking Confirmation'
    message = f'Thank you for your booking. Here are your booking details:\n{booking_details}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
    return f'Booking confirmation email sent to {user_email}.'