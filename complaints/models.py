from django.db import models
from django.contrib.auth.models import User


# =========================================================
# USER PROFILE
# =========================================================

class UserProfile(models.Model):

    DEPT_CHOICES = [
        ("CSE", "CSE Department"),
        ("ECE", "ECE Department"),
        ("MBA", "MBA Department"),
        ("AIML", "AIML Department"),
        ("AIDS", "AIDS Department"),
    ]

    ROLE_CHOICES = [
        ("student", "Student"),
        ("staff", "Staff"),
    ]

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True
    )

    full_name = models.CharField(
        max_length=100,
        blank=True
    )

    birthday = models.DateField(
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True
    )

    course = models.CharField(
        max_length=100,
        blank=True
    )

    department = models.CharField(
        max_length=100,
        choices=DEPT_CHOICES
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    def __str__(self):
        return self.user.username


# =========================================================
# COMPLAINT
# =========================================================

class Complaint(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Resolved", "Resolved"),
    ]

    RATING_CHOICES = [
        (1, "★"),
        (2, "★★"),
        (3, "★★★"),
        (4, "★★★★"),
        (5, "★★★★★"),
    ]

    DEPT_CHOICES = [
        ("CSE", "CSE Department"),
        ("ECE", "ECE Department"),
        ("MBA", "MBA Department"),
        ("AIML", "AIML Department"),
        ("AIDS", "AIDS Department"),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="complaints"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    department = models.CharField(
        max_length=100,
        choices=DEPT_CHOICES
    )

    proof = models.ImageField(
        upload_to="proofs/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    reply = models.TextField(
        blank=True,
        null=True
    )

    # =====================================================
    # FEEDBACK
    # =====================================================

    feedback = models.TextField(
        blank=True,
        null=True
    )

    feedback_rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        blank=True,
        null=True
    )

    feedback_submitted_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


# =========================================================
# APPROVED COLLEGE IDs
# =========================================================

class ApprovedID(models.Model):

    college_id = models.CharField(
        max_length=30,
        unique=True
    )

    department = models.CharField(
        max_length=100,
        choices=UserProfile.DEPT_CHOICES
    )

    role = models.CharField(
        max_length=20,
        choices=UserProfile.ROLE_CHOICES
    )

    is_used = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.college_id