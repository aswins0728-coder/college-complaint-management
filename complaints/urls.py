from django.urls import include, path

from . import views


urlpatterns = [

    # =====================================================
    # API
    # =====================================================

    path(
        "api/",
        include("complaints.api_urls")
    ),


    # =====================================================
    # AUTHENTICATION
    # =====================================================

    path(
        "",
        views.signup_view,
        name="signup"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),


    # =====================================================
    # SIGNUP OTP
    # =====================================================

    path(
        "verify-signup-otp/",
        views.verify_signup_otp,
        name="verify_signup_otp"
    ),

    path(
        "resend-signup-otp/",
        views.resend_signup_otp,
        name="resend_signup_otp"
    ),


    # =====================================================
    # FORGOT PASSWORD / PASSWORD RESET OTP
    # =====================================================

    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password"
    ),

    path(
        "verify-password-otp/",
        views.verify_password_otp,
        name="verify_password_otp"
    ),

    path(
        "resend-password-otp/",
        views.resend_password_otp,
        name="resend_password_otp"
    ),

    path(
        "reset-password/",
        views.reset_password,
        name="reset_password"
    ),


    # =====================================================
    # STUDENT
    # =====================================================

    path(
        "student/dashboard/",
        views.student_dashboard,
        name="student_dashboard"
    ),

    path(
        "profile/",
        views.profile_view,
        name="student_profile"
    ),

    path(
        "student/submit/",
        views.submit_complaint,
        name="submit_complaint"
    ),

    path(
        "my-complaints/",
        views.student_dashboard,
        name="my_complaints"
    ),

    path(
        "student/view-complaint/<int:complaint_id>/",
        views.student_view_complaint,
        name="student_view_complaint"
    ),

    path(
        "student/delete-complaint/<int:complaint_id>/",
        views.delete_complaint,
        name="delete_complaint"
    ),

    path(
        "student/feedback/<int:complaint_id>/",
        views.submit_feedback,
        name="submit_feedback"
    ),


    # =====================================================
    # STAFF
    # =====================================================

    path(
        "staff/dashboard/",
        views.staff_dashboard,
        name="staff_dashboard"
    ),

    path(
        "staff/view-complaint/<int:complaint_id>/",
        views.staff_view_complaint,
        name="staff_view_complaint"
    ),

    path(
        "staff/reply/<int:complaint_id>/",
        views.reply_to_complaint,
        name="reply_complaint"
    ),

    path(
        "staff/delete-complaint/<int:complaint_id>/",
        views.staff_delete_complaint,
        name="staff_delete_complaint"
    ),

    path(
        "view-all-complaints/",
        views.staff_dashboard,
        name="view_all_complaints"
    ),

]