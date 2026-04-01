from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate

from checklist.views.api.sync_api import (
    receive_checkLists_filleds,
    receive_mobile_logs_api,
    receive_work_orders_api,
)


@pytest.fixture
def api_user(django_user_model):
    return django_user_model.objects.create_user(
        username="api-user",
        password="secret123",
    )


def test_receive_work_orders_api_returns_400_with_validation_message(api_user, monkeypatch):
    factory = APIRequestFactory()
    request = factory.post("/gerenciador/receive_work_orders_api/", [], format="json")
    force_authenticate(request, user=api_user)

    monkeypatch.setattr(
        "checklist.views.api.sync_api.validate_work_order_entries",
        Mock(side_effect=ValidationError("payload invalido")),
    )
    save_log_mock = Mock()
    monkeypatch.setattr("checklist.views.api.sync_api.save_log", save_log_mock)

    response = receive_work_orders_api(request)

    assert response.status_code == 400
    assert response.data == {"ok": False, "error": "payload invalido"}
    save_log_mock.assert_called_once()


def test_receive_work_orders_api_returns_ok_on_success(api_user, monkeypatch):
    factory = APIRequestFactory()
    request = factory.post("/gerenciador/receive_work_orders_api/", [], format="json")
    force_authenticate(request, user=api_user)

    monkeypatch.setattr(
        "checklist.views.api.sync_api.validate_work_order_entries",
        Mock(return_value=[{"work_order": object(), "status": "2"}]),
    )
    save_work_orders_mock = Mock()
    monkeypatch.setattr("checklist.views.api.sync_api.api_services.save_work_orders_filleds", save_work_orders_mock)

    response = receive_work_orders_api(request)

    assert response.status_code == 200
    assert response.data == {"ok": True}
    save_work_orders_mock.assert_called_once()


def test_receive_checklists_api_returns_false_on_unexpected_exception(api_user, monkeypatch):
    factory = APIRequestFactory()
    request = factory.post("/gerenciador/receive_checklist_api/", [], format="json")
    force_authenticate(request, user=api_user)

    monkeypatch.setattr(
        "checklist.views.api.sync_api.validate_checklist_entries",
        Mock(return_value=[{"id": "1"}]),
    )
    monkeypatch.setattr(
        "checklist.views.api.sync_api.api_services.save_checklists_filleds",
        Mock(side_effect=RuntimeError("db down")),
    )
    save_log_mock = Mock()
    monkeypatch.setattr("checklist.views.api.sync_api.save_log", save_log_mock)

    response = receive_checkLists_filleds(request)

    assert response.status_code == 200
    assert response.data == {"ok": False}
    save_log_mock.assert_called_once()


def test_receive_mobile_logs_api_returns_ok_on_success(api_user, monkeypatch):
    factory = APIRequestFactory()
    request = factory.post("/gerenciador/receive_mobile_logs_api/", [], format="json")
    force_authenticate(request, user=api_user)

    monkeypatch.setattr(
        "checklist.views.api.sync_api.validate_mobile_log_entries",
        Mock(return_value=[{"id": "1"}]),
    )
    save_logs_mock = Mock()
    monkeypatch.setattr("checklist.views.api.sync_api.api_services.save_mobile_logs", save_logs_mock)

    response = receive_mobile_logs_api(request)

    assert response.status_code == 200
    assert response.data == {"ok": True}
    save_logs_mock.assert_called_once_with([{"id": "1"}], request=request)
