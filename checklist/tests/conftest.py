import pytest

from checklist.models import ChecklistItem, Client, WorkOrder


@pytest.fixture
def client_obj(db):
    return Client.objects.create(
        name="Cliente Teste",
        email="cliente@empresa.com",
        phone="(11) 98765-4321",
    )


@pytest.fixture
def work_order(client_obj):
    return WorkOrder.objects.create(
        operation_code="000001",
        symptoms="Falha no motor",
        client=client_obj,
    )


@pytest.fixture
def checklist_item(db):
    return ChecklistItem.objects.create(name="Verificar painel", status=1)
