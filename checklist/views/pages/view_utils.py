from django.shortcuts import render

from checklist.exception_handler import RepositoryOperationError, is_repository_error
from checklist.templates_paths import TemplatePaths
from checklist.utils.logging_utils import save_log


def get_generic_repository_error_message(status_code):
    if status_code == 400:
        return "Dados invalidos"
    if status_code == 404:
        return "Nao encontrado"
    return "Erro interno"


def resolve_repository_result(request, result):
    if not is_repository_error(result):
        return result, None

    payload, status_code = result
    save_log(payload["error"], request=request)
    response = render(
        request,
        TemplatePaths.ERROR,
        {
            "error_message": get_generic_repository_error_message(status_code),
            "status_code": status_code,
        },
        status=status_code,
    )
    return None, response


def render_repository_error(request, exc):
    if not isinstance(exc, RepositoryOperationError):
        raise exc

    save_log(exc, request=request)

    return render(
        request,
        TemplatePaths.ERROR,
        {
            "error_message": get_generic_repository_error_message(exc.status_code),
            "status_code": exc.status_code,
        },
        status=exc.status_code,
    )


def render_forbidden(request, message="Acesso negado"):
    return render(
        request,
        TemplatePaths.ERROR,
        {
            "error_message": message,
            "status_code": 403,
        },
        status=403,
    )
