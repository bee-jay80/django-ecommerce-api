from random import randint
from ..models import OTP
# hashing
from django.contrib.auth.hashers import make_password, check_password


from accounts.utils.emails import send_otp_email_task
def generate_send_otp(user):
    # Generate a random six-digit OTP
    otp = randint(100000, 999999)

    # Hash the OTP before saving to the database (for security)
    hash_otp = make_password(str(otp))

    # Save the hashed OTP to the database
    OTP.objects.create(user=user, hash_otp=hash_otp)

    # Send the OTP to the user's email asynchronously
    send_otp_email_task(user, otp)

def verify_otp(user, otp):
    try:
        otp_record = OTP.objects.filter(user=user).latest("created_at")

        if otp_record.is_expired():
            otp_record.delete()  # Delete expired OTP
            return False

    except OTP.DoesNotExist:
        return False

    # Check if the provided OTP matches the hashed OTP in the database
    if check_password(str(otp), otp_record.hash_otp):
        # If the OTP is correct, you can delete it from the database
        otp_record.delete()
        return True