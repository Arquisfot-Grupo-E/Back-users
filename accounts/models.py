"""
Este archivo define un modelo de usuario personalizado en Django.
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, last_name=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        if not first_name:
            raise ValueError('El nombre es obligatorio')
        if not last_name:
            raise ValueError('El apellido es obligatorio')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password) # Encripta la contraseña
        user.save(using=self._db)
        return user

    # Crea un superusuario
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True) # Necesario para acceder al admin
        extra_fields.setdefault('is_superuser', True) # Necesario para permisos de superusuario

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Modelo de usuario personalizado
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)  # obligatorio
    last_name = models.CharField(max_length=150)   # obligatorio
    description = models.TextField(blank=True, null=True)  # opcional
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # obligatorios para createsuperuser

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.first_name} {self.user.last_name} <{self.user.email}>"
