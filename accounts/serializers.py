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

class SetNameSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15)
    full_name = serializers.CharField(max_length=150)

    def validate_full_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name is too short")
        return value.strip()