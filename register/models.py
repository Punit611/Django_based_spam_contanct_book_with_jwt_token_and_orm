from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class PhoneNumber(models.Model):
    number = models.CharField(max_length=20,unique=True)
    verified_name = models.CharField(max_length=100)
    is_spam=models.BooleanField(default=False)

    def __str__(self):
        return self.number


class OtherName(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=20,default='')
    is_spam = models.BooleanField(default=False)
    user = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, name, email=None, password=None):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, name=name, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, email=None, password=None):
        user = self.create_user(phone_number=phone_number, name=name, email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255, default='no_name')

    email = models.EmailField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.phone_number
