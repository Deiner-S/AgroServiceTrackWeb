from functools import wraps

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from rest_framework.exceptions import Throttled
from rest_framework.views import exception_handler as drf_exception_handler

from checklist.utils.logging_utils import save_log, save_security_log


class RepositoryOperationError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


def get_validation_error_message(exc):
    if hasattr(exc, "message_dict"):
        return " ".join(
            message
            for field_messages in exc.message_dict.values()
            for message in field_messages
        )

    if hasattr(exc, "messages"):
        return " ".join(exc.messages)

    return str(exc)


def is_repository_error(result):
    return (
        isinstance(result, tuple)
        and len(result) == 2
        and isinstance(result[0], dict)
        and "error" in result[0]
    )


def unwrap_repository_result(result):
    if not is_repository_error(result):
        return result

    payload, status_code = result
    raise RepositoryOperationError(payload["error"], status_code)


def handle_validation_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as exc:
            save_log(exc)
            return {"error": get_validation_error_message(exc)}, 400

    return wrapper


def handle_repository_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as exc:
            save_log(exc)
            return {"error": get_validation_error_message(exc)}, 400
        except IntegrityError as exc:
            save_log(exc)
            return {"error": "Dados inválidos"}, 400
        except ObjectDoesNotExist as exc:
            save_log(exc)
            return {"error": "Não encontrado"}, 404
        except Exception as exc:
            save_log(exc)
            return {"error": "Erro interno"}, 500

    return wrapper


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if isinstance(exc, Throttled):
        request = context.get("request") if context else None
        wait_time = int(exc.wait) if exc.wait is not None else None
        view = context.get("view") if context else None

        save_security_log(
            "api_rate_limit_exceeded",
            request=request,
            wait_seconds=wait_time,
            view_name=view.__class__.__name__ if view is not None else None,
            throttle_detail=str(exc.detail),
        )

    return response
