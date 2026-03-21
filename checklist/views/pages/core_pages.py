from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from checklist.repository import employee_repository
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.view_utils import resolve_repository_result

@login_required(login_url="gerenciador/login/")
def home(request):
    return render(request, TemplatePaths.HOME)


def auth_login(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        senha = request.POST.get("senha")

        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            login(request, user)
            return redirect("home")

        inactive_user, error_response = resolve_repository_result(
            request,
            employee_repository.find_inactive_by_username(usuario),
        )
        if error_response:
            return error_response

        if inactive_user is not None and inactive_user.check_password(senha):
            return render(
                request,
                TemplatePaths.LOGIN,
                {"erro": "Funcionario inativo. Procure um administrador."},
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
