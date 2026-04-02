import pytest

from checklist.models import Employee, WorkOrder
from checklist.repository.employee_repository import employee_repository
from checklist.repository.work_order_repository import work_order_repository


@pytest.mark.django_db
def test_work_order_repository_get_next_operation_code_uses_increment(client_obj):
    WorkOrder.objects.create(operation_code="000009", symptoms="Falha", client=client_obj)

    next_code = work_order_repository.get_next_operation_code()

    assert next_code == "000010"


@pytest.mark.django_db
def test_work_order_repository_list_for_panel_filters_by_status_and_search(client_obj):
    WorkOrder.objects.create(operation_code="000001", symptoms="Motor", client=client_obj, status="1")
    WorkOrder.objects.create(operation_code="000002", symptoms="Freio", client=client_obj, status="2", service="Servico")

    queryset = work_order_repository.list_for_panel(status_filter="2", search_query="Serv")

    assert list(queryset.values_list("operation_code", flat=True)) == ["000002"]


@pytest.mark.django_db
def test_work_order_repository_list_pending_for_api_sync_excludes_finalized(client_obj):
    WorkOrder.objects.create(operation_code="000001", symptoms="Motor", client=client_obj, status="1")
    WorkOrder.objects.create(operation_code="000002", symptoms="Freio", client=client_obj, status="4")

    queryset = work_order_repository.list_pending_for_api_sync()

    assert list(queryset.values_list("operation_code", flat=True)) == ["000001"]


@pytest.mark.django_db
def test_employee_repository_list_for_management_filters_by_query(django_user_model):
    Employee.objects.create_user(
        username="joao",
        password="secret123",
        first_name="Joao",
        last_name="Silva",
        email="joao@example.com",
        cpf="111",
        phone="9999",
        position="1",
    )
    Employee.objects.create_user(
        username="maria",
        password="secret123",
        first_name="Maria",
        last_name="Souza",
        email="maria@example.com",
        cpf="222",
        phone="9999",
        position="2",
    )

    queryset = employee_repository.list_for_management("Souza")

    assert list(queryset.values_list("username", flat=True)) == ["maria"]


@pytest.mark.django_db
def test_employee_repository_toggle_active_status_persists_change(django_user_model):
    employee = Employee.objects.create_user(
        username="inactive-user",
        password="secret123",
        email="inactive@example.com",
        cpf="333",
        phone="9999",
        position="2",
        is_active=True,
    )

    updated = employee_repository.toggle_active_status(employee)

    employee.refresh_from_db()
    assert updated.is_active is False
    assert employee.is_active is False


@pytest.mark.django_db
def test_employee_repository_find_inactive_by_username_returns_only_inactive(django_user_model):
    Employee.objects.create_user(
        username="target-user",
        password="secret123",
        email="active@example.com",
        cpf="444",
        phone="9999",
        position="2",
        is_active=True,
    )
    Employee.objects.create_user(
        username="inactive-target",
        password="secret123",
        email="inactive@example.com",
        cpf="555",
        phone="9999",
        position="2",
        is_active=False,
    )

    assert employee_repository.find_inactive_by_username("target-user") is None
    assert employee_repository.find_inactive_by_username("inactive-target").username == "inactive-target"
