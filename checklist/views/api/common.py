from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response

from checklist.exception_handler import get_validation_error_message
from checklist.utils.logging_utils import save_log


def forbid_if(condition, message):
    if condition:
        raise PermissionDenied(message)


def validation_error_response(error, request):
    save_log(error, request)
    return Response(
        {"ok": False, "error": get_validation_error_message(error)},
        status=status.HTTP_400_BAD_REQUEST,
    )
