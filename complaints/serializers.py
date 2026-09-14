from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Complaint, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "birthday",
            "gender",
            "course",
            "department",
            "role",
            "phone",
            "profile_picture",
        ]


class ComplaintSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(
        source="student.username",
        read_only=True
    )

    class Meta:
        model = Complaint
        fields = [
            "id",
            "student_username",
            "title",
            "description",
            "department",
            "proof",
            "status",
            "reply",
            "feedback",
            "feedback_rating",
            "feedback_submitted_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "student_username",
            "status",
            "reply",
            "feedback",
            "feedback_rating",
            "feedback_submitted_at",
            "created_at",
        ]