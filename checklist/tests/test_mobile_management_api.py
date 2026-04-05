from unittest.mock import Mock

from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate

from checklist.views.api.mobile_management_api import (
    mobile_add_employee_address_api,
    mobile_checklist_item_detail_api,
    mobile_checklist_items_api,
    mobile_client_detail_api,
    mobile_clients_api,
    mobile_delete_employee_address_api,
    mobile_dashboard_api,
    mobile_employee_detail_api,
    mobile_employees_api,
    mobile_toggle_checklist_item_status_api,
    mobile_toggle_employee_status_api,
)


def create_user(django_user_model, username, position):
    return django_user_model.objects.create_user(
        username=username,
        password="secret123",
        position=position,
        cpf=f"cpf-{username}",
        phone="999999",
    )


def test_mobile_dashboard_api_returns_service_payload(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "director", "0")
    factory = APIRequestFactory()
    request = factory.get("/gerenciador/mobile/dashboard_api/")
    force_authenticate(request, user=user)

    monkeypatch.setattr(
        "checklist.views.api.mobile_management_api.api_services.get_mobile_dashboard",
        Mock(return_value={"summary": {"pendingOrders": 1}}),
    )

    response = mobile_dashboard_api(request)

    assert response.status_code == 200
    assert response.data == {"summary": {"pendingOrders": 1}}


def test_mobile_clients_api_blocks_user_without_permission(db, django_user_model):
    user = create_user(django_user_model, "tech", "3")
    factory = APIRequestFactory()
    request = factory.get("/gerenciador/mobile/clients_api/")
    force_authenticate(request, user=user)

    response = mobile_clients_api(request)

    assert response.status_code == 400
    assert response.data["ok"] is False


def test_mobile_clients_api_validates_query_and_calls_service(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "manager", "1")
    factory = APIRequestFactory()
    request = factory.get("/gerenciador/mobile/clients_api/?search= cliente ")
    force_authenticate(request, user=user)

    service_mock = Mock(return_value=[{"id": "1"}])
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.get_mobile_clients", service_mock)

    response = mobile_clients_api(request)

    assert response.status_code == 200
    assert response.data == [{"id": "1"}]
    service_mock.assert_called_once_with("cliente")


def test_mobile_client_detail_api_returns_validation_error_for_invalid_identifier(db, django_user_model):
    user = create_user(django_user_model, "admin", "2")
    factory = APIRequestFactory()
    request = factory.get("/gerenciador/mobile/clients_api/bad/detail/")
    force_authenticate(request, user=user)

    response = mobile_client_detail_api(request, "bad-id")

    assert response.status_code == 400
    assert response.data["ok"] is False


def test_mobile_employees_api_returns_service_payload(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "director2", "0")
    factory = APIRequestFactory()
    request = factory.get("/gerenciador/mobile/employees_api/")
    force_authenticate(request, user=user)

    service_mock = Mock(return_value=[{"id": "emp-1"}])
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.get_mobile_employees", service_mock)

    response = mobile_employees_api(request)

    assert response.status_code == 200
    assert response.data == [{"id": "emp-1"}]


def test_mobile_employee_detail_api_returns_service_payload(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "manager2", "1")
    employee_id = "11111111-1111-4111-8111-111111111111"
    factory = APIRequestFactory()
    request = factory.get(f"/gerenciador/mobile/employees_api/{employee_id}/detail/")
    force_authenticate(request, user=user)

    employee = type("Employee", (), {"position": "3"})()
    monkeypatch.setattr(
        "checklist.views.api.mobile_management_api.employee_repository.get_by_identifier",
        Mock(return_value=employee),
    )
    service_mock = Mock(return_value={
        "id": employee_id,
        "permissions": {
            "canEditEmployee": True,
            "canManageAddresses": True,
            "canToggleStatus": True,
        },
        "positionOptions": [{"value": "3", "label": "Tecnico"}],
    })
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.get_mobile_employee_detail", service_mock)

    response = mobile_employee_detail_api(request, employee_id)

    assert response.status_code == 200
    assert response.data["permissions"]["canToggleStatus"] is True
    service_mock.assert_called_once_with(employee_id, user)


def test_mobile_employee_detail_api_updates_employee_and_returns_detail(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "director6", "0")
    employee_id = "11111111-1111-4111-8111-111111111111"
    factory = APIRequestFactory()
    request = factory.patch(
        f"/gerenciador/mobile/employees_api/{employee_id}/detail/",
        {
            "first_name": "Deiner",
            "last_name": "Silva",
            "cpf": "123.456.789-00",
            "phone": "(11) 98765-4321",
            "email": "deiner@example.com",
            "position": "3",
            "username": "deiner",
            "password": "",
        },
        format="json",
    )
    force_authenticate(request, user=user)

    employee = type("Employee", (), {"id": employee_id, "position": "3", "set_password": lambda self, value: None})()
    form_instance = Mock()
    form_instance.is_valid.return_value = True
    form_instance.cleaned_data = {"password": ""}
    form_instance.save.return_value = employee

    monkeypatch.setattr(
        "checklist.views.api.mobile_management_api.employee_repository.get_by_identifier",
        Mock(return_value=employee),
    )
    monkeypatch.setattr("checklist.views.api.mobile_management_api.EmployeeDetailForm", Mock(return_value=form_instance))
    update_mock = Mock(return_value=employee)
    detail_mock = Mock(return_value={"id": employee_id})
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.update_mobile_employee", update_mock)
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.get_mobile_employee_detail", detail_mock)

    response = mobile_employee_detail_api(request, employee_id)

    assert response.status_code == 200
    update_mock.assert_called_once_with(employee)
    detail_mock.assert_called_once_with(employee_id, user)


def test_mobile_add_employee_address_api_returns_updated_detail(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "director7", "0")
    employee_id = "11111111-1111-4111-8111-111111111111"
    factory = APIRequestFactory()
    request = factory.post(
        f"/gerenciador/mobile/employees_api/{employee_id}/addresses/",
        {
            "street": "Rua A",
            "number": "10",
            "complement": "",
            "city": "Sao Paulo",
            "state": "Sao Paulo",
            "zip_code": "12345-678",
        },
        format="json",
    )
    force_authenticate(request, user=user)

    employee = type("Employee", (), {"position": "3"})()
    form_instance = Mock()
    form_instance.is_valid.return_value = True
    form_instance.save.return_value = object()

    monkeypatch.setattr(
        "checklist.views.api.mobile_management_api.employee_repository.get_by_identifier",
        Mock(return_value=employee),
    )
    monkeypatch.setattr("checklist.views.api.mobile_management_api.AddressForm", Mock(return_value=form_instance))
    create_mock = Mock()
    detail_mock = Mock(return_value={"id": employee_id, "addresses": []})
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.create_mobile_employee_address", create_mock)
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.get_mobile_employee_detail", detail_mock)

    response = mobile_add_employee_address_api(request, employee_id)

    assert response.status_code == 201
    create_mock.assert_called_once()
    detail_mock.assert_called_once_with(employee_id, user)


def test_mobile_delete_employee_address_api_returns_updated_detail(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "director8", "0")
    employee_id = "11111111-1111-4111-8111-111111111111"
    address_id = "22222222-2222-4222-8222-222222222222"
    factory = APIRequestFactory()
    request = factory.delete(f"/gerenciador/mobile/employees_api/{employee_id}/addresses/{address_id}/")
    force_authenticate(request, user=user)

    employee = type("Employee", (), {"position": "3"})()
    address = object()

    monkeypatch.setattr(
        "checklist.views.api.mobile_management_api.employee_repository.get_by_identifier",
        Mock(return_value=employee),
    )
    monkeypatch.setattr(
        "checklist.views.api.mobile_management_api.address_repository.get_by_id",
        Mock(return_value=address),
    )
    delete_mock = Mock(return_value={"ok": True})
    detail_mock = Mock(return_value={"id": employee_id, "addresses": []})
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.delete_mobile_employee_address", delete_mock)
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.get_mobile_employee_detail", detail_mock)

    response = mobile_delete_employee_address_api(request, employee_id, address_id)

    assert response.status_code == 200
    delete_mock.assert_called_once_with(employee, address)
    detail_mock.assert_called_once_with(employee_id, user)


def test_mobile_toggle_employee_status_api_handles_missing_employee(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "director3", "0")
    employee_id = "11111111-1111-4111-8111-111111111111"
    factory = APIRequestFactory()
    request = factory.post(f"/gerenciador/mobile/employees_api/{employee_id}/toggle-status/")
    force_authenticate(request, user=user)

    monkeypatch.setattr(
        "checklist.views.api.mobile_management_api.employee_repository.get_by_identifier",
        Mock(return_value=({"error": "not found"}, 404)),
    )

    response = mobile_toggle_employee_status_api(request, employee_id)

    assert response.status_code == 400
    assert response.data["error"] == "Funcionario nao encontrado."


def test_mobile_toggle_employee_status_api_checks_permission_before_service_call(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "manager3", "1")
    employee_id = "11111111-1111-4111-8111-111111111111"
    factory = APIRequestFactory()
    request = factory.post(f"/gerenciador/mobile/employees_api/{employee_id}/toggle-status/")
    force_authenticate(request, user=user)

    employee = type("Employee", (), {"position": "0"})()
    monkeypatch.setattr(
        "checklist.views.api.mobile_management_api.employee_repository.get_by_identifier",
        Mock(return_value=employee),
    )
    service_mock = Mock(return_value={"ok": True})
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.toggle_mobile_employee_status", service_mock)

    response = mobile_toggle_employee_status_api(request, employee_id)

    assert response.status_code == 400
    assert response.data["ok"] is False
    service_mock.assert_not_called()


def test_mobile_checklist_items_api_returns_service_payload(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "director4", "0")
    factory = APIRequestFactory()
    request = factory.get("/gerenciador/mobile/checklist_items_api/?search=freio")
    force_authenticate(request, user=user)

    service_mock = Mock(return_value=[{"id": "item-1"}])
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.get_mobile_checklist_items", service_mock)

    response = mobile_checklist_items_api(request)

    assert response.status_code == 200
    assert response.data == [{"id": "item-1"}]
    service_mock.assert_called_once_with("freio")


def test_mobile_checklist_items_api_creates_item_and_returns_detail(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "director9", "0")
    factory = APIRequestFactory()
    request = factory.post(
        "/gerenciador/mobile/checklist_items_api/",
        {"name": "Freio"},
        format="json",
    )
    force_authenticate(request, user=user)

    checklist_item = type("ChecklistItem", (), {"id": "11111111-1111-4111-8111-111111111111"})()
    form_instance = Mock()
    form_instance.is_valid.return_value = True
    form_instance.save.return_value = checklist_item

    monkeypatch.setattr("checklist.views.api.mobile_management_api.ChecklistItemForm", Mock(return_value=form_instance))
    create_mock = Mock(return_value=checklist_item)
    detail_mock = Mock(return_value={"id": str(checklist_item.id)})
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.create_mobile_checklist_item", create_mock)
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.get_mobile_checklist_item_detail", detail_mock)

    response = mobile_checklist_items_api(request)

    assert response.status_code == 201
    create_mock.assert_called_once_with(checklist_item)
    detail_mock.assert_called_once_with(str(checklist_item.id), user)


def test_mobile_checklist_item_detail_api_blocks_user_without_permission(db, django_user_model):
    user = create_user(django_user_model, "admin2", "2")
    item_id = "11111111-1111-4111-8111-111111111111"
    factory = APIRequestFactory()
    request = factory.get(f"/gerenciador/mobile/checklist_items_api/{item_id}/detail/")
    force_authenticate(request, user=user)

    response = mobile_checklist_item_detail_api(request, item_id)

    assert response.status_code == 400
    assert response.data["ok"] is False


def test_mobile_checklist_item_detail_api_passes_authenticated_user_to_service(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "director5", "0")
    item_id = "11111111-1111-4111-8111-111111111111"
    factory = APIRequestFactory()
    request = factory.get(f"/gerenciador/mobile/checklist_items_api/{item_id}/detail/")
    force_authenticate(request, user=user)

    service_mock = Mock(return_value={"id": item_id, "permissions": {"canToggleStatus": True, "canDeleteChecklistItem": True}})
    monkeypatch.setattr(
        "checklist.views.api.mobile_management_api.api_services.get_mobile_checklist_item_detail",
        service_mock,
    )

    response = mobile_checklist_item_detail_api(request, item_id)

    assert response.status_code == 200
    assert response.data["permissions"]["canToggleStatus"] is True
    service_mock.assert_called_once_with(item_id, user)


def test_mobile_checklist_item_detail_api_deletes_item(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "director10", "0")
    item_id = "11111111-1111-4111-8111-111111111111"
    factory = APIRequestFactory()
    request = factory.delete(f"/gerenciador/mobile/checklist_items_api/{item_id}/detail/")
    force_authenticate(request, user=user)

    delete_mock = Mock(return_value={"ok": True})
    monkeypatch.setattr("checklist.views.api.mobile_management_api.api_services.delete_mobile_checklist_item", delete_mock)

    response = mobile_checklist_item_detail_api(request, item_id)

    assert response.status_code == 200
    assert response.data == {"ok": True}
    delete_mock.assert_called_once_with(item_id)


def test_mobile_toggle_checklist_item_status_api_returns_validation_error(db, django_user_model, monkeypatch):
    user = create_user(django_user_model, "manager4", "1")
    item_id = "11111111-1111-4111-8111-111111111111"
    factory = APIRequestFactory()
    request = factory.post(f"/gerenciador/mobile/checklist_items_api/{item_id}/toggle-status/")
    force_authenticate(request, user=user)

    monkeypatch.setattr(
        "checklist.views.api.mobile_management_api.api_services.toggle_mobile_checklist_item_status",
        Mock(side_effect=ValidationError("falha de validacao")),
    )

    response = mobile_toggle_checklist_item_status_api(request, item_id)

    assert response.status_code == 400
    assert response.data == {"ok": False, "error": "falha de validacao"}
