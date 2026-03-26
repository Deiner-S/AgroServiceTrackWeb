from django.core.cache import cache


MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 900
ATTEMPT_WINDOW_SECONDS = 900


def _normalize_username(username):
    return (username or "").strip().lower()


def _get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _build_cache_key(username, client_ip):
    return f"login_attempts:{_normalize_username(username)}:{client_ip}"


def get_login_attempt_state(request, username):
    client_ip = _get_client_ip(request)
    key = _build_cache_key(username, client_ip)
    attempts = cache.get(key, 0)
    is_blocked = attempts >= MAX_LOGIN_ATTEMPTS

    return {
        "key": key,
        "attempts": attempts,
        "remaining_attempts": max(MAX_LOGIN_ATTEMPTS - attempts, 0),
        "is_blocked": is_blocked,
        "client_ip": client_ip,
        "username": _normalize_username(username),
        "lockout_seconds": LOCKOUT_SECONDS,
    }


def register_failed_login(request, username):
    state = get_login_attempt_state(request, username)
    attempts = state["attempts"] + 1
    cache.set(state["key"], attempts, timeout=ATTEMPT_WINDOW_SECONDS)

    state["attempts"] = attempts
    state["remaining_attempts"] = max(MAX_LOGIN_ATTEMPTS - attempts, 0)
    state["is_blocked"] = attempts >= MAX_LOGIN_ATTEMPTS
    return state


def reset_login_attempts(request, username):
    state = get_login_attempt_state(request, username)
    cache.delete(state["key"])
