from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile, Complaint

class ComplaintModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student1", password="Pass@1234", is_active=True
        )
        UserProfile.objects.create(
            user=self.user,
            role="student",
            department="Computer_Department",
        )

    def test_complaint_defaults_to_pending(self):
        complaint = Complaint.objects.create(
            student=self.user,
            title="Projector not working",
            description="The projector in classroom G-21 is not functioning properly.",
        )
        self.assertEqual(complaint.status, "Pending")

    def test_student_dashboard_requires_login(self):
        response = self.client.get(reverse("student_dashboard"))
        self.assertEqual(response.status_code, 302)
