from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from checklist.utils.logging_utils import save_log


def handle_repository_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
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
