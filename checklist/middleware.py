from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404, JsonResponse
from django.shortcuts import render

from checklist.templates_paths import TemplatePaths
from checklist.utils.logging_utils import save_log


class GlobalExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:
            status_code, message = self._resolve_error_response(exc)
            save_log(exc, request=request)

            if self._expects_json(request):
                return JsonResponse(
                    {
                        "error": message,
                        "status_code": status_code,
                    },
                    status=status_code,
                )

            return render(
                request,
                TemplatePaths.ERROR,
                {
                    "error_message": message,
                    "status_code": status_code,
                },
                status=status_code,
            )

    def _resolve_error_response(self, exc):
        if isinstance(exc, SuspiciousOperation):
            return 400, "Dados inválidos"
        if isinstance(exc, PermissionDenied):
            return 403, "Acesso negado"
        if isinstance(exc, Http404):
            return 404, "Não encontrado"
        return 500, "Erro interno"

    def _expects_json(self, request):
        accept = request.headers.get("Accept", "")
        return (
            request.path.startswith("/gerenciador/api/")
            or request.path.startswith("/gerenciador/send_")
            or request.path.startswith("/gerenciador/receive_")
            or "application/json" in accept
        )
