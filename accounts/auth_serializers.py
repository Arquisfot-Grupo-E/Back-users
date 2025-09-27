from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Añade claims personalizados al payload
        token['first_name'] = user.first_name
        # 'user_id' ya viene por defecto; añadimos 'sub' si prefieres el estándar
        token['sub'] = str(user.pk)
        return token
