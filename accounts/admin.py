from django.contrib import admin
from .models import User, ProfilePicture, OTP

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "phone_number", "is_active", "is_verified", "is_staff", "role")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    list_filter = ("is_active", "is_verified", "is_staff", "role")

admin.site.register(OTP)

@admin.register(ProfilePicture)
class ProfilePictureAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    list_filter = ("created_at", "updated_at")