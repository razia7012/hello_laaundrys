from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import User
from .serializers import SendOTPSerializer, VerifyOTPSerializer
from .utils import generate_otp, send_otp, store_otp
from django.core.cache import cache
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView


class SendOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            mobile = serializer.validated_data.get("mobile")
            contact = email or mobile
            otp = generate_otp()
            send_otp(contact, otp)
            store_otp(contact, otp)

            return Response({
                "success": True,
                "message": "OTP sent successfully.",
                "contact": contact
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data.get("mobile")
            email = serializer.validated_data.get("email")
            otp = serializer.validated_data["otp"]

            # OTP is always tied to mobile
            cached_otp = cache.get(f"otp_{mobile}")
            if cached_otp != otp:
                return Response({
                    "success": False,
                    "message": "Invalid or expired OTP."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create/find user using mobile
            user, _ = User.objects.get_or_create(mobile=mobile)

            # Update email only if provided
            if email and not user.email:
                user.email = email
                user.save()

            token, _ = Token.objects.get_or_create(user=user)
            cache.delete(f"otp_{mobile}")

            return Response({
                "success": True,
                "message": "Login successful.",
                "token": token.key,
                "user": {
                    "mobile": user.mobile,
                    "email": user.email,
                    "user_id": user.id
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
