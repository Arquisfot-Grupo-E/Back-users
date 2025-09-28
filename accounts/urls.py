"""
Define las rutas URL para las vistas de la aplicación de cuentas.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .auth_views import MyTokenObtainPairView
from .views import RegisterView, UserListView, get_user_profile, update_user_profile, password_reset_request, password_reset_confirm, confirm_preferences, update_preferred_genres

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'), # registro
    path('users/', UserListView.as_view(), name='user-list'), # solo admin/listar usuarios
    path('profile/', get_user_profile, name='user-profile'), # perfil del usuario actual
    path('profile/update/', update_user_profile, name='user-profile-update'), # actualizar perfil del usuario actual
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # login (custom serializer adds first_name)
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),      # refrescar token
    path('password-reset/', password_reset_request, name='password_reset'),
    path('password-reset-confirm/', password_reset_confirm, name='password_reset_confirm'),
    path('confirm-preferences/', confirm_preferences, name='confirm_preferences'),
    path('profile/genres/', update_preferred_genres, name='update_preferred_genres'),
]
