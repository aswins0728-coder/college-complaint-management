from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Complaint, UserProfile
from .serializers import ComplaintSerializer, UserProfileSerializer


# =========================================================
# API LOGIN
# =========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def api_login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {
                "success": False,
                "message": "Username and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {
                "success": False,
                "message": "Invalid username or password."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {
                "success": False,
                "message": "Your account is not active."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    token, created = Token.objects.get_or_create(user=user)

    return Response(
        {
            "success": True,
            "message": "Login successful.",
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# API LOGOUT
# =========================================================

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_logout(request):

    try:
        request.auth.delete()
    except Exception:
        pass

    return Response(
        {
            "success": True,
            "message": "Logout successful."
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# CURRENT USER PROFILE
# =========================================================

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_profile(request):

    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "User profile not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserProfileSerializer(profile)

    return Response(
        {
            "success": True,
            "profile": serializer.data
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# COMPLAINT LIST
# =========================================================

@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_complaints(request):

    # -----------------------------------------------------
    # GET COMPLAINTS
    # -----------------------------------------------------

    if request.method == "GET":

        if hasattr(request.user, "userprofile"):
            profile = request.user.userprofile

            if profile.role == "staff":
                complaints = Complaint.objects.filter(
                    department=profile.department
                ).order_by("-created_at")
            else:
                complaints = Complaint.objects.filter(
                    student=request.user
                ).order_by("-created_at")
        else:
            complaints = Complaint.objects.filter(
                student=request.user
            ).order_by("-created_at")

        serializer = ComplaintSerializer(
            complaints,
            many=True,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": complaints.count(),
                "complaints": serializer.data
            },
            status=status.HTTP_200_OK
        )

    # -----------------------------------------------------
    # CREATE COMPLAINT
    # -----------------------------------------------------

    if request.method == "POST":

        if not hasattr(request.user, "userprofile"):
            return Response(
                {
                    "success": False,
                    "message": "User profile not found."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = request.user.userprofile

        if profile.role != "student":
            return Response(
                {
                    "success": False,
                    "message": "Only students can submit complaints."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ComplaintSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            complaint = serializer.save(
                student=request.user
            )

            return Response(
                {
                    "success": True,
                    "message": "Complaint submitted successfully.",
                    "complaint": ComplaintSerializer(
                        complaint,
                        context={"request": request}
                    ).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================================================
# SINGLE COMPLAINT
# =========================================================

@api_view(["GET", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_complaint_detail(request, complaint_id):

    try:
        complaint = Complaint.objects.get(
            id=complaint_id
        )
    except Complaint.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Complaint not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # -----------------------------------------------------
    # CHECK ACCESS
    # -----------------------------------------------------

    if hasattr(request.user, "userprofile"):
        profile = request.user.userprofile

        if profile.role == "staff":

            if complaint.department != profile.department:
                return Response(
                    {
                        "success": False,
                        "message": "You cannot access this complaint."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        else:

            if complaint.student != request.user:
                return Response(
                    {
                        "success": False,
                        "message": "You cannot access this complaint."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

    else:

        if complaint.student != request.user:
            return Response(
                {
                    "success": False,
                    "message": "You cannot access this complaint."
                },
                status=status.HTTP_403_FORBIDDEN
            )

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    if request.method == "GET":

        serializer = ComplaintSerializer(
            complaint,
            context={"request": request}
        )

        return Response(
            {
                "success": True,
                "complaint": serializer.data
            },
            status=status.HTTP_200_OK
        )

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------

    if request.method == "DELETE":

        if complaint.student != request.user:
            return Response(
                {
                    "success": False,
                    "message": "Only the complaint owner can delete it."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if complaint.status == "Resolved":
            return Response(
                {
                    "success": False,
                    "message": "Resolved complaints cannot be deleted."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        complaint.delete()

        return Response(
            {
                "success": True,
                "message": "Complaint deleted successfully."
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# STAFF REPLY
# =========================================================

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_reply(request, complaint_id):

    if not hasattr(request.user, "userprofile"):
        return Response(
            {
                "success": False,
                "message": "User profile not found."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    profile = request.user.userprofile

    if profile.role != "staff":
        return Response(
            {
                "success": False,
                "message": "Only staff members can reply."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        complaint = Complaint.objects.get(
            id=complaint_id
        )
    except Complaint.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Complaint not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if complaint.department != profile.department:
        return Response(
            {
                "success": False,
                "message": "You cannot reply to complaints from another department."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    reply = request.data.get("reply", "").strip()

    if not reply:
        return Response(
            {
                "success": False,
                "message": "Reply is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    complaint.reply = reply
    complaint.status = "Resolved"
    complaint.save(
        update_fields=["reply", "status"]
    )

    return Response(
        {
            "success": True,
            "message": "Reply submitted and complaint marked as resolved.",
            "complaint": ComplaintSerializer(
                complaint,
                context={"request": request}
            ).data
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# STUDENT FEEDBACK
# =========================================================

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_feedback(request, complaint_id):

    try:
        complaint = Complaint.objects.get(
            id=complaint_id
        )
    except Complaint.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Complaint not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if complaint.student != request.user:
        return Response(
            {
                "success": False,
                "message": "You can only give feedback for your own complaint."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    if complaint.status != "Resolved":
        return Response(
            {
                "success": False,
                "message": "Feedback can be submitted only after the complaint is resolved."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    feedback = request.data.get("feedback", "").strip()
    rating = request.data.get("feedback_rating")

    if not feedback:
        return Response(
            {
                "success": False,
                "message": "Feedback is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return Response(
            {
                "success": False,
                "message": "Rating must be between 1 and 5."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if rating < 1 or rating > 5:
        return Response(
            {
                "success": False,
                "message": "Rating must be between 1 and 5."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    complaint.feedback = feedback
    complaint.feedback_rating = rating
    complaint.feedback_submitted_at = timezone.now()

    complaint.save(
        update_fields=[
            "feedback",
            "feedback_rating",
            "feedback_submitted_at"
        ]
    )

    return Response(
        {
            "success": True,
            "message": "Feedback submitted successfully.",
            "complaint": ComplaintSerializer(
                complaint,
                context={"request": request}
            ).data
        },
        status=status.HTTP_200_OK
    )