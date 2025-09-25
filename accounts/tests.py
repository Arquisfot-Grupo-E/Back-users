from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from accounts.models import UserProfile

User = get_user_model()

TOKEN_URL = "/api/accounts/login/"
PROFILE_URL = "/api/accounts/profile/"  # ajusta si tu path es distinto
PROFILE_EDIT_URL = "/api/accounts/profile/update/"

class ProfileApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Usuario base para pruebas
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="123456",
            first_name="Test",
            last_name="User",
        )
        # La señal debe crear automáticamente el UserProfile
        # Verificamos en un test aparte, pero aquí ya debería existir

    def setUp(self):
        self.client = APIClient()

    def test_signal_crea_perfil_al_crear_usuario(self):
        u = User.objects.create_user(
            email="nueva@ej.com",
            password="x",
            first_name="Nueva",
            last_name="User",
        )

        self.assertTrue(
            UserProfile.objects.filter(user=u).exists(),
            "La señal no creó el UserProfile automáticamente",
        )

    def test_get_profile_requiere_auth(self):
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_ok(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("user", res.data)
        # Campos esperados
        self.assertIn("avatar", res.data)
        self.assertIn("bio", res.data)
        # Datos del nested user
        self.assertEqual(res.data["user"]["email"], "test@example.com")

    def test_put_profile_actualiza(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "avatar": "https://i.imgur.com/xyz123.png",
            "bio": "Me gusta programar en Django",
        }
        res = self.client.put(PROFILE_EDIT_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["avatar"], payload["avatar"])
        self.assertEqual(res.data["bio"], payload["bio"])

        # Verifica en DB
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.avatar, payload["avatar"])
        self.assertEqual(self.user.profile.bio, payload["bio"])

    def test_put_profile_valida_url(self):
        self.client.force_authenticate(user=self.user)
        payload = {"avatar": "no-es-url"}
        res = self.client.put(PROFILE_EDIT_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", res.data)

class JwtFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="jwt@example.com",
            password="secret123",
            first_name="Jwt",
            last_name="User",
        )

    def test_jwt_obtain_and_use_on_profile(self):
        # 1) Obtiene token
        res = self.client.post(TOKEN_URL, {
            "email": "jwt@example.com",
            "password": "secret123",
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        access = res.data["access"]

        # 2) Usa el token en Authorization
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        res2 = self.client.get(PROFILE_URL)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data["user"]["email"], "jwt@example.com")

    def test_jwt_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token")
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)