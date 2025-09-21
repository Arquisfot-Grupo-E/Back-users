"""
Define las rutas URL para las vistas de la aplicación de cuentas.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, UserListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'), # registro
    path('users/', UserListView.as_view(), name='user-list'), # solo admin/listar usuarios
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # login
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),      # refrescar token
]
