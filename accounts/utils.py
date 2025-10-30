import random
from django.core.cache import cache

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp(contact, otp):
    # Later integrate Twilio/Firebase/SMTP
    print(f"OTP for {contact}: {otp}")

def store_otp(contact, otp):
    cache.set(f"otp_{contact}", otp, timeout=300)  # valid 5 minutes
