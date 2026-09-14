from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ComplaintForm, FeedbackForm, UserProfileForm
from .models import Complaint, UserProfile


# =========================================================
# SIGN UP
# =========================================================

def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        department = request.POST.get("department")
        role = request.POST.get("role")
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not username or not email or not department or not role:
            messages.error(
                request,
                "Please fill in all required fields."
            )
            return redirect("signup")

        # -------------------------------------------------
        # PASSWORD MATCH
        # -------------------------------------------------

        if password1 != password2:
            messages.error(
                request,
                "Passwords do not match."
            )
            return redirect("signup")

        # -------------------------------------------------
        # PASSWORD LENGTH
        # -------------------------------------------------

        if len(password1) < 8:
            messages.error(
                request,
                "Password must contain at least 8 characters."
            )
            return redirect("signup")

        # -------------------------------------------------
        # PASSWORD STRENGTH
        # -------------------------------------------------

        if (
            not any(c.isalpha() for c in password1)
            or not any(c.isdigit() for c in password1)
            or not any(not c.isalnum() for c in password1)
        ):
            messages.error(
                request,
                "Password must contain a letter, number and special character."
            )
            return redirect("signup")

        # -------------------------------------------------
        # USERNAME CHECK
        # -------------------------------------------------

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Username already taken."
            )
            return redirect("signup")

        # -------------------------------------------------
        # EMAIL CHECK
        # -------------------------------------------------

        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                "Email address is already registered."
            )
            return redirect("signup")

        # -------------------------------------------------
        # ROLE CHECK
        # -------------------------------------------------

        if role not in {"student", "staff"}:
            messages.error(
                request,
                "Invalid role."
            )
            return redirect("signup")

        # -------------------------------------------------
        # DEPARTMENT CHECK
        # -------------------------------------------------

        if department not in dict(UserProfile.DEPT_CHOICES):
            messages.error(
                request,
                "Invalid department."
            )
            return redirect("signup")

        # -------------------------------------------------
        # CREATE ACTIVE USER
        # -------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_active=True,
        )

        # -------------------------------------------------
        # CREATE PROFILE
        # -------------------------------------------------

        UserProfile.objects.create(
            user=user,
            role=role,
            department=department,
        )

        messages.success(
            request,
            "Account created successfully! You can login now."
        )

        return redirect("login")

    return render(
        request,
        "complaints/signup.html"
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # NORMAL LOGIN
        # -------------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # -------------------------------------------------
        # EXISTING INACTIVE USER
        #
        # If an old account was created before we removed
        # email activation, check the password directly.
        # If correct, activate the account automatically.
        # -------------------------------------------------

        if user is None:

            existing_user = User.objects.filter(
                username=username
            ).first()

            if (
                existing_user
                and not existing_user.is_active
                and existing_user.check_password(password)
            ):

                existing_user.is_active = True

                existing_user.save(
                    update_fields=["is_active"]
                )

                user = authenticate(
                    request,
                    username=username,
                    password=password
                )

        # -------------------------------------------------
        # LOGIN SUCCESS
        # -------------------------------------------------

        if user is not None:

            try:

                profile = user.userprofile

            except UserProfile.DoesNotExist:

                logout(request)

                messages.error(
                    request,
                    "User profile not found."
                )

                return redirect("login")

            login(
                request,
                user
            )

            # -------------------------------------------------
            # STUDENT
            # -------------------------------------------------

            if profile.role == "student":

                return redirect(
                    "student_dashboard"
                )

            # -------------------------------------------------
            # STAFF
            # -------------------------------------------------

            if profile.role == "staff":

                return redirect(
                    "staff_dashboard"
                )

            # -------------------------------------------------
            # INVALID ROLE
            # -------------------------------------------------

            logout(request)

            messages.error(
                request,
                "Invalid user role."
            )

            return redirect("login")

        # -------------------------------------------------
        # LOGIN FAILED
        # -------------------------------------------------

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "complaints/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect("login")


# =========================================================
# OLD ACTIVATION URL
# =========================================================
#
# Kept here so an old activation URL does not crash.
# New accounts do NOT need activation.
#

def activate_account(request, uidb64=None, token=None):

    messages.info(
        request,
        "Email activation is no longer required. You can login directly."
    )

    return redirect("login")


# =========================================================
# OLD SEND ACTIVATION EMAIL
# =========================================================
#
# Kept only for compatibility with any old code.
# It is NOT called during signup anymore.
#

def send_activation_email(user, request):

    return None


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@login_required
def student_dashboard(request):

    try:

        user_profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect("login")

    if user_profile.role != "student":

        messages.error(
            request,
            "Access denied."
        )

        return redirect("login")

    complaints = Complaint.objects.filter(
        student=request.user
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "complaints/student_dashboard.html",
        {
            "complaints": complaints,
            "user_profile": user_profile,
        }
    )


# =========================================================
# SUBMIT COMPLAINT
# =========================================================

@login_required
def submit_complaint(request):

    try:

        user_profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect("login")

    if user_profile.role != "student":

        messages.error(
            request,
            "Only students can submit complaints."
        )

        return redirect("login")

    if request.method == "POST":

        form = ComplaintForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            complaint = form.save(
                commit=False
            )

            complaint.student = request.user

            complaint.save()

            messages.success(
                request,
                "Complaint submitted successfully."
            )

            return redirect(
                "student_dashboard"
            )

    else:

        form = ComplaintForm(
            initial={
                "department": user_profile.department
            }
        )

    return render(
        request,
        "complaints/submit_complaint.html",
        {
            "form": form,
            "user_profile": user_profile,
        }
    )


# =========================================================
# STUDENT VIEW COMPLAINT
# =========================================================

@login_required
def student_view_complaint(request, complaint_id):

    try:

        profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect("login")

    if profile.role != "student":

        messages.error(
            request,
            "Access denied."
        )

        return redirect("login")

    complaint = get_object_or_404(
        Complaint,
        id=complaint_id,
        student=request.user
    )

    return render(
        request,
        "complaints/student_view_complaint.html",
        {
            "complaint": complaint
        }
    )


# =========================================================
# DELETE COMPLAINT
# =========================================================

@login_required
def delete_complaint(request, complaint_id):

    try:

        profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect("login")

    if profile.role != "student":

        messages.error(
            request,
            "Access denied."
        )

        return redirect("login")

    complaint = Complaint.objects.filter(
        id=complaint_id,
        student=request.user
    ).first()

    if complaint is None:

        messages.error(
            request,
            "Complaint not found."
        )

        return redirect(
            "student_dashboard"
        )

    if request.method == "POST":

        complaint.delete()

        messages.success(
            request,
            "Complaint deleted successfully."
        )

    return redirect(
        "student_dashboard"
    )


# =========================================================
# STUDENT FEEDBACK
# =========================================================

@login_required
def submit_feedback(request, complaint_id):

    try:

        profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect("login")

    if profile.role != "student":

        messages.error(
            request,
            "Access denied."
        )

        return redirect("login")

    complaint = get_object_or_404(
        Complaint,
        id=complaint_id,
        student=request.user
    )

    if complaint.status != "Resolved":

        messages.error(
            request,
            "Feedback can only be submitted after the complaint is resolved."
        )

        return redirect(
            "student_view_complaint",
            complaint_id=complaint.id
        )

    if complaint.feedback_rating or complaint.feedback:

        messages.info(
            request,
            "Feedback has already been submitted."
        )

        return redirect(
            "student_view_complaint",
            complaint_id=complaint.id
        )

    if request.method == "POST":

        form = FeedbackForm(
            request.POST
        )

        if form.is_valid():

            complaint.feedback_rating = (
                form.cleaned_data["feedback_rating"]
            )

            complaint.feedback = (
                form.cleaned_data["feedback"]
            )

            complaint.feedback_submitted_at = (
                timezone.now()
            )

            complaint.save(
                update_fields=[
                    "feedback_rating",
                    "feedback",
                    "feedback_submitted_at",
                ]
            )

            messages.success(
                request,
                "Thank you! Your feedback has been submitted."
            )

            return redirect(
                "student_view_complaint",
                complaint_id=complaint.id
            )

    else:

        form = FeedbackForm()

    return render(
        request,
        "complaints/feedback.html",
        {
            "form": form,
            "complaint": complaint,
        }
    )


# =========================================================
# STAFF DASHBOARD
# =========================================================

@login_required
def staff_dashboard(request):

    try:

        user_profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect("login")

    if user_profile.role != "staff":

        messages.error(
            request,
            "Only staff members can access this page."
        )

        return redirect("login")

    complaints = Complaint.objects.filter(
        department=user_profile.department
    ).select_related(
        "student",
        "student__userprofile"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "complaints/staff_dashboard.html",
        {
            "complaints": complaints,
            "user_profile": user_profile,
        }
    )



        return redirect("login")

    complaint = get_object_or_404(
        Complaint,
        id=complaint_id
    )

    # -----------------------------------------------------
    # DEPARTMENT SECURITY
    # -----------------------------------------------------

    if complaint.department != profile.department:

        messages.error(
            request,
            "You can only manage complaints from your department."
        )

        return redirect(
            "staff_dashboard"
        )

    if request.method == "POST":

        reply = request.POST.get(
            "reply",
            ""
        ).strip()

        if len(reply) < 20:

            messages.error(
                request,
                "Reply must be at least 20 characters."
            )

        else:

            complaint.reply = reply

            complaint.status = "Resolved"

            complaint.save(
                update_fields=[
                    "reply",
                    "status",
                ]
            )

            messages.success(
                request,
                "Reply submitted and complaint marked as resolved."
            )

            return redirect(
                "staff_dashboard"
            )

    return render(
        request,
        "complaints/staff_view_complaint.html",
        {
            "complaint": complaint
        }
    )# =========================================================
# STAFF VIEW COMPLAINT + REPLY
# =========================================================

@login_required
def staff_view_complaint(request, complaint_id):

    try:
        profile = request.user.userprofile

    except UserProfile.DoesNotExist:
        messages.error(
            request,
            "User profile not found."
        )
        return redirect("login")

    if profile.role != "staff":
        messages.error(
            request,
            "Access denied."
        )
        return redirect("login")

    complaint = get_object_or_404(
        Complaint,
        id=complaint_id
    )

    if complaint.department != profile.department:
        messages.error(
            request,
            "You can only manage complaints from your department."
        )
        return redirect("staff_dashboard")

    if request.method == "POST":

        reply = request.POST.get(
            "reply",
            ""
        ).strip()

        if not reply:
            messages.error(
                request,
                "Please enter a reply."
            )
            return redirect(
                "staff_view_complaint",
                complaint_id=complaint.id
            )

        if len(reply) < 20:
            messages.error(
                request,
                "Reply must be at least 20 characters."
            )
            return redirect(
                "staff_view_complaint",
                complaint_id=complaint.id
            )

        complaint.reply = reply
        complaint.status = "Resolved"

        complaint.save(
            update_fields=[
                "reply",
                "status",
            ]
        )

        messages.success(
            request,
            "Reply submitted successfully. Complaint marked as Resolved."
        )

        return redirect("staff_dashboard")

    return render(
        request,
        "complaints/staff_view_complaint.html",
        {
            "complaint": complaint,
            "profile": profile,
        }
    )

# =========================================================
# PROFILE
# =========================================================

@login_required
def profile_view(request):

    user_profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "role": "student",
            "department": "CSE",
        }
    )

    # -----------------------------------------------------
    # PROFILE PHOTO
    # -----------------------------------------------------

    if (
        request.method == "POST"
        and request.FILES.get("profile_picture")
    ):

        user_profile.profile_picture = (
            request.FILES["profile_picture"]
        )

        user_profile.save(
            update_fields=[
                "profile_picture"
            ]
        )

        messages.success(
            request,
            "Profile photo updated successfully!"
        )

        return redirect(
            "student_profile"
        )

    # -----------------------------------------------------
    # PROFILE DETAILS
    # -----------------------------------------------------

    if request.method == "POST":

        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=user_profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully!"
            )

            return redirect(
                "student_profile"
            )

        messages.error(
            request,
            "Please correct the errors below."
        )

    else:

        form = UserProfileForm(
            instance=user_profile
        )

    return render(
        request,
        "complaints/profile.html",
        {
            "form": form,
            "user_profile": user_profile,
        }
    )