from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from checklist.login_attempts import (
    get_login_attempt_state,
    register_failed_login,
    reset_login_attempts,
)
from checklist.repository import employee_repository
from checklist.templates_paths import TemplatePaths
from checklist.utils.logging_utils import save_security_log
from checklist.views.pages.view_utils import resolve_repository_result

@login_required(login_url="gerenciador/login/")
def home(request):
    return render(request, TemplatePaths.HOME)


def auth_login(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        senha = request.POST.get("senha")
        login_state = get_login_attempt_state(request, usuario)

        if login_state["is_blocked"]:
            save_security_log(
                "web_login_blocked",
                request=request,
                attempted_username=login_state["username"],
                attempts=login_state["attempts"],
                lockout_seconds=login_state["lockout_seconds"],
            )
            return render(
                request,
                TemplatePaths.LOGIN,
                {"erro": "Muitas tentativas de login. Tente novamente mais tarde."},
            )

        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            reset_login_attempts(request, usuario)
            login(request, user)
            return redirect("home")

        inactive_user, error_response = resolve_repository_result(
            request,
            employee_repository.find_inactive_by_username(usuario),
        )
        if error_response:
            return error_response

        if inactive_user is not None and inactive_user.check_password(senha):
            failed_state = register_failed_login(request, usuario)
            if failed_state["is_blocked"]:
                save_security_log(
                    "web_login_rate_limit_exceeded",
                    request=request,
                    attempted_username=failed_state["username"],
                    attempts=failed_state["attempts"],
                    remaining_attempts=failed_state["remaining_attempts"],
                    lockout_seconds=failed_state["lockout_seconds"],
                )
            return render(
                request,
                TemplatePaths.LOGIN,
                {"erro": "Funcionario inativo. Procure um administrador."},
            )

        failed_state = register_failed_login(request, usuario)
        if failed_state["is_blocked"]:
            save_security_log(
                "web_login_rate_limit_exceeded",
                request=request,
                attempted_username=failed_state["username"],
                attempts=failed_state["attempts"],
                remaining_attempts=failed_state["remaining_attempts"],
                lockout_seconds=failed_state["lockout_seconds"],
            )

        return render(
            request,
            TemplatePaths.LOGIN,
            {"erro": "Usuario ou senha invalidos."},
        )

    return render(request, TemplatePaths.LOGIN)


def logout_view(request):
    logout(request)
    return redirect(reverse("login"))
