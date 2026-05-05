from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
import uuid

from django.utils import timezone

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)

    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # email/otp verified
    is_staff = models.BooleanField(default=False)

    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("admin", "Admin"),
        ("vendor", "Vendor"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")

    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

class ProfilePicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="proile_picture", null=True, blank=True)
    image = models.ImageField(upload_to="user_profile", default="user_profile/default.png")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Profile Picture"



class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp")
    hash_otp = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        # OTP expires after 10 minutes
        expiration_time = self.created_at + timezone.timedelta(minutes=10)
        return timezone.now() > expiration_time

    def __str__(self):
        return f"{self.user.email} OTP"