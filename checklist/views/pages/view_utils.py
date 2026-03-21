from django.shortcuts import render

from checklist.repository.exception_handler import is_repository_error
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
