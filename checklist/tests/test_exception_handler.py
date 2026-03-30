from unittest.mock import Mock

import pytest
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from django.test import RequestFactory
from rest_framework.exceptions import NotFound, Throttled

from checklist.exception_handler import (
    RepositoryOperationError,
    api_exception_handler,
    get_validation_error_message,
    handle_validation_exceptions,
    handle_repository_exceptions,
    is_repository_error,
    unwrap_repository_result,
)
from checklist.views.pages.view_utils import render_repository_error, resolve_repository_result


def test_get_validation_error_message_from_messages():
    exc = ValidationError(["Erro um", "Erro dois"])
    assert get_validation_error_message(exc) == "Erro um Erro dois"


def test_get_validation_error_message_from_message_dict():
    exc = ValidationError({"cpf": ["CPF invalido"], "email": ["Email invalido"]})
    assert get_validation_error_message(exc) == "CPF invalido Email invalido"


def test_handle_validation_exceptions_returns_error_payload():
    @handle_validation_exceptions
    def run_validation():
        raise ValidationError("CPF invalido")

    assert run_validation() == ({"error": "CPF invalido"}, 400)


def test_is_repository_error_returns_true_for_expected_shape():
    assert is_repository_error(({"error": "Falha"}, 400)) is True


def test_is_repository_error_returns_false_for_non_repository_payload():
    assert is_repository_error({"error": "Falha"}) is False
    assert is_repository_error(({"message": "Falha"}, 400)) is False
    assert is_repository_error(("Falha", 400)) is False


def test_unwrap_repository_result_returns_original_value_for_success_payload():
    payload = {"ok": True}
    assert unwrap_repository_result(payload) == payload


def test_unwrap_repository_result_raises_repository_operation_error():
    with pytest.raises(RepositoryOperationError) as exc_info:
        unwrap_repository_result(({"error": "Falha de repositorio"}, 409))

    assert str(exc_info.value) == "Falha de repositorio"
    assert exc_info.value.status_code == 409


def test_handle_repository_exceptions_returns_validation_error_payload(monkeypatch):
    save_log_mock = Mock()
    monkeypatch.setattr("checklist.exception_handler.save_log", save_log_mock)

    @handle_repository_exceptions
    def run_repository():
        raise ValidationError("Campo invalido")

    assert run_repository() == ({"error": "Campo invalido"}, 400)
    save_log_mock.assert_called_once()


def test_handle_repository_exceptions_returns_integrity_error_payload(monkeypatch):
    save_log_mock = Mock()
    monkeypatch.setattr("checklist.exception_handler.save_log", save_log_mock)

    @handle_repository_exceptions
    def run_repository():
        raise IntegrityError("Violacao de integridade")

    assert run_repository() == ({"error": "Dados invalidos"}, 400)
    save_log_mock.assert_called_once()


def test_handle_repository_exceptions_returns_not_found_payload(monkeypatch):
    save_log_mock = Mock()
    monkeypatch.setattr("checklist.exception_handler.save_log", save_log_mock)

    @handle_repository_exceptions
    def run_repository():
        raise ObjectDoesNotExist("Nao encontrado")

    assert run_repository() == ({"error": "Nao encontrado"}, 404)
    save_log_mock.assert_called_once()


def test_handle_repository_exceptions_returns_internal_error_payload(monkeypatch):
    save_log_mock = Mock()
    monkeypatch.setattr("checklist.exception_handler.save_log", save_log_mock)

    @handle_repository_exceptions
    def run_repository():
        raise RuntimeError("Erro inesperado")

    assert run_repository() == ({"error": "Erro interno"}, 500)
    save_log_mock.assert_called_once()


def test_api_exception_handler_logs_throttled_requests(client, monkeypatch):
    save_security_log_mock = Mock()
    monkeypatch.setattr(
        "checklist.exception_handler.save_security_log",
        save_security_log_mock,
    )

    request = client.get("/gerenciador/api/token/").wsgi_request
    response = api_exception_handler(Throttled(wait=60), {"request": request, "view": None})

    assert response is not None
    assert response.status_code == 429
    save_security_log_mock.assert_called_once()


def test_api_exception_handler_does_not_log_non_throttled_requests(client, monkeypatch):
    save_security_log_mock = Mock()
    monkeypatch.setattr(
        "checklist.exception_handler.save_security_log",
        save_security_log_mock,
    )

    request = client.get("/gerenciador/api/token/").wsgi_request
    response = api_exception_handler(NotFound(), {"request": request, "view": None})

    assert response is not None
    assert response.status_code == 404
    save_security_log_mock.assert_not_called()


def test_render_repository_error_logs_original_error_and_returns_generic_message(monkeypatch):
    request = RequestFactory().get("/gerenciador/clientes/")
    save_log_mock = Mock()
    render_mock = Mock(return_value="rendered-response")
    monkeypatch.setattr("checklist.views.pages.view_utils.save_log", save_log_mock)
    monkeypatch.setattr("checklist.views.pages.view_utils.render", render_mock)

    response = render_repository_error(
        request,
        RepositoryOperationError("Falha detalhada do repositorio", 400),
    )

    assert response == "rendered-response"
    save_log_mock.assert_called_once()
    assert save_log_mock.call_args.args[0].args[0] == "Falha detalhada do repositorio"
    assert save_log_mock.call_args.kwargs["request"] is request
    assert render_mock.call_args.args[2]["error_message"] == "Dados invalidos"
    assert render_mock.call_args.kwargs["status"] == 400


def test_resolve_repository_result_logs_original_error_and_returns_generic_message(
    monkeypatch,
):
    request = RequestFactory().get("/gerenciador/clientes/")
    save_log_mock = Mock()
    render_mock = Mock(return_value="rendered-response")
    monkeypatch.setattr("checklist.views.pages.view_utils.save_log", save_log_mock)
    monkeypatch.setattr("checklist.views.pages.view_utils.render", render_mock)

    result, response = resolve_repository_result(
        request,
        ({"error": "Falha detalhada do repositorio"}, 404),
    )

    assert result is None
    assert response == "rendered-response"
    save_log_mock.assert_called_once_with("Falha detalhada do repositorio", request=request)
    assert render_mock.call_args.args[2]["error_message"] == "Nao encontrado"
    assert render_mock.call_args.kwargs["status"] == 404
