import pytest
from types import SimpleNamespace

from checklist.services.api_services import save_checklists_filleds, save_mobile_logs


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
