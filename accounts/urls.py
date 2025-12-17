from django.urls import path
from .views import SendOTPView, VerifyOTPView, SetCustomerNameView

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('customer/set-name/', SetCustomerNameView.as_view(), name='set-customer-name'),
]
