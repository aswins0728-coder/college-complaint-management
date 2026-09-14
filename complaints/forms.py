from django import forms
from .models import UserProfile, Complaint


# =========================================================
# USER PROFILE FORM
# =========================================================

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile

        fields = [
            "full_name",
            "birthday",
            "gender",
            "course",
            "phone",
            "profile_picture",
        ]

        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),

            "birthday": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "course": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "numeric",
                    "maxlength": "10",
                    "placeholder": "Enter 10-digit phone number",
                }
            ),

            "profile_picture": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }


# =========================================================
# COMPLAINT FORM
# =========================================================

class ComplaintForm(forms.ModelForm):

    class Meta:
        model = Complaint

        fields = [
            "department",
            "title",
            "description",
            "proof",
        ]

        widgets = {
            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter complaint title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Describe your complaint clearly",
                }
            ),

            "proof": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }


# =========================================================
# FEEDBACK FORM
# =========================================================

class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Complaint

        fields = [
            "feedback_rating",
            "feedback",
        ]

        widgets = {
            "feedback_rating": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "feedback": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Tell us about your experience...",
                }
            ),
        }