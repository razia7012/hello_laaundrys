from rest_framework import serializers
from .models import User

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=False)

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("mobile"):
            raise serializers.ValidationError("Either email or mobile is required.")
        return attrs


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=False)
    otp = serializers.CharField(max_length=4)

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("mobile"):
            raise serializers.ValidationError("Either email or mobile is required.")
        return attrs
