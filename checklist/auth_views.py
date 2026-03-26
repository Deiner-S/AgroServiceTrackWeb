from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from checklist.auth_serializers import (
    ActiveEmployeeTokenObtainPairSerializer,
    ActiveEmployeeTokenRefreshSerializer,
)
from checklist.throttling import LoginRateThrottle, TokenRefreshRateThrottle


class ActiveEmployeeTokenObtainPairView(TokenObtainPairView):
    serializer_class = ActiveEmployeeTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]


class ActiveEmployeeTokenRefreshView(TokenRefreshView):
    serializer_class = ActiveEmployeeTokenRefreshSerializer
    throttle_classes = [TokenRefreshRateThrottle]
