from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.test import RequestFactory

from checklist.middleware import GlobalExceptionMiddleware


def test_middleware_returns_json_response_for_api_requests(monkeypatch):
    save_log_calls = []
    monkeypatch.setattr("checklist.middleware.save_log", lambda error, request=None: save_log_calls.append((error, request)))

    middleware = GlobalExceptionMiddleware(lambda request: (_ for _ in ()).throw(PermissionDenied("nope")))
    request = RequestFactory().get("/gerenciador/receive_work_orders_api/", HTTP_ACCEPT="application/json")

    response = middleware(request)

    assert response.status_code == 403
    assert response.json() == {"error": "Acesso negado", "status_code": 403}
    assert len(save_log_calls) == 1


def test_middleware_returns_template_response_for_page_requests(monkeypatch):
    save_log_calls = []
    monkeypatch.setattr("checklist.middleware.save_log", lambda error, request=None: save_log_calls.append((error, request)))
    monkeypatch.setattr("checklist.middleware.render", lambda request, template, context, status=200: (template, context, status))

    middleware = GlobalExceptionMiddleware(lambda request: (_ for _ in ()).throw(Http404("missing")))
    request = RequestFactory().get("/gerenciador/panel/")

    template, context, status_code = middleware(request)

    assert status_code == 404
    assert context["error_message"] == "NÃ£o encontrado"
    assert context["status_code"] == 404
    assert len(save_log_calls) == 1


def test_middleware_resolves_suspicious_operation_to_400():
    middleware = GlobalExceptionMiddleware(lambda request: request)

    assert middleware._resolve_error_response(SuspiciousOperation()) == (400, "Dados invÃ¡lidos")


def test_middleware_detects_json_expectation_from_accept_header():
    middleware = GlobalExceptionMiddleware(lambda request: request)
    request = RequestFactory().get("/gerenciador/panel/", HTTP_ACCEPT="application/json")

    assert middleware._expects_json(request) is True


def test_middleware_detects_non_json_page_request():
    middleware = GlobalExceptionMiddleware(lambda request: request)
    request = RequestFactory().get("/gerenciador/panel/")

    assert middleware._expects_json(request) is False
