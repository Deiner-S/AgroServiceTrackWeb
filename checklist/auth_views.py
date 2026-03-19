from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from checklist.auth_serializers import (
    ActiveEmployeeTokenObtainPairSerializer,
    ActiveEmployeeTokenRefreshSerializer,
)


class ActiveEmployeeTokenObtainPairView(TokenObtainPairView):
    serializer_class = ActiveEmployeeTokenObtainPairSerializer


class ActiveEmployeeTokenRefreshView(TokenRefreshView):
    serializer_class = ActiveEmployeeTokenRefreshSerializer
