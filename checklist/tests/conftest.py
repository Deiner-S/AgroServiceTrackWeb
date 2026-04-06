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
def manager_user(db):
    return Employee.objects.create_user(
        username="gerente",
        password="senha123",
        position="1",
        cpf="123.456.789-12",
        phone="(11) 92345-6789",
        email="gerente@empresa.com",
        first_name="Gerente",
        last_name="Teste",
    )


@pytest.fixture
def technical_employee(db):
    return Employee.objects.create_user(
        username="tecnico",
        password="senha123",
        position="3",
        cpf="123.456.789-13",
        phone="(11) 93456-7890",
        email="tecnico@empresa.com",
        first_name="Tecnico",
        last_name="Campo",
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
