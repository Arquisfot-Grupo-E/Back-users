from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.serializers import (
    UserProfileSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from django.utils.encoding import force_bytes, smart_str
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


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

class UserProfileSerializerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@example.com",
            password="123456",
            first_name="User",
            last_name="Example",
        )
        # La señal debe crear el perfil automáticamente
        cls.profile = cls.user.profile

    def test_user_is_nested_and_read_only_in_output(self):
        ser = UserProfileSerializer(self.profile)
        data = ser.data
        # user viene anidado
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], "user@example.com")
        # campos del perfil también
        self.assertIn("avatar", data)
        self.assertIn("bio", data)

    def test_cannot_update_nested_user_fields(self):
        payload = {"user": {"email": "otro@example.com"}, "bio": "nueva bio"}
        ser = UserProfileSerializer(instance=self.profile, data=payload, partial=True)
        self.assertTrue(ser.is_valid(), ser.errors)
        updated = ser.save()
        # bio sí cambia
        self.assertEqual(updated.bio, "nueva bio")
        # email NO cambia porque user es read-only
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "user@example.com")

    def test_update_avatar_valid_url(self):
        payload = {"avatar": "https://i.imgur.com/xyz123.png"}
        ser = UserProfileSerializer(instance=self.profile, data=payload, partial=True)
        self.assertTrue(ser.is_valid(), ser.errors)
        updated = ser.save()
        self.assertEqual(updated.avatar, payload["avatar"])

    def test_update_avatar_invalid_url(self):
        payload = {"avatar": "no-es-url"}
        ser = UserProfileSerializer(instance=self.profile, data=payload, partial=True)
        self.assertFalse(ser.is_valid())
        self.assertIn("avatar", ser.errors)

    def test_allow_blank_and_null_avatar(self):
        # blank
        ser_blank = UserProfileSerializer(instance=self.profile, data={"avatar": ""}, partial=True)
        self.assertTrue(ser_blank.is_valid(), ser_blank.errors)
        ser_blank.save()
        # null
        ser_null = UserProfileSerializer(instance=self.profile, data={"avatar": None}, partial=True)
        self.assertTrue(ser_null.is_valid(), ser_null.errors)
        updated = ser_null.save()
        self.assertIsNone(updated.avatar)

    def test_serializer_requires_profile_instance_not_user(self):
        with self.assertRaises(TypeError):
            UserProfileSerializer(instance=self.user)  # instancia equivocada

class PasswordResetSerializersTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="pwd@example.com", password="OldPass123!",
            first_name="Pwd", last_name="User"
        )

    def test_request_serializer_accepts_existing_email(self):
        s = PasswordResetRequestSerializer(data={"email": "pwd@example.com"})
        self.assertTrue(s.is_valid(), s.errors)

    def test_request_serializer_rejects_unknown_email(self):
        s = PasswordResetRequestSerializer(data={"email": "nope@example.com"})
        self.assertFalse(s.is_valid())
        self.assertIn("email", s.errors)

    def test_confirm_serializer_valid_token_changes_password(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = PasswordResetTokenGenerator().make_token(self.user)

        s = PasswordResetConfirmSerializer(data={
            "uidb64": uidb64,
            "token": token,
            "new_password": "NewPass123!",
        })
        self.assertTrue(s.is_valid(), s.errors)
        user = s.save()
        self.assertTrue(user.check_password("NewPass123!"))

    def test_confirm_serializer_invalid_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        s = PasswordResetConfirmSerializer(data={
            "uidb64": uidb64,
            "token": "invalid-token",
            "new_password": "NewPass123!",
        })
        self.assertFalse(s.is_valid())
        self.assertIn("token", s.errors)

class UserProfileSignalTests(TestCase):
    def test_bio_copies_from_description_and_clears_description(self):
        # Al crear el usuario con description...
        u = User.objects.create_user(
            email="copy@test.com",
            password="123456",
            first_name="Copy",
            last_name="User",
            description="Mi descripción inicial"
        )
        # La signal debe crear el perfil y copiar la description a bio
        profile = UserProfile.objects.get(user=u)
        self.assertEqual(profile.bio, "Mi descripción inicial")

        # Y debe limpiar description en el usuario
        u.refresh_from_db()
        self.assertEqual(u.description, "")

    def test_bio_not_overwritten_on_subsequent_user_saves(self):
        u = User.objects.create_user(
            email="keep@test.com",
            password="123456",
            first_name="Keep",
            last_name="User",
            description="Bio original"
        )
        profile = UserProfile.objects.get(user=u)
        self.assertEqual(profile.bio, "Bio original")

        # Cambiamos la description del usuario y guardamos
        u.description = "No debería copiarse"
        u.save()

        # La signal solo actúa en created=True; no debe modificar el bio existente
        profile.refresh_from_db()
        self.assertEqual(profile.bio, "Bio original")