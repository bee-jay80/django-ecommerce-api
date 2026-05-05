from accounts.tasks import send_otp_email

def send_otp_email_task(user, otp):
	# pass serializable email string to the Celery task
	send_otp_email.delay(user.email, otp)