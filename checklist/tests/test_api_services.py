import pytest
from types import SimpleNamespace

from checklist.services.api_services import (
    create_mobile_checklist_item,
    create_mobile_client_address,
    create_mobile_client_order,
    create_mobile_employee_address,
    delete_mobile_checklist_item,
    delete_mobile_employee_address,
    get_mobile_dashboard,
    get_mobile_checklist_item_detail,
    get_mobile_client_detail,
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


def test_save_mobile_logs_propagates_persistence_failure(monkeypatch):
    monkeypatch.setattr(
        "checklist.services.api_services.save_mobile_log",
        lambda log_entry, request=None: (_ for _ in ()).throw(RuntimeError("disk down")),
    )

    with pytest.raises(RuntimeError, match="disk down"):
        save_mobile_logs(
            [
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
            ],
            request=object(),
        )


@pytest.mark.django_db
def test_get_mobile_client_detail_includes_permissions_and_next_operation_code(
    client_obj,
    work_order,
    administrative_user,
):
    detail = get_mobile_client_detail(str(client_obj.id), administrative_user)

    assert detail["id"] == str(client_obj.id)
    assert detail["permissions"]["canEditClient"] is True
    assert detail["permissions"]["canManageAddresses"] is True
    assert detail["permissions"]["canCreateServiceOrder"] is True
    assert detail["permissions"]["nextOperationCode"] == "000002"


@pytest.mark.django_db
def test_create_mobile_client_address_links_address_to_client(client_obj, address_obj):
    create_mobile_client_address(client_obj, address_obj)

    client_obj.refresh_from_db()

    assert client_obj.addresses.count() == 1
    assert str(client_obj.addresses.first()) == "Rua Projetada 12, 10 - Sao Paulo/Sao Paulo"


@pytest.mark.django_db
def test_create_mobile_client_order_links_order_to_client(client_obj):
    order = SimpleNamespace(
        operation_code="000001",
        symptoms="Falha hidraulica",
        client=None,
        save=lambda *args, **kwargs: None,
    )

    saved = create_mobile_client_order(client_obj, order)

    assert saved.client == client_obj


@pytest.mark.django_db
def test_get_mobile_employee_detail_includes_permissions_and_position_options(
    technical_employee,
    manager_user,
):
    detail = get_mobile_employee_detail(str(technical_employee.id), manager_user)

    assert detail["id"] == str(technical_employee.id)
    assert detail["permissions"]["canEditEmployee"] is True
    assert detail["permissions"]["canManageAddresses"] is True
    assert detail["permissions"]["canToggleStatus"] is True
    assert [option["value"] for option in detail["positionOptions"]] == ["2", "3"]


@pytest.mark.django_db
def test_create_mobile_employee_address_links_address_to_employee(technical_employee, address_obj):
    create_mobile_employee_address(technical_employee, address_obj)

    technical_employee.refresh_from_db()

    assert technical_employee.addresses.count() == 1
    assert str(technical_employee.addresses.first()) == "Rua Projetada 12, 10 - Sao Paulo/Sao Paulo"


@pytest.mark.django_db
def test_delete_mobile_employee_address_unlinks_address_from_employee(technical_employee, address_obj):
    technical_employee.addresses.add(address_obj)

    delete_mobile_employee_address(technical_employee, address_obj)
    technical_employee.refresh_from_db()

    assert technical_employee.addresses.count() == 0


@pytest.mark.django_db
def test_create_mobile_checklist_item_persists_item():
    checklist_item = SimpleNamespace(
        name="Freio",
        save=lambda *args, **kwargs: None,
    )

    saved = create_mobile_checklist_item(checklist_item)

    assert saved.name == "Freio"


@pytest.mark.django_db
def test_get_mobile_checklist_item_detail_includes_delete_permission(checklist_item, db):
    from checklist.models import Employee

    manager_user = Employee.objects.create_user(
        username="gerente_checklist",
        password="senha123",
        position="1",
        cpf="123.456.789-11",
        phone="(11) 91234-5678",
        email="gerente.checklist@empresa.com",
        first_name="Gerente",
        last_name="Checklist",
    )

    detail = get_mobile_checklist_item_detail(str(checklist_item.id), manager_user)

    assert detail["id"] == str(checklist_item.id)
    assert detail["permissions"]["canToggleStatus"] is True
    assert detail["permissions"]["canDeleteChecklistItem"] is True


@pytest.mark.django_db
def test_delete_mobile_checklist_item_removes_record(checklist_item):
    delete_mobile_checklist_item(str(checklist_item.id))

    with pytest.raises(Exception):
        checklist_item.refresh_from_db()


@pytest.mark.django_db
def test_get_mobile_dashboard_includes_offline_session_metadata(manager_user):
    payload = get_mobile_dashboard(manager_user)

    assert payload["user"]["username"] == manager_user.username
    assert payload["session"]["permissionVersion"] == "mobile-management-v1"
    assert payload["session"]["scope"] == ["mobile:management"]
    assert payload["session"]["validatedAt"] < payload["session"]["offlineSessionExpiresAt"]
