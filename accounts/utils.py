import requests
import random
from django.core.cache import cache
from .models import OTP

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp(contact, otp):
    # Later integrate Twilio/Firebase/SMTP
    print(f"OTP for {contact}: {otp}")

def store_otp(contact, otp):
    OTP.objects.create(contact=contact, otp=otp)
    print("OTP stored in the db.")
    # cache.set(f"otp_{contact}", otp, timeout=300)  
