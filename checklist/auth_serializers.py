from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)


class ActiveEmployeeTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": "Funcionário inativo ou credenciais inválidas."
    }


class ActiveEmployeeTokenRefreshSerializer(TokenRefreshSerializer):
    default_error_messages = {
        "no_active_account": "Funcionário inativo ou credenciais inválidas."
    }
