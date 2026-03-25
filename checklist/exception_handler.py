from functools import wraps

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError

from checklist.utils.logging_utils import save_log


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
            return {"error": "Dados invalidos"}, 400
        except ObjectDoesNotExist as exc:
            save_log(exc)
            return {"error": "Nao encontrado"}, 404
        except Exception as exc:
            save_log(exc)
            return {"error": "Erro interno"}, 500

    return wrapper
