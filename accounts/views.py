"""
Este archivo define las vistas (exponen los ENDPOINTS) 
para el registro y la gestión de usuarios.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer

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
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# Create your views here.
