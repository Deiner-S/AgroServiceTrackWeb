from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)


class ActiveEmployeeTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": "Funcionario inativo ou credenciais invalidas."
    }


class ActiveEmployeeTokenRefreshSerializer(TokenRefreshSerializer):
    default_error_messages = {
        "no_active_account": "Funcionario inativo ou credenciais invalidas."
    }
