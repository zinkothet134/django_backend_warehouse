from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.exceptions import AuthenticationFailed
import random
from django.core.cache import cache


User = get_user_model()

# Custom Login Serializer to add the role claim 
# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # add custom claims to the JWT payload
#         token['username'] = user.username
#         token['role'] = user.role

#         return token 
    
# Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'phone_number')

    def create(self, validated_data):
        # Use create_user to ensure password is hashed properly
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'SALES'),
            phone_number=validated_data.get('phone_number', '')
        )
        return user
    

class StaffManagementSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        style={"input_type": "password"},
    )
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "phone_number",
            "is_active",
            "date_joined",
            "password",
        ]
        read_only_fields = ["id", "full_name", "date_joined"]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def validate_email(self, value):
        if not value:
            return value

        queryset = User.objects.filter(email__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("A user with this email already exists.")

        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        if not password:
            raise serializers.ValidationError(
                {"password": "Password is required when creating a staff account."}
            )

        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
class CurrentUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'full_name', 
            'role', 
            'phone_number'
        ]
        # Make everything read-only since this is just for fetching the profile
        read_only_fields = fields 

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    password = serializers.CharField(min_length=8, write_only=True)
    # token = serializers.CharField(min_length=1, write_only=True)
    # uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        # fields = ['password', 'token', 'uidb64']
        fields = ['email', 'otp', 'password']

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        password = attrs.get('password')

        # 1. Retrieve the OTP from Django's cache
        cached_otp = cache.get(f"password_reset_otp_{email}")

        # 2. Check if it exists and matches
        if not cached_otp or cached_otp != otp:
            raise AuthenticationFailed('This OTP is invalid or has expired.', 401)
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            
            # 4. Delete the OTP from the cache so it cannot be reused
            cache.delete(f"password_reset_otp_{email}")
            # password = attrs.get('password')
            # token = attrs.get('token')
            # uidb64 = attrs.get('uidb64')
            # # Decode the User ID
            # id = force_str(urlsafe_base64_decode(uidb64))
            # user = User.objects.get(id=id)

            # # Verify the token is valid for this specific user
            # if not PasswordResetTokenGenerator().check_token(user, token):
            #     raise AuthenticationFailed('The reset link is invalid or has expired', 401)

            # # Set the new password
            # user.set_password(password)
            # user.save()

            return user
        except Exception:
            raise AuthenticationFailed('User not found', 401)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Get the standard token
        token = super().get_token(user)
        # Add custom fields to the token payload (the ID card)
        token['username'] = user.username
        token['role'] = user.role
        token['email'] = user.email # Uncomment if you want email too!
        return token