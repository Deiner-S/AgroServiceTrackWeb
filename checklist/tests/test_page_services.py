from types import SimpleNamespace

import pytest

from checklist.services import (
    address_page_services,
    client_page_services,
    employee_page_services,
    service_order_page_services,
)


def test_get_client_list_context_uses_pagination(monkeypatch):
    monkeypatch.setattr(
        "checklist.services.client_page_services.client_repository.list_for_management",
        lambda search_query: ["client-1", "client-2"],
    )
    monkeypatch.setattr(
        "checklist.services.client_page_services.paginate_items",
        lambda items, page_number: {"items": items, "page": page_number},
    )

    context = client_page_services.get_client_list_context(search_query="cli", page_number="2")

    assert context == {"page_client": {"items": ["client-1", "client-2"], "page": "2"}, "current_search": "cli"}


def test_get_client_detail_context_combines_services_and_addresses(monkeypatch):
    client = SimpleNamespace(id="c-1")
    form = object()
    monkeypatch.setattr(
        "checklist.services.client_page_services.work_order_repository.list_by_client",
        lambda current_client: ["os-1"],
    )
    monkeypatch.setattr(
        "checklist.services.client_page_services.get_address_section_context",
        lambda current_client, entity_kind: {"addresses": ["addr-1"], "entity_kind": entity_kind},
    )

    context = client_page_services.get_client_detail_context(
        client=client,
        form=form,
        search_query="motor",
        page_number="3",
    )

    assert context["client"] is client
    assert context["form"] is form
    assert context["services"] == ["os-1"]
    assert context["addresses"] == ["addr-1"]


def test_prepare_employee_helpers_apply_password_when_present():
    calls = []
    employee = SimpleNamespace(set_password=lambda password: calls.append(password))

    assert employee_page_services.prepare_new_employee(employee, "secret") is employee
    assert employee_page_services.prepare_employee_update(employee, None) is employee
    assert employee_page_services.prepare_employee_update(employee, "new-secret") is employee
    assert calls == ["secret", "new-secret"]


def test_toggle_employee_status_delegates_to_repository(monkeypatch):
    employee = SimpleNamespace(id="emp-1", is_active=True)
    monkeypatch.setattr(
        "checklist.services.employee_page_services.employee_repository.get_by_id",
        lambda employee_id: employee,
    )
    monkeypatch.setattr(
        "checklist.services.employee_page_services.employee_repository.toggle_active_status",
        lambda current_employee: SimpleNamespace(id=current_employee.id, is_active=False),
    )

    updated = employee_page_services.toggle_employee_status("emp-1")

    assert updated.id == "emp-1"
    assert updated.is_active is False


def test_address_page_services_create_and_delete_for_client(monkeypatch):
    client = SimpleNamespace(id="client-1")
    address = SimpleNamespace(id="addr-1")
    calls = []

    monkeypatch.setattr(
        "checklist.services.address_page_services.address_repository.save",
        lambda current_address: address,
    )
    monkeypatch.setattr(
        "checklist.services.address_page_services.address_repository.add_to_client",
        lambda current_client, current_address: calls.append(("add", current_client.id, current_address.id)),
    )
    monkeypatch.setattr(
        "checklist.services.address_page_services.address_repository.remove_from_client",
        lambda current_client, current_address: calls.append(("remove", current_client.id, current_address.id)),
    )
    monkeypatch.setattr(
        "checklist.services.address_page_services.address_repository.delete_if_orphan",
        lambda current_address: calls.append(("delete_if_orphan", current_address.id)),
    )

    saved = address_page_services.create_address_for_client(client, address)
    address_page_services.delete_address_from_client(client, address)

    assert saved is address
    assert calls == [
        ("add", "client-1", "addr-1"),
        ("remove", "client-1", "addr-1"),
        ("delete_if_orphan", "addr-1"),
    ]


def test_service_panel_context_normalizes_invalid_status(monkeypatch):
    monkeypatch.setattr(
        "checklist.services.service_order_page_services.work_order_repository.list_for_panel",
        lambda **kwargs: ["os-1", kwargs["status_filter"], kwargs["search_query"]],
    )

    context = service_order_page_services.get_service_panel_context(
        status_filter="9",
        search_query="motor",
    )

    assert context["orders"] == ["os-1", "all", "motor"]
    assert context["selected_status"] == "all"
    assert context["current_search"] == "motor"


def test_service_order_detail_context_returns_selected_filters(monkeypatch):
    order = SimpleNamespace(id="order-1")
    monkeypatch.setattr(
        "checklist.services.service_order_page_services.work_order_repository.get_detail_by_id",
        lambda order_id: order,
    )

    context = service_order_page_services.get_service_order_detail_context(
        order_id="order-1",
        search_query="cliente",
        status_filter="2",
    )

    assert context == {
        "order": order,
        "current_search": "cliente",
        "selected_status": "2",
    }
