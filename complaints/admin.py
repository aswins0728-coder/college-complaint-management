from django.contrib import admin
from .models import UserProfile, Complaint, ApprovedID


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "full_name",
        "department",
        "role",
        "phone",
    )
    list_filter = (
        "department",
        "role",
    )
    search_fields = (
        "user__username",
        "full_name",
        "phone",
    )


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "student",
        "department",
        "status",
        "created_at",
    )
    list_filter = (
        "department",
        "status",
    )
    search_fields = (
        "title",
        "description",
        "student__username",
    )


@admin.register(ApprovedID)
class ApprovedIDAdmin(admin.ModelAdmin):
    list_display = (
        "college_id",
        "department",
        "role",
        "is_used",
    )
    list_filter = (
        "department",
        "role",
        "is_used",
    )
    search_fields = (
        "college_id",
    )