from dataclasses import dataclass

from django.contrib.auth import authenticate, login

from checklist.exception_handler import unwrap_repository_result
from checklist.login_attempts import (
    get_login_attempt_state,
    register_failed_login,
    reset_login_attempts,
)
from checklist.repository import employee_repository
from checklist.utils.logging_utils import save_security_log


@dataclass(frozen=True)
class LoginServiceResult:
    ok: bool
    error_message: str = ""


def authenticate_web_user(request, username, password):
    login_state = get_login_attempt_state(request, username)

    if login_state["is_blocked"]:
        save_security_log(
            "web_login_blocked",
            request=request,
            attempted_username=login_state["username"],
            attempts=login_state["attempts"],
            lockout_seconds=login_state["lockout_seconds"],
        )
        return LoginServiceResult(
            ok=False,
            error_message="Muitas tentativas de login. Tente novamente mais tarde.",
        )

    user = authenticate(request, username=username, password=password)
    if user is not None:
        reset_login_attempts(request, username)
        login(request, user)
        return LoginServiceResult(ok=True)

    inactive_user = unwrap_repository_result(
        employee_repository.find_inactive_by_username(username)
    )
    if inactive_user is not None and inactive_user.check_password(password):
        _register_failed_login_with_audit(request, username)
        return LoginServiceResult(
            ok=False,
            error_message="Funcionario inativo. Procure um administrador.",
        )

    _register_failed_login_with_audit(request, username)
    return LoginServiceResult(
        ok=False,
        error_message="Usuario ou senha invalidos.",
    )


def _register_failed_login_with_audit(request, username):
    failed_state = register_failed_login(request, username)
    if failed_state["is_blocked"]:
        save_security_log(
            "web_login_rate_limit_exceeded",
            request=request,
            attempted_username=failed_state["username"],
            attempts=failed_state["attempts"],
            remaining_attempts=failed_state["remaining_attempts"],
            lockout_seconds=failed_state["lockout_seconds"],
        )
    return failed_state
