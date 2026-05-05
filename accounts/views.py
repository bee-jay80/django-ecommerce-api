from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import User, ProfilePicture
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer, ProfilePictureSerializer
# jwt
import jwt
from django.conf import settings

# from accounts.utils.emails import send_otp_email_task
from accounts.utils.otp import generate_send_otp, verify_otp
from accounts.utils.handle_cookie import set_session_cookie, set_access_refresh_token
from rest_framework import permissions


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        generate_send_otp(user)
        response = Response({"message": "User registered successfully. Please check your email for the OTP."}, status=status.HTTP_201_CREATED)
        # Setting a cookie here has no effect because DRF builds the final Response.
        # Return the response from `create()` instead so the cookie is included.
        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        generate_send_otp(user)
        response = Response({"message": "User registered successfully. Please check your email for the OTP."}, status=status.HTTP_201_CREATED)
        return set_session_cookie(response, user.id)


class VerifyOTPView(APIView):
    def post(self, request):
        otp = request.data.get("otp")

        # get jwt token for the user
        user_id = request.COOKIES.get("session_token")
        if not user_id:
            return Response({"error": "Session token missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = jwt.decode(user_id, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get("user_id")
            user = User.objects.get(id=user_id)
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            return Response({"error": "Invalid session token"}, status=status.HTTP_400_BAD_REQUEST)
        
        if verify_otp(user, otp):
            user.is_verified = True
            user.is_active = True
            user.is_email_verified = True
            user.save()

            ProfilePicture.objects.create(user=user)  # Create default profile picture record
            return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_verified:
            # Resend OTP if user is not verified
            generate_send_otp(user)
            # Set a cookie with the user ID for OTP verification
            response = Response({"message": "User is not verified. A new OTP has been sent to your email."}, status=status.HTTP_400_BAD_REQUEST)
            return set_session_cookie(response, user.id)
        
        response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return set_access_refresh_token(response, user)


class ProfilePictureView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        # If the user already has a profile picture, update it instead of creating a new one
        existing = ProfilePicture.objects.filter(user=request.user).first()
        if existing:
            serializer = ProfilePictureSerializer(existing, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({"message": "Profile picture updated successfully"}, status=status.HTTP_200_OK)

        # No existing picture — create one
        serializer = ProfilePictureSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save(user=request.user)
        except Exception as exc:
            # Catch DB integrity errors and return structured JSON
            return Response({"error": "Could not save profile picture", "details": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Profile picture uploaded successfully"}, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        profile_picture = ProfilePicture.objects.filter(user=request.user).first()
        if not profile_picture:
            return Response({"error": "No profile picture found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfilePictureSerializer(profile_picture)
        return Response(serializer.data, status=status.HTTP_200_OK)