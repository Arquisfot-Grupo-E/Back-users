"""
sirve para definir cómo los modelos de Django se convierten en JSON y cómo los JSON 
que vienen del frontend se convierten en objetos válidos para Django.
"""

from rest_framework import serializers
from .models import CustomUser, UserProfile

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, smart_bytes, smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model

# Serializador para la información del usuario
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'description',
            'is_active',
            'has_selected_preferences',
            'preferred_genres',
            'is_staff',
        ]

    def validate_preferred_genres(self, value):
        # Permitir lista vacía o hasta 3 géneros (strings)
        if not isinstance(value, list):
            raise serializers.ValidationError('preferred_genres debe ser una lista')
        if len(value) > 3:
            raise serializers.ValidationError('Solo se permiten hasta 3 géneros')
        for item in value:
            if not isinstance(item, str):
                raise serializers.ValidationError('Cada género debe ser una cadena de texto')
        return value

class UserProfileSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        if instance is not None and not isinstance(instance, UserProfile):
            raise TypeError("UserProfileSerializer requires a UserProfile instance")
    
    user = UserSerializer(read_only=True)
    avatar = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    first_name = serializers.CharField(write_only=True, required=False)
    last_name  = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'avatar',
            'bio',
            "first_name",
            "last_name",
        ]

    def update(self, instance, validated_data):
        first_name = validated_data.pop("first_name", None)
        last_name  = validated_data.pop("last_name", None)

        if first_name is not None:
            instance.user.first_name = first_name
        if last_name is not None:
            instance.user.last_name = last_name
        if first_name is not None or last_name is not None:
            to_update = []
            if first_name is not None: to_update.append("first_name")
            if last_name  is not None: to_update.append("last_name")
            instance.user.save(update_fields=to_update)

        # continúa con la actualización del perfil (avatar/bio)
        return super().update(instance, validated_data)
    
# Serializer for requesting password reset
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        User = get_user_model()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email address.")
        return value


# Serializer for confirming password reset
class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        try:
            uid = smart_str(urlsafe_base64_decode(attrs['uidb64']))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist, DjangoUnicodeDecodeError):
            raise serializers.ValidationError({'uidb64': 'Invalid value'})

        if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
            raise serializers.ValidationError({'token': 'Invalid or expired token'})

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.validated_data['user']
        user.set_password(password)
        user.save()
        return user

# Serializador para el registro de nuevos usuarios
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    
    class Meta:
        model = CustomUser
        fields = [
            'email',
            'first_name',
            'last_name',
            'description',
            'password',
        ]

    # Crear un nuevo usuario con los datos validados
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],  
            last_name=validated_data['last_name'],    
            password=validated_data['password'],
            description=validated_data.get('description', '')  
        )
        return user


class UserPublicProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar información pública de un usuario
    (sin email ni datos sensibles)
    """
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'date_joined',
            'profile',  # incluye avatar y bio
        ]