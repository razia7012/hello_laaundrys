from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import OTP
from .serializers import SendOTPSerializer, VerifyOTPSerializer
from .utils import generate_otp, send_otp, store_otp
from django.core.cache import cache
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from django.contrib.auth import get_user_model
User = get_user_model()


class SendOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            mobile = serializer.validated_data.get("mobile")
            contact = mobile
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

            # cached_otp = cache.get(f"otp_{mobile}")
            cached_otp = OTP.objects.filter(contact=mobile).order_by('-created_at').first()
            
            if not cached_otp or cached_otp.otp != otp or cached_otp.is_expired():
                return Response({
                    "success": False,
                    "message": "Invalid or expired OTP."
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.filter(mobile=mobile).first()

                if not user:
                    # If email is provided, check if a user with that email exists
                    if email:
                        user = User.objects.filter(email=email).first()
                    if not user:
                        # Create new user
                        user = User.objects.create_user(email=email, mobile=mobile)
            except Exception as ex:
                return Response({
                    "success": False,
                    "message": str(ex)
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                token, _ = Token.objects.get_or_create(user=user)
            except Exception as ex:
                return Response({
                    "success": False,
                    "message": str(ex)
                }, status=status.HTTP_400_BAD_REQUEST)

            # cache.delete(f"otp_{mobile}")
            cached_otp.delete()

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
