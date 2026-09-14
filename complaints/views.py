import re
import secrets
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ComplaintForm, FeedbackForm, UserProfileForm
from .models import ApprovedID, Complaint, UserProfile


# =========================================================
# OTP SETTINGS
# =========================================================

OTP_EXPIRY_MINUTES = 5


# =========================================================
# OTP GENERATION
# =========================================================

def generate_otp():
    """
    Generate a secure 6-digit OTP.
    """
    return str(secrets.randbelow(900000) + 100000)


def send_otp_email(email, otp, purpose="verification"):
    """
    Send OTP to the user's email.
    """

    if purpose == "verification":

        subject = (
            "College Complaint Management - "
            "Email Verification OTP"
        )

        message = f"""
Hello,

Your OTP for College Complaint Management
account verification is:

{otp}

This OTP is valid for {OTP_EXPIRY_MINUTES} minutes.

If you did not request this verification,
please ignore this email.

Thank you.

College Complaint Management System
"""

    else:

        subject = (
            "College Complaint Management - "
            "Password Reset OTP"
        )

        message = f"""
Hello,

Your OTP for resetting your College Complaint
Management password is:

{otp}

This OTP is valid for {OTP_EXPIRY_MINUTES} minutes.

If you did not request a password reset,
please ignore this email.

Thank you.

College Complaint Management System
"""

    send_mail(
        subject,
        message,
        None,
        [email],
        fail_silently=False,
    )


# =========================================================
# OTP SESSION HELPERS
# =========================================================

def save_otp_in_session(request, otp, email, purpose):
    """
    Save OTP, email and creation time in session.
    """

    request.session[f"{purpose}_otp"] = otp

    request.session[f"{purpose}_email"] = email

    request.session[f"{purpose}_otp_created"] = (
        timezone.now().isoformat()
    )

    request.session.modified = True


def get_otp_from_session(request, purpose):
    """
    Get OTP information from session.

    Returns:
        otp,
        email,
        created_at
    """

    otp = request.session.get(
        f"{purpose}_otp"
    )

    email = request.session.get(
        f"{purpose}_email"
    )

    created_string = request.session.get(
        f"{purpose}_otp_created"
    )

    if not otp or not email or not created_string:
        return None, None, None

    try:

        created_at = datetime.fromisoformat(
            created_string
        )

        if timezone.is_naive(created_at):

            created_at = timezone.make_aware(
                created_at
            )

    except (ValueError, TypeError):

        return None, None, None

    return otp, email, created_at


def clear_otp_from_session(request, purpose):
    """
    Remove OTP information from session.
    """

    request.session.pop(
        f"{purpose}_otp",
        None
    )

    request.session.pop(
        f"{purpose}_email",
        None
    )

    request.session.pop(
        f"{purpose}_otp_created",
        None
    )

    request.session.modified = True


def is_otp_expired(created_at):
    """
    Check whether OTP has expired.
    """

    expiry_time = (
        created_at
        + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        )
    )

    return timezone.now() > expiry_time


# =========================================================
# COLLEGE ID VALIDATION
# =========================================================

def validate_student_id(student_id, department):
    """
    Validate student College ID.

    Examples:
        25JUCS141
        24JUCS193
        23JUEC101
        etc.
    """

    student_id = student_id.strip().upper()

    department_codes = {
        "CSE": "CS",
        "ECE": "EC",
        "MBA": "MBA",
        "AIML": "AIML",
        "AIDS": "AIDS",
    }

    expected_code = department_codes.get(
        department
    )

    if not expected_code:

        return (
            False,
            "Invalid department."
        )

    pattern = (
        rf"^(\d{{2}})JU"
        rf"{re.escape(expected_code)}"
        rf"(\d{{3}})$"
    )

    match = re.fullmatch(
        pattern,
        student_id
    )

    if not match:

        return (
            False,
            "Invalid College ID format."
        )

    joining_year = int(
        match.group(1)
    )

    if joining_year < 21:

        return (
            False,
            "Invalid College ID."
        )

    return True, ""


def validate_staff_id(staff_id):
    """
    Validate staff College ID.

    Example:
        JU-6841-CSE
    """

    staff_id = staff_id.strip().upper()

    pattern = (
        r"^JU-\d{4}-"
        r"(CSE|ECE|MBA|AIML|AIDS)$"
    )

    if not re.fullmatch(
        pattern,
        staff_id
    ):

        return (
            False,
            "Invalid College ID format."
        )

    return True, ""


# =========================================================
# SIGN UP
# =========================================================

def signup_view(request):

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        college_id = request.POST.get(
            "college_id",
            ""
        ).strip().upper()

        department = request.POST.get(
            "department",
            ""
        ).strip().upper()

        role = request.POST.get(
            "role",
            ""
        ).strip().lower()

        password1 = request.POST.get(
            "password1",
            ""
        )

        password2 = request.POST.get(
            "password2",
            ""
        )

        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not email:

            messages.error(
                request,
                "Please enter your email address."
            )

            return redirect("signup")

        if not college_id:

            messages.error(
                request,
                "Please enter your College ID Card Number."
            )

            return redirect("signup")

        if not department:

            messages.error(
                request,
                "Please select your department."
            )

            return redirect("signup")

        if not role:

            messages.error(
                request,
                "Please select your account type."
            )

            return redirect("signup")

        # =================================================
        # ROLE VALIDATION
        # =================================================

        if role not in {
            "student",
            "staff",
        }:

            messages.error(
                request,
                "Invalid account type selected."
            )

            return redirect("signup")

        # =================================================
        # DEPARTMENT VALIDATION
        # =================================================

        valid_departments = {
            choice[0]
            for choice in UserProfile.DEPT_CHOICES
        }

        if department not in valid_departments:

            messages.error(
                request,
                "Invalid department selected."
            )

            return redirect("signup")

        # =================================================
        # COLLEGE ID FORMAT
        # =================================================

        if role == "student":

            valid, error_message = (
                validate_student_id(
                    college_id,
                    department
                )
            )

            if not valid:

                messages.error(
                    request,
                    error_message
                )

                return redirect("signup")

        else:

            valid, error_message = (
                validate_staff_id(
                    college_id
                )
            )

            if not valid:

                messages.error(
                    request,
                    error_message
                )

                return redirect("signup")

        # =================================================
        # APPROVED ID CHECK
        # =================================================

        approved_id = (
            ApprovedID.objects.filter(
                college_id=college_id
            ).first()
        )

        if approved_id is None:

            messages.error(
                request,
                "This College ID is not approved for registration."
            )

            return redirect("signup")

        # =================================================
        # DEPARTMENT MATCH
        # =================================================

        if approved_id.department != department:

            messages.error(
                request,
                "The selected department does not match your approved College ID."
            )

            return redirect("signup")

        # =================================================
        # ROLE MATCH
        # =================================================

        if approved_id.role != role:

            messages.error(
                request,
                "The selected account type does not match your approved College ID."
            )

            return redirect("signup")

        # =================================================
        # PASSWORD VALIDATION
        # =================================================

        if password1 != password2:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("signup")

        if len(password1) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

            return redirect("signup")

        if not any(
            c.isalpha()
            for c in password1
        ):

            messages.error(
                request,
                "Password must contain at least one letter."
            )

            return redirect("signup")

        if not any(
            c.isdigit()
            for c in password1
        ):

            messages.error(
                request,
                "Password must contain at least one number."
            )

            return redirect("signup")

        if not any(
            not c.isalnum()
            for c in password1
        ):

            messages.error(
                request,
                "Password must contain at least one special character."
            )

            return redirect("signup")

        # =================================================
        # CHECK COLLEGE ID USER
        # =================================================

        existing_college_user = (
            User.objects.filter(
                username__iexact=college_id
            ).first()
        )

        # =================================================
        # EXISTING USER
        # =================================================

        if existing_college_user:

            # -------------------------------------------------
            # ALREADY ACTIVATED
            # -------------------------------------------------

            if existing_college_user.is_active:

                messages.error(
                    request,
                    "This College ID is already registered and activated. Please login."
                )

                return redirect("login")

            # -------------------------------------------------
            # EXISTING INACTIVE USER
            #
            # This normally means:
            # previous OTP expired.
            #
            # DO NOT CREATE ANOTHER USER.
            # SEND A NEW OTP.
            # -------------------------------------------------

            if (
                existing_college_user.email.lower()
                != email.lower()
            ):

                messages.error(
                    request,
                    "This College ID is already registered with another email address."
                )

                return redirect("signup")

            # -------------------------------------------------
            # GET PROFILE
            # -------------------------------------------------

            try:

                existing_profile = (
                    existing_college_user.userprofile
                )

            except UserProfile.DoesNotExist:

                existing_college_user.delete()

                existing_college_user = None

            else:

                # -------------------------------------------------
                # CHECK DEPARTMENT
                # -------------------------------------------------

                if (
                    existing_profile.department
                    != department
                ):

                    messages.error(
                        request,
                        "The selected department does not match your existing registration."
                    )

                    return redirect("signup")

                # -------------------------------------------------
                # CHECK ROLE
                # -------------------------------------------------

                if (
                    existing_profile.role
                    != role
                ):

                    messages.error(
                        request,
                        "The selected account type does not match your existing registration."
                    )

                    return redirect("signup")

                # -------------------------------------------------
                # UPDATE PASSWORD
                # -------------------------------------------------

                existing_college_user.set_password(
                    password1
                )

                existing_college_user.save(
                    update_fields=[
                        "password"
                    ]
                )

                # -------------------------------------------------
                # SAVE SIGNUP SESSION
                # -------------------------------------------------

                request.session[
                    "signup_college_id"
                ] = college_id

                request.session[
                    "signup_user_id"
                ] = existing_college_user.id

                # -------------------------------------------------
                # GENERATE NEW OTP
                # -------------------------------------------------

                otp = generate_otp()

                save_otp_in_session(
                    request,
                    otp,
                    email,
                    "signup"
                )

                # -------------------------------------------------
                # SEND NEW OTP
                # -------------------------------------------------

                try:

                    send_otp_email(
                        email,
                        otp,
                        "verification"
                    )

                except Exception:

                    clear_otp_from_session(
                        request,
                        "signup"
                    )

                    request.session.pop(
                        "signup_college_id",
                        None
                    )

                    request.session.pop(
                        "signup_user_id",
                        None
                    )

                    messages.error(
                        request,
                        "We could not send the verification OTP. Please try again."
                    )

                    return redirect("signup")

                messages.success(
                    request,
                    "Your previous OTP expired. A new verification OTP has been sent to your email."
                )

                return redirect(
                    "verify_signup_otp"
                )

        # =================================================
        # EMAIL DUPLICATE CHECK
        # =================================================

        existing_email_user = (
            User.objects.filter(
                email__iexact=email
            ).first()
        )

        if existing_email_user:

            messages.error(
                request,
                "This email address is already registered. Please login or use Forgot Password."
            )

            return redirect("signup")

        # =================================================
        # APPROVED ID USED CHECK
        # =================================================

        if approved_id.is_used:

            messages.error(
                request,
                "This College ID has already been used for registration."
            )

            return redirect("login")

        # =================================================
        # CREATE USER
        # =================================================

        user = User.objects.create_user(
            username=college_id,
            email=email,
            password=password1,
            is_active=False,
        )

        # =================================================
        # CREATE USER PROFILE
        # =================================================

        UserProfile.objects.create(
            user=user,
            role=role,
            department=department,
        )

        # =================================================
        # SAVE SIGNUP SESSION
        # =================================================

        request.session[
            "signup_college_id"
        ] = college_id

        request.session[
            "signup_user_id"
        ] = user.id

        # =================================================
        # GENERATE OTP
        # =================================================

        otp = generate_otp()

        save_otp_in_session(
            request,
            otp,
            email,
            "signup"
        )

        # =================================================
        # SEND OTP
        # =================================================

        try:

            send_otp_email(
                email,
                otp,
                "verification"
            )

        except Exception:

            user_profile = getattr(
                user,
                "userprofile",
                None
            )

            if user_profile:

                user_profile.delete()

            user.delete()

            clear_otp_from_session(
                request,
                "signup"
            )

            request.session.pop(
                "signup_college_id",
                None
            )

            request.session.pop(
                "signup_user_id",
                None
            )

            messages.error(
                request,
                "We could not send the verification OTP. Please check your email settings and try again."
            )

            return redirect("signup")

        # =================================================
        # IMPORTANT
        #
        # ApprovedID.is_used remains FALSE.
        #
        # It becomes TRUE only after successful OTP.
        # =================================================

        messages.success(
            request,
            "Registration successful! A verification OTP has been sent to your email."
        )

        return redirect(
            "verify_signup_otp"
        )

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "complaints/signup.html"
    )


# =========================================================
# VERIFY SIGNUP OTP
# =========================================================

def verify_signup_otp(request):

    otp, email, created_at = (
        get_otp_from_session(
            request,
            "signup"
        )
    )

    college_id = request.session.get(
        "signup_college_id"
    )

    user_id = request.session.get(
        "signup_user_id"
    )

    # =====================================================
    # SESSION CHECK
    # =====================================================

    if (
        not otp
        or not email
        or not created_at
        or not college_id
        or not user_id
    ):

        messages.error(
            request,
            "Your verification session has expired. Please sign up again."
        )

        return redirect("signup")

    # =====================================================
    # OTP EXPIRY
    # =====================================================

    if is_otp_expired(created_at):

        # Keep signup identity information.
        # This allows RESEND OTP.

        clear_otp_from_session(
            request,
            "signup"
        )

        messages.error(
            request,
            "Your OTP has expired. Please click 'Resend OTP' to receive a new OTP."
        )

        return render(
            request,
            "complaints/verify_signup_otp.html",
            {
                "email": email,
                "otp_expired": True,
            }
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        entered_otp = request.POST.get(
            "otp",
            ""
        ).strip()

        # -------------------------------------------------
        # EMPTY OTP
        # -------------------------------------------------

        if not entered_otp:

            messages.error(
                request,
                "Please enter the OTP."
            )

            return render(
                request,
                "complaints/verify_signup_otp.html",
                {
                    "email": email
                }
            )

        # -------------------------------------------------
        # OTP FORMAT
        # -------------------------------------------------

        if not re.fullmatch(
            r"\d{6}",
            entered_otp
        ):

            messages.error(
                request,
                "OTP must contain exactly 6 digits."
            )

            return render(
                request,
                "complaints/verify_signup_otp.html",
                {
                    "email": email
                }
            )

        # -------------------------------------------------
        # OTP MATCH
        # -------------------------------------------------

        if not secrets.compare_digest(
            entered_otp,
            otp
        ):

            messages.error(
                request,
                "Invalid OTP. Please enter the correct OTP."
            )

            return render(
                request,
                "complaints/verify_signup_otp.html",
                {
                    "email": email
                }
            )

        # =================================================
        # FIND USER
        # =================================================

        user = User.objects.filter(
            id=user_id,
            username__iexact=college_id,
            email__iexact=email,
        ).first()

        if user is None:

            messages.error(
                request,
                "Account not found. Please sign up again."
            )

            clear_otp_from_session(
                request,
                "signup"
            )

            request.session.pop(
                "signup_college_id",
                None
            )

            request.session.pop(
                "signup_user_id",
                None
            )

            return redirect("signup")

        # =================================================
        # ACTIVATE USER
        # =================================================

        user.is_active = True

        user.save(
            update_fields=[
                "is_active"
            ]
        )

        # =================================================
        # MARK APPROVED ID USED
        # =================================================

        approved_id = (
            ApprovedID.objects.filter(
                college_id=college_id
            ).first()
        )

        if approved_id:

            approved_id.is_used = True

            approved_id.save(
                update_fields=[
                    "is_used"
                ]
            )

        # =================================================
        # CLEAR SIGNUP SESSION
        # =================================================

        clear_otp_from_session(
            request,
            "signup"
        )

        request.session.pop(
            "signup_college_id",
            None
        )

        request.session.pop(
            "signup_user_id",
            None
        )

        # =================================================
        # SUCCESS
        # =================================================

        messages.success(
            request,
            "Email verified successfully! Your account is now activated. Please login."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "complaints/verify_signup_otp.html",
        {
            "email": email
        }
    )


# =========================================================
# RESEND SIGNUP OTP
# =========================================================

def resend_signup_otp(request):

    email = request.session.get(
        "signup_email"
    )

    college_id = request.session.get(
        "signup_college_id"
    )

    user_id = request.session.get(
        "signup_user_id"
    )

    # =====================================================
    # SESSION CHECK
    # =====================================================

    if (
        not email
        or not college_id
        or not user_id
    ):

        messages.error(
            request,
            "Your verification session has expired. Please sign up again."
        )

        return redirect("signup")

    # =====================================================
    # FIND USER
    # =====================================================

    user = User.objects.filter(
        id=user_id,
        username__iexact=college_id,
        email__iexact=email,
        is_active=False,
    ).first()

    if user is None:

        messages.error(
            request,
            "Account not found or already activated."
        )

        return redirect("login")

    # =====================================================
    # APPROVED ID
    # =====================================================

    approved_id = (
        ApprovedID.objects.filter(
            college_id=college_id
        ).first()
    )

    if approved_id is None:

        messages.error(
            request,
            "Approved College ID not found."
        )

        return redirect("signup")

    if approved_id.is_used:

        messages.error(
            request,
            "This College ID has already been used."
        )

        return redirect("login")

    # =====================================================
    # GENERATE NEW OTP
    # =====================================================

    otp = generate_otp()

    save_otp_in_session(
        request,
        otp,
        email,
        "signup"
    )

    # =====================================================
    # SEND OTP
    # =====================================================

    try:

        send_otp_email(
            email,
            otp,
            "verification"
        )

    except Exception:

        messages.error(
            request,
            "We could not send the new OTP. Please try again."
        )

        return redirect(
            "verify_signup_otp"
        )

    messages.success(
        request,
        "A new verification OTP has been sent to your email."
    )

    return redirect(
        "verify_signup_otp"
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip().upper()

        password = request.POST.get(
            "password",
            ""
        )


        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not username or not password:

            messages.error(
                request,
                "Please enter your College ID and password."
            )

            return render(
                request,
                "complaints/login.html"
            )

        # =================================================
        # FIND USER
        # =================================================

        existing_user = (
            User.objects.filter(
                username__iexact=username
            ).first()
        )

        # =================================================
        # INACTIVE USER
        # =================================================

        if existing_user:

            if not existing_user.is_active:

                messages.error(
                    request,
                    "Your account is not activated. Please complete email OTP verification before logging in."
                )

                return render(
                    request,
                    "complaints/login.html"
                )

        # =================================================
        # AUTHENTICATE
        # =================================================

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # =================================================
            # ACTIVE CHECK
            # =================================================

            if not user.is_active:

                messages.error(
                    request,
                    "Your account is not activated. Please verify your email using OTP."
                )

                return redirect(
                    "login"
                )

            # =================================================
            # PROFILE
            # =================================================

            try:

                profile = user.userprofile

            except UserProfile.DoesNotExist:

                logout(request)

                messages.error(
                    request,
                    "User profile not found. Please contact the administrator."
                )

                return redirect(
                    "login"
                )

            # =================================================
            # LOGIN
            # =================================================

            login(
                request,
                user
            )

            # =================================================
            # ROLE
            # =================================================

            if profile.role == "student":

                return redirect(
                    "student_dashboard"
                )

            if profile.role == "staff":

                return redirect(
                    "staff_dashboard"
                )

            logout(request)

            messages.error(
                request,
                "Invalid account role."
            )

            return redirect(
                "login"
            )

        # =================================================
        # INVALID LOGIN
        # =================================================

        messages.error(
            request,
            "Invalid College ID or password."
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
        "You have been logged out successfully."
    )

    return redirect(
        "login"
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password(request):

    if request.method == "POST":

        identifier = request.POST.get(
            "identifier",
            ""
        ).strip()

        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not identifier:

            messages.error(
                request,
                "Please enter your College ID or registered email."
            )

            return redirect(
                "forgot_password"
            )

        # =================================================
        # FIND BY COLLEGE ID
        # =================================================

        user = User.objects.filter(
            username__iexact=identifier
        ).first()

        # =================================================
        # FIND BY EMAIL
        # =================================================

        if user is None:

            user = User.objects.filter(
                email__iexact=identifier
            ).first()

        # =================================================
        # NOT FOUND
        # =================================================

        if user is None:

            messages.error(
                request,
                "No account was found with that College ID or email."
            )

            return redirect(
                "forgot_password"
            )

        # =================================================
        # ACTIVE CHECK
        # =================================================

        if not user.is_active:

            messages.error(
                request,
                "Your account is not activated. Please complete email verification first."
            )

            return redirect(
                "login"
            )

        # =================================================
        # EMAIL CHECK
        # =================================================

        if not user.email:

            messages.error(
                request,
                "No email address is associated with this account."
            )

            return redirect(
                "forgot_password"
            )

        # =================================================
        # GENERATE OTP
        # =================================================

        otp = generate_otp()

        save_otp_in_session(
            request,
            otp,
            user.email,
            "password_reset"
        )

        request.session[
            "password_reset_user_id"
        ] = user.id

        request.session[
            "password_reset_verified"
        ] = False

        # =================================================
        # SEND OTP
        # =================================================

        try:

            send_otp_email(
                user.email,
                otp,
                "password_reset"
            )

        except Exception:

            clear_otp_from_session(
                request,
                "password_reset"
            )

            request.session.pop(
                "password_reset_user_id",
                None
            )

            request.session.pop(
                "password_reset_verified",
                None
            )

            messages.error(
                request,
                "We could not send the password reset OTP. Please try again."
            )

            return redirect(
                "forgot_password"
            )

        messages.success(
            request,
            "Password reset OTP has been sent to your registered email."
        )

        return redirect(
            "verify_password_otp"
        )

    return render(
        request,
        "complaints/forgot_password.html"
    )


# =========================================================
# VERIFY PASSWORD OTP
# =========================================================

def verify_password_otp(request):

    otp, email, created_at = (
        get_otp_from_session(
            request,
            "password_reset"
        )
    )

    user_id = request.session.get(
        "password_reset_user_id"
    )

    # =====================================================
    # SESSION CHECK
    # =====================================================

    if (
        not otp
        or not email
        or not created_at
        or not user_id
    ):

        messages.error(
            request,
            "Your password reset session has expired. Please request a new OTP."
        )

        return redirect(
            "forgot_password"
        )

    # =====================================================
    # OTP EXPIRY
    # =====================================================

    if is_otp_expired(created_at):

        clear_otp_from_session(
            request,
            "password_reset"
        )

        messages.error(
            request,
            "OTP has expired. Please click 'Resend OTP' to receive a new OTP."
        )

        return render(
            request,
            "complaints/verify_password_otp.html",
            {
                "email": email,
                "otp_expired": True,
            }
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        entered_otp = request.POST.get(
            "otp",
            ""
        ).strip()

        # -------------------------------------------------
        # EMPTY
        # -------------------------------------------------

        if not entered_otp:

            messages.error(
                request,
                "Please enter the OTP."
            )

            return render(
                request,
                "complaints/verify_password_otp.html",
                {
                    "email": email
                }
            )

        # -------------------------------------------------
        # FORMAT
        # -------------------------------------------------

        if not re.fullmatch(
            r"\d{6}",
            entered_otp
        ):

            messages.error(
                request,
                "OTP must contain exactly 6 digits."
            )

            return render(
                request,
                "complaints/verify_password_otp.html",
                {
                    "email": email
                }
            )

        # -------------------------------------------------
        # MATCH
        # -------------------------------------------------

        if not secrets.compare_digest(
            entered_otp,
            otp
        ):

            messages.error(
                request,
                "Invalid OTP. Please enter the correct OTP."
            )

            return render(
                request,
                "complaints/verify_password_otp.html",
                {
                    "email": email
                }
            )

        # =================================================
        # USER CHECK
        # =================================================

        user = User.objects.filter(
            id=user_id,
            email__iexact=email,
            is_active=True,
        ).first()

        if user is None:

            messages.error(
                request,
                "Account not found."
            )

            clear_otp_from_session(
                request,
                "password_reset"
            )

            request.session.pop(
                "password_reset_user_id",
                None
            )

            return redirect(
                "forgot_password"
            )

        # =================================================
        # OTP VERIFIED
        # =================================================

        request.session[
            "password_reset_verified"
        ] = True

        clear_otp_from_session(
            request,
            "password_reset"
        )

        messages.success(
            request,
            "OTP verified successfully. Please create your new password."
        )

        return redirect(
            "reset_password"
        )

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "complaints/verify_password_otp.html",
        {
            "email": email
        }
    )


# =========================================================
# RESEND PASSWORD OTP
# =========================================================

def resend_password_otp(request):

    user_id = request.session.get(
        "password_reset_user_id"
    )

    # =====================================================
    # SESSION CHECK
    # =====================================================

    if not user_id:

        messages.error(
            request,
            "Your password reset session has expired. Please start again."
        )

        return redirect(
            "forgot_password"
        )

    # =====================================================
    # FIND USER
    # =====================================================

    user = User.objects.filter(
        id=user_id,
        is_active=True
    ).first()

    if user is None:

        messages.error(
            request,
            "Account not found."
        )

        return redirect(
            "forgot_password"
        )

    # =====================================================
    # EMAIL CHECK
    # =====================================================

    if not user.email:

        messages.error(
            request,
            "No email address is associated with this account."
        )

        return redirect(
            "forgot_password"
        )

    # =====================================================
    # NEW OTP
    # =====================================================

    otp = generate_otp()

    save_otp_in_session(
        request,
        otp,
        user.email,
        "password_reset"
    )

    request.session[
        "password_reset_verified"
    ] = False

    # =====================================================
    # SEND
    # =====================================================

    try:

        send_otp_email(
            user.email,
            otp,
            "password_reset"
        )

    except Exception:

        messages.error(
            request,
            "We could not send the new OTP. Please try again."
        )

        return redirect(
            "verify_password_otp"
        )

    messages.success(
        request,
        "A new password reset OTP has been sent to your email."
    )

    return redirect(
        "verify_password_otp"
    )


# =========================================================
# RESET PASSWORD
# =========================================================

def reset_password(request):

    verified = request.session.get(
        "password_reset_verified",
        False
    )

    user_id = request.session.get(
        "password_reset_user_id"
    )

    # =====================================================
    # SECURITY CHECK
    # =====================================================

    if not verified or not user_id:

        messages.error(
            request,
            "Please verify the OTP first."
        )

        return redirect(
            "forgot_password"
        )

    # =====================================================
    # FIND USER
    # =====================================================

    user = User.objects.filter(
        id=user_id,
        is_active=True
    ).first()

    if user is None:

        messages.error(
            request,
            "Account not found."
        )

        return redirect(
            "forgot_password"
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        password1 = request.POST.get(
            "password1",
            ""
        )

        password2 = request.POST.get(
            "password2",
            ""
        )

        # -------------------------------------------------
        # MATCH
        # -------------------------------------------------

        if password1 != password2:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "complaints/reset_password.html"
            )

        # -------------------------------------------------
        # LENGTH
        # -------------------------------------------------

        if len(password1) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

            return render(
                request,
                "complaints/reset_password.html"
            )

        # -------------------------------------------------
        # LETTER
        # -------------------------------------------------

        if not any(
            c.isalpha()
            for c in password1
        ):

            messages.error(
                request,
                "Password must contain at least one letter."
            )

            return render(
                request,
                "complaints/reset_password.html"
            )

        # -------------------------------------------------
        # NUMBER
        # -------------------------------------------------

        if not any(
            c.isdigit()
            for c in password1
        ):

            messages.error(
                request,
                "Password must contain at least one number."
            )

            return render(
                request,
                "complaints/reset_password.html"
            )

        # -------------------------------------------------
        # SPECIAL CHARACTER
        # -------------------------------------------------

        if not any(
            not c.isalnum()
            for c in password1
        ):

            messages.error(
                request,
                "Password must contain at least one special character."
            )

            return render(
                request,
                "complaints/reset_password.html"
            )

        # =================================================
        # SAVE PASSWORD
        # =================================================

        user.set_password(
            password1
        )

        user.save(
            update_fields=[
                "password"
            ]
        )

        # =================================================
        # CLEAR SESSION
        # =================================================

        request.session.pop(
            "password_reset_user_id",
            None
        )

        request.session.pop(
            "password_reset_verified",
            None
        )

        clear_otp_from_session(
            request,
            "password_reset"
        )

        # =================================================
        # SUCCESS
        # =================================================

        messages.success(
            request,
            "Password changed successfully! You can now login with your new password."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "complaints/reset_password.html"
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@login_required
def student_dashboard(request):

    # =====================================================
    # EXTRA ACTIVE CHECK
    # =====================================================

    if not request.user.is_active:

        logout(request)

        messages.error(
            request,
            "Your account is not activated."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # PROFILE
    # =====================================================

    try:

        user_profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # ROLE
    # =====================================================

    if user_profile.role != "student":

        messages.error(
            request,
            "Access denied."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # COMPLAINTS
    # =====================================================

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

    if not request.user.is_active:

        logout(request)

        return redirect(
            "login"
        )

    # =====================================================
    # PROFILE
    # =====================================================

    try:

        user_profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # STUDENT ONLY
    # =====================================================

    if user_profile.role != "student":

        messages.error(
            request,
            "Only students can submit complaints."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # POST
    # =====================================================

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
def student_view_complaint(
    request,
    complaint_id
):

    if not request.user.is_active:

        logout(request)

        return redirect(
            "login"
        )

    # =====================================================
    # PROFILE
    # =====================================================

    try:

        profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # STUDENT ONLY
    # =====================================================

    if profile.role != "student":

        messages.error(
            request,
            "Access denied."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # OWN COMPLAINT ONLY
    # =====================================================

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
# STUDENT DELETE COMPLAINT
# =========================================================

@login_required
def delete_complaint(
    request,
    complaint_id
):

    if not request.user.is_active:

        logout(request)

        return redirect(
            "login"
        )

    # =====================================================
    # PROFILE
    # =====================================================

    try:

        profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # STUDENT ONLY
    # =====================================================

    if profile.role != "student":

        messages.error(
            request,
            "Access denied."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # OWN COMPLAINT
    # =====================================================

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

    # =====================================================
    # POST ONLY
    # =====================================================

    if request.method == "POST":

        complaint.delete()

        messages.success(
            request,
            "Complaint deleted successfully."
        )

    else:

        messages.error(
            request,
            "Invalid delete request."
        )

    return redirect(
        "student_dashboard"
    )


# =========================================================
# STUDENT FEEDBACK
# =========================================================

@login_required
def submit_feedback(
    request,
    complaint_id
):

    if not request.user.is_active:

        logout(request)

        return redirect(
            "login"
        )

    # =====================================================
    # PROFILE
    # =====================================================

    try:

        profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # STUDENT ONLY
    # =====================================================

    if profile.role != "student":

        messages.error(
            request,
            "Access denied."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # OWN COMPLAINT
    # =====================================================

    complaint = get_object_or_404(
        Complaint,
        id=complaint_id,
        student=request.user
    )

    # =====================================================
    # RESOLVED CHECK
    # =====================================================

    if complaint.status != "Resolved":

        messages.error(
            request,
            "Feedback can only be submitted after the complaint is resolved."
        )

        return redirect(
            "student_view_complaint",
            complaint_id=complaint.id
        )

    # =====================================================
    # ALREADY SUBMITTED
    # =====================================================

    if (
        complaint.feedback_rating is not None
        or complaint.feedback
    ):

        messages.info(
            request,
            "Feedback has already been submitted."
        )

        return redirect(
            "student_view_complaint",
            complaint_id=complaint.id
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        form = FeedbackForm(
            request.POST
        )

        if form.is_valid():

            complaint.feedback_rating = (
                form.cleaned_data[
                    "feedback_rating"
                ]
            )

            complaint.feedback = (
                form.cleaned_data[
                    "feedback"
                ]
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

    if not request.user.is_active:

        logout(request)

        messages.error(
            request,
            "Your account is not activated."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # PROFILE
    # =====================================================

    try:

        user_profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # STAFF ONLY
    # =====================================================

    if user_profile.role != "staff":

        messages.error(
            request,
            "Only staff members can access this page."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # DEPARTMENT COMPLAINTS
    # =====================================================

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


# =========================================================
# STAFF VIEW COMPLAINT / REPLY
# =========================================================

@login_required
def staff_view_complaint(
    request,
    complaint_id
):

    if not request.user.is_active:

        logout(request)

        return redirect(
            "login"
        )

    # =====================================================
    # PROFILE
    # =====================================================

    try:

        profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # STAFF ONLY
    # =====================================================

    if profile.role != "staff":

        messages.error(
            request,
            "Access denied."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # FIND COMPLAINT
    # =====================================================

    complaint = get_object_or_404(
        Complaint,
        id=complaint_id
    )

    # =====================================================
    # DEPARTMENT SECURITY
    # =====================================================

    if complaint.department != profile.department:

        messages.error(
            request,
            "You can only manage complaints from your department."
        )

        return redirect(
            "staff_dashboard"
        )

    # =====================================================
    # POST REPLY
    # =====================================================

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
    )


# =========================================================
# OLD REPLY URL COMPATIBILITY
# =========================================================

@login_required
def reply_to_complaint(
    request,
    complaint_id
):

    return staff_view_complaint(
        request,
        complaint_id
    )


# =========================================================
# STAFF DELETE COMPLAINT
# =========================================================

@login_required
def staff_delete_complaint(
    request,
    complaint_id
):

    if not request.user.is_active:

        logout(request)

        return redirect(
            "login"
        )

    # =====================================================
    # PROFILE
    # =====================================================

    try:

        profile = request.user.userprofile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            "User profile not found."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # STAFF ONLY
    # =====================================================

    if profile.role != "staff":

        messages.error(
            request,
            "Only staff members can delete complaints."
        )

        return redirect(
            "login"
        )

    # =====================================================
    # FIND COMPLAINT
    # =====================================================

    complaint = Complaint.objects.filter(
        id=complaint_id
    ).first()

    if complaint is None:

        messages.error(
            request,
            "Complaint not found."
        )

        return redirect(
            "staff_dashboard"
        )

    # =====================================================
    # DEPARTMENT SECURITY
    # =====================================================

    if complaint.department != profile.department:

        messages.error(
            request,
            "You can only delete complaints from your department."
        )

        return redirect(
            "staff_dashboard"
        )

    # =====================================================
    # POST ONLY
    # =====================================================

    if request.method == "POST":

        complaint.delete()

        messages.success(
            request,
            "Complaint deleted successfully."
        )

    else:

        messages.error(
            request,
            "Invalid delete request."
        )

    return redirect(
        "staff_dashboard"
    )


# =========================================================
# PROFILE
# =========================================================

@login_required
def profile_view(request):

    if not request.user.is_active:

        logout(request)

        return redirect(
            "login"
        )

    # =====================================================
    # GET OR CREATE PROFILE
    # =====================================================

    user_profile, created = (
        UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "role": "student",
                "department": "CSE",
            }
        )
    )

    # =====================================================
    # PROFILE PHOTO
    # =====================================================

    if (
        request.method == "POST"
        and request.FILES.get(
            "profile_picture"
        )
    ):

        user_profile.profile_picture = (
            request.FILES[
                "profile_picture"
            ]
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

    # =====================================================
    # PROFILE DETAILS
    # =====================================================

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