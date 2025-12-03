from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta

#previous one
# class UserManager(BaseUserManager):
#     def create_user(self, email=None, mobile=None, **extra_fields):
#         if not email and not mobile:
#             raise ValueError("User must have either email or mobile.")
#         user = self.model(email=email, mobile=mobile, **extra_fields)
#         user.set_unusable_password()
#         user.save(using=self._db)
#         return user

class UserManager(BaseUserManager):
    def create_user(self, email=None, mobile=None, password=None, **extra_fields):
        if not email and not mobile:
            raise ValueError("User must have either email or mobile.")

        user = self.model(email=email, mobile=mobile, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, mobile=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, mobile=mobile, password=password, **extra_fields)

# previous one
# class User(AbstractBaseUser):
#     email = models.EmailField(unique=True, null=True, blank=True)
#     mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
#     is_active = models.BooleanField(default=True)
#     date_joined = models.DateTimeField(auto_now_add=True)

#     # USERNAME_FIELD = 'email'
#     # REQUIRED_FIELDS = []
#     USERNAME_FIELD = 'mobile'
#     REQUIRED_FIELDS = []

#     objects = UserManager()

#     def __str__(self):
#         return self.email or self.mobile or "User"

class User(AbstractBaseUser, models.Model):
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)        # ← REQUIRED for admin login
    is_superuser = models.BooleanField(default=False)    # ← REQUIRED for admin permissions

    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []   # Django will ask only for mobile

    objects = UserManager()

    def __str__(self):
        return self.email or self.mobile or "User"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class OTP(models.Model):
    contact = models.CharField(max_length=100)  
    otp = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.contact} - {self.otp}"
