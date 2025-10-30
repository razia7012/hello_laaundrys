from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import User
from .serializers import SendOTPSerializer, VerifyOTPSerializer
from .utils import generate_otp, send_otp, store_otp
from django.core.cache import cache

class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
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
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            mobile = serializer.validated_data.get("mobile")
            otp = serializer.validated_data["otp"]
            contact = email or mobile

            cached_otp = cache.get(f"otp_{contact}")
            if cached_otp != otp:
                return Response({
                    "success": False,
                    "message": "Invalid or expired OTP."
                }, status=status.HTTP_400_BAD_REQUEST)

            user, _ = User.objects.get_or_create(email=email, mobile=mobile)
            token, _ = Token.objects.get_or_create(user=user)
            cache.delete(f"otp_{contact}")

            return Response({
                "success": True,
                "message": "Login successful.",
                "token": token.key,
                "user": {
                    "email": user.email,
                    "mobile": user.mobile,
                    "user_id": user.id
                }
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
