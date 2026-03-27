from django.shortcuts import render

from checklist.exception_handler import RepositoryOperationError, is_repository_error
from checklist.templates_paths import TemplatePaths


def resolve_repository_result(request, result):
    if not is_repository_error(result):
        return result, None

    payload, status_code = result
    response = render(
        request,
        TemplatePaths.ERROR,
        {
            "error_message": payload["error"],
            "status_code": status_code,
        },
        status=status_code,
    )
    return None, response


def render_repository_error(request, exc):
    if not isinstance(exc, RepositoryOperationError):
        raise exc

    return render(
        request,
        TemplatePaths.ERROR,
        {
            "error_message": str(exc),
            "status_code": exc.status_code,
        },
        status=exc.status_code,
    )
