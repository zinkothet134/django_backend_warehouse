from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .serializers import (
    UserRegistrationSerializer, 
    PasswordResetConfirmSerializer, 
    PasswordResetRequestSerializer, 
    CustomTokenObtainPairSerializer,
    CurrentUserSerializer,
    StaffManagementSerializer)
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
import random
from django.core.cache import cache

# Create your views here.

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # Anyone can access this endpoint to register
    serializer_class =UserRegistrationSerializer

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Find the user by email
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            # 1. Generate a random 6-digit OTP
            otp = str(random.randint(100000, 999999))
            # # Generate the UID and Token
            # uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            # token = PasswordResetTokenGenerator().make_token(user)

            # 2. Save it to Django's cache for 10 minutes (600 seconds)
            cache.set(f"password_reset_otp_{user.email}", otp, timeout=600)


            # # In production, this would be your React/Vue frontend URL
            # frontend_url = f"http://localhost:5173/reset-password?uidb64={uidb64}&token={token}"


            # Send the email
            send_mail(
                subject='Your Passwrod Reset Code',
                # message=f'Click the link below to reset your password:\n\n{frontend_url}',
                message=f'Hello {user.username},\n\nYour 6-digit password reset code is: {otp}\n\nThis code will expire in 10 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        
        # Always return 200 OK even if email doesn't exist to prevent email enumeration attacks
        # return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        return Response(
            {'success': 'If an account exists, an OTP has been sent to that email.'}, 
            status=status.HTTP_200_OK
        )
    
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': 'Password reset successfully'}, status=status.HTTP_200_OK)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CurrentUserView(APIView):
    # This ensures only logged-in users with a valid JWT can access this endpoint
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user is automatically populated by SimpleJWT
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)
    
class StaffViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = StaffManagementSerializer
    permission_classes = [IsAuthenticated]

    # Optional but recommended: Extra backend security to ensure 
    # ONLY Admins can add, edit, or delete staff.
    def check_permissions(self, request):
        super().check_permissions(request)
        # Allow everyone to GET (view) the list, but restrict modifications
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            if request.user.role != 'ADMIN':
                raise PermissionDenied("Only administrators can modify staff accounts.")