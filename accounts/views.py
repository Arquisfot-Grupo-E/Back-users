"""
Este archivo define las vistas (exponen los ENDPOINTS) 
para el registro y la gestión de usuarios.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import CustomUser
from .serializers import RegisterSerializer, UserPublicProfileSerializer, UserSerializer, UserProfileSerializer

from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.core.mail import send_mail
from django.conf import settings

# Registro de usuario
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# Listado y administración (solo admin)
class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

# Perfil del usuario actual
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    """
    Obtiene el perfil del usuario autenticado actual
    """
    serializer = UserProfileSerializer(request.user.profile)
    return Response(serializer.data)





@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_user_profile(request):
    """
    Actualiza el perfil del usuario autenticado actual
    """
    profile = request.user.profile
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create your views here.

# Password reset request view
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = get_user_model().objects.get(email=email)
        uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_url = f"http://localhost:5173/reset-password-confirm/{uidb64}/{token}/"  # Adjust frontend URL as needed
        send_mail(
            subject="Password Reset Request",
            message=f"Use the following link to reset your password: {reset_url}",
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({"detail": "Password reset link sent."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Password reset confirm view
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_preferred_genres(request):
    """
    Actualiza la lista de géneros preferidos del usuario (max 3 strings).
    Body esperado: { "preferred_genres": ["Genero1", "Genero2", "Genero3"] }
    """
    user = request.user
    data = request.data
    genres = data.get('preferred_genres', None)
    if genres is None:
        return Response({'preferred_genres': 'Este campo es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

    # Usar las mismas validaciones que en el serializer
    ser = UserSerializer(instance=user, data={'preferred_genres': genres}, partial=True)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    # Guardar campo en el usuario
    user.preferred_genres = ser.validated_data.get('preferred_genres', [])
    user.save()

    return Response({'detail': 'Géneros preferidos actualizados.', 'preferred_genres': user.preferred_genres}, status=status.HTTP_200_OK)


# Confirmar que el usuario ya eligió sus gustos
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_preferences(request):
    """
    Marca que el usuario ya eligió sus gustos.
    Este endpoint debe ser llamado por el frontend después de
    enviar los gustos al servicio de Recomendaciones.
    """
    user = request.user

    if getattr(user, 'has_selected_preferences', False):
        return Response(
            {"detail": "Ya seleccionaste tus gustos."},
            status=status.HTTP_200_OK
        )

    user.has_selected_preferences = True
    user.save()

    return Response(
        {"detail": "Preferencias confirmadas correctamente."},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_public_user_profile(request, user_id):
    """
    Obtiene el perfil público de un usuario específico por su ID
    """
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response(
            {"detail": "Usuario no encontrado"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = UserPublicProfileSerializer(user)
    return Response(serializer.data)
