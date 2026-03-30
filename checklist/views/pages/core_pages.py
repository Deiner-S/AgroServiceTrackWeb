from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from checklist.exception_handler import RepositoryOperationError
from checklist.permissions import get_access_context
from checklist.services import auth_page_services
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.view_utils import render_repository_error


@login_required(login_url="gerenciador/login/")
def home(request):
    return render(request, TemplatePaths.HOME, get_access_context(request.user))


def auth_login(request):
    try:
        if request.method == "POST":
            usuario = request.POST.get("usuario")
            senha = request.POST.get("senha")
            result = auth_page_services.authenticate_web_user(request, usuario, senha)

            if result.ok:
                return redirect("home")

            return render(
                request,
                TemplatePaths.LOGIN,
                {"erro": result.error_message},
            )

        return render(request, TemplatePaths.LOGIN)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


def logout_view(request):
    logout(request)
    return redirect(reverse("login"))
