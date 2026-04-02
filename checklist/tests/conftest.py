import pytest

from checklist.models import Address, ChecklistItem, Client, Employee, WorkOrder


@pytest.fixture
def client_obj(db):
    return Client.objects.create(
        cnpj="12.345.678/0001-90",
        name="Cliente Teste",
        email="cliente@empresa.com",
        phone="(11) 98765-4321",
    )


@pytest.fixture
def address_obj(db):
    return Address.objects.create(
        street="Rua Projetada 12",
        number="10",
        complement="",
        city="Sao Paulo",
        state="Sao Paulo",
        zip_code="12345-678",
    )


@pytest.fixture
def administrative_user(db):
    return Employee.objects.create_user(
        username="administrativo",
        password="senha123",
        position="2",
        cpf="123.456.789-10",
        phone="(11) 91234-5678",
        email="admin@empresa.com",
        first_name="Admin",
        last_name="Teste",
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
