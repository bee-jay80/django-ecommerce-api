from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# OTP MAIL SENDER
@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_backoff_max=600, retry_jitter=True, max_retries=5, name="send_otp_email_task")
def send_otp_email(self, email, otp):
    User = get_user_model()
    try:
        # get user by email
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return

    subject = "Verify your email"
    current_year = timezone.now().year
    html_content = render_to_string(
        "emails/send_email_otp.html",
        {"user_name": user.username, "otp": otp, "current_year": current_year}
    )

    msg = EmailMultiAlternatives(
        subject,
        to=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# delete all expired OTPs after every 10 minutes
@shared_task
def delete_expired_otps():
    from .models import OTP
    cutoff = timezone.now() - timezone.timedelta(minutes=10)
    expired_otps = OTP.objects.filter(created_at__lte=cutoff)
    count = expired_otps.count()
    if count:
        expired_otps.delete()
        logger.info("Deleted %d expired OTP(s) older than %s", count, cutoff.isoformat())
    else:
        logger.debug("No expired OTPs to delete (cutoff=%s)", cutoff.isoformat())
    return count