import pytest
from types import SimpleNamespace

from checklist.services.api_services import (
    get_mobile_checklist_item_detail,
    get_mobile_employee_detail,
    get_pending_work_order,
    save_checklists_filleds,
    save_mobile_logs,
)


def test_get_pending_work_order_includes_status_sync(monkeypatch):
    work_order = SimpleNamespace(
        id="11111111-1111-4111-8111-111111111111",
        operation_code="000001",
        symptoms="Falha no motor",
        client=SimpleNamespace(name="Cliente 1"),
        status="1",
        chassi="1HGCM82633A123456",
        horimetro="1200",
        model="TRATORX",
        date_in=None,
        date_out=None,
        service=None,
        insert_date=None,
    )

    monkeypatch.setattr(
        "checklist.services.api_services.work_order_repository.list_pending_for_api_sync",
        lambda: [work_order],
    )

    response = get_pending_work_order()

    assert response[0]["operation_code"] == "000001"
    assert response[0]["status_sync"] == 1


def test_save_checklists_filleds_raises_when_status_is_missing(monkeypatch):
    employee = object()
    checklist_obj = SimpleNamespace(status=None, employee=None, image_in=None, image_out=None)

    monkeypatch.setattr(
        "checklist.services.api_services.employee_repository.get_by_identifier",
        lambda employee_id: employee,
    )
    monkeypatch.setattr(
        "checklist.services.api_services.checklist_repository.find_latest_by_work_order_and_item",
        lambda work_order, checklist_item: checklist_obj,
    )

    checklists = [
        {
            "id": "0f7bb3fe-6e84-4da5-aee8-6a6e263c4f4b",
            "work_order": object(),
            "checklist_item": object(),
            "status": None,
            "image_in": None,
            "image_out": None,
        }
    ]

    with pytest.raises(ValueError, match="Checklist status is required"):
        save_checklists_filleds(checklists, employee_id="funcionario-1")


def test_save_mobile_logs_writes_each_entry(monkeypatch):
    save_mobile_log_mock = []

    def capture_mobile_log(log_entry, request=None):
        save_mobile_log_mock.append((log_entry, request))

    monkeypatch.setattr("checklist.services.api_services.save_mobile_log", capture_mobile_log)

    logs = [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "osVersion": "35",
            "deviceModel": "Pixel 9",
            "user": "deiner",
            "erro": "falha",
            "stacktrace": "stack",
            "horario": "2026-03-31T12:00:00+00:00",
            "status_sync": 0,
        }
    ]

    request = object()
    save_mobile_logs(logs, request=request)

    assert save_mobile_log_mock == [(logs[0], request)]


def test_get_mobile_employee_detail_returns_toggle_permission(monkeypatch):
    employee = SimpleNamespace(
        id="11111111-1111-4111-8111-111111111111",
        username="tecnico",
        first_name="Tecnico",
        last_name="Campo",
        email="tecnico@example.com",
        cpf="123",
        phone="9999",
        position="3",
        get_position_display=lambda: "Tecnico",
        is_active=True,
        insert_date=None,
        addresses=SimpleNamespace(all=lambda: [], count=lambda: 0),
    )
    user = SimpleNamespace(position="1")

    monkeypatch.setattr(
        "checklist.services.api_services.employee_repository.get_by_identifier",
        lambda employee_id: employee,
    )

    response = get_mobile_employee_detail("11111111-1111-4111-8111-111111111111", user)

    assert response["permissions"]["canToggleStatus"] is True


def test_get_mobile_checklist_item_detail_returns_toggle_permission(monkeypatch):
    item = SimpleNamespace(
        id="11111111-1111-4111-8111-111111111111",
        name="Freio",
        status=1,
        executions=SimpleNamespace(count=lambda: 2),
        insert_date=None,
    )
    user = SimpleNamespace(position="1")

    monkeypatch.setattr(
        "checklist.services.api_services.checklist_item_repository.get_by_id",
        lambda item_id: item,
    )

    response = get_mobile_checklist_item_detail("11111111-1111-4111-8111-111111111111", user)

    assert response["permissions"]["canToggleStatus"] is True
