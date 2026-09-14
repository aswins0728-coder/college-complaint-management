from django.urls import path

from . import api_views


urlpatterns = [

    # Authentication
    path(
        "login/",
        api_views.api_login,
        name="api_login"
    ),

    path(
        "logout/",
        api_views.api_logout,
        name="api_logout"
    ),

    # Profile
    path(
        "profile/",
        api_views.api_profile,
        name="api_profile"
    ),

    # Complaints
    path(
        "complaints/",
        api_views.api_complaints,
        name="api_complaints"
    ),

    path(
        "complaints/<int:complaint_id>/",
        api_views.api_complaint_detail,
        name="api_complaint_detail"
    ),

    # Staff reply
    path(
        "complaints/<int:complaint_id>/reply/",
        api_views.api_reply,
        name="api_reply"
    ),

    # Student feedback
    path(
        "complaints/<int:complaint_id>/feedback/",
        api_views.api_feedback,
        name="api_feedback"
    ),
]