from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email=None, mobile=None, **extra_fields):
        if not email and not mobile:
            raise ValueError("User must have either email or mobile.")
        user = self.model(email=email, mobile=mobile, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email or self.mobile or "User"
