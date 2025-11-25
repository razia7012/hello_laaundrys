from rest_framework import serializers
from .models import User

class SendOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("mobile"):
            raise serializers.ValidationError("Either email or mobile is required.")
        return attrs


class VerifyOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    otp = serializers.CharField(required=True)

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("mobile"):
            raise serializers.ValidationError("Either email or mobile is required.")
        return attrs
