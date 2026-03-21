from django.shortcuts import render

from checklist.templates_paths import TemplatePaths


def is_repository_error(result):
    return (
        isinstance(result, tuple)
        and len(result) == 2
        and isinstance(result[0], dict)
        and "error" in result[0]
    )


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
