from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class TokenRefreshRateThrottle(UserRateThrottle):
    scope = "token_refresh"


class SyncReadRateThrottle(UserRateThrottle):
    scope = "sync_read"


class SyncWriteRateThrottle(UserRateThrottle):
    scope = "sync_write"
