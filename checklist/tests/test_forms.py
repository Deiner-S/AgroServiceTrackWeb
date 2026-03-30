import pytest

from checklist.forms import AddressForm, ClientForm, EmployeeForm
from checklist.models import Employee


@pytest.mark.django_db
def test_employee_form_rejects_invalid_name_cpf_phone_and_email():
    form = EmployeeForm(
        data={
            "first_name": "Joao1",
            "last_name": "Silva",
            "cpf": "12345678900",
            "phone": "11999999999",
            "email": "joao@empresa.org",
            "position": "1",
            "username": "JoaoSilva",
            "password": "senha123",
        }
    )

    assert not form.is_valid()
    assert "first_name" in form.errors
    assert "cpf" in form.errors
    assert "phone" in form.errors
    assert "email" in form.errors
    assert "username" in form.errors


@pytest.mark.django_db
def test_client_form_rejects_invalid_cnpj():
    form = ClientForm(
        data={
            "cnpj": "12345678000190",
            "name": "Cliente 1",
            "email": "cliente@empresa.com",
            "phone": "(11) 98765-4321",
        }
    )

    assert not form.is_valid()
    assert "cnpj" in form.errors
    assert "name" in form.errors


@pytest.mark.django_db
def test_address_form_rejects_invalid_street_city_and_zip_code():
    form = AddressForm(
        data={
            "street": "Rua das Flores, 10",
            "number": "10A",
            "complement": "Apto-2",
            "city": "Sao Paulo 2",
            "state": "SP",
            "zip_code": "12345678",
        }
    )

    assert not form.is_valid()
    assert "street" in form.errors
    assert "number" in form.errors
    assert "complement" in form.errors
    assert "city" in form.errors
    assert "state" in form.errors
    assert "zip_code" in form.errors


@pytest.mark.django_db
def test_address_form_accepts_empty_complement():
    form = AddressForm(
        data={
            "street": "Rua Projetada 12",
            "number": "10",
            "complement": "",
            "city": "Sao Paulo",
            "state": "Sao Paulo",
            "zip_code": "12345-678",
        }
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_address_form_renders_brazilian_state_choices():
    form = AddressForm()

    assert len(form.fields["state"].choices) == 27
    assert ("Sao Paulo", "Sao Paulo") in form.fields["state"].choices
    assert ("Distrito Federal", "Distrito Federal") in form.fields["state"].choices


@pytest.mark.django_db
def test_employee_form_limits_position_choices_for_manager():
    manager = Employee(username="gerente", position="1")

    form = EmployeeForm(actor=manager)

    assert form.fields["position"].choices == [
        ("2", "Administrativo"),
        ("3", "Técnico"),
    ]
