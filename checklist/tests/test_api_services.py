import pytest
from types import SimpleNamespace

from checklist.services.api_services import save_checklists_filleds


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
