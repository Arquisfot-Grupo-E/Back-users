"""
sirve para definir cómo los modelos de Django se convierten en JSON y cómo los JSON 
que vienen del frontend se convierten en objetos válidos para Django.
"""

from rest_framework import serializers
from .models import CustomUser, UserProfile

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
            'is_staff',
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    avatar = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'avatar',
            'bio',
        ]

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
