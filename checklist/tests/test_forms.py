import pytest

from checklist.forms import AddressForm, ClientForm, EmployeeForm


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
            "city": "Sao Paulo 2",
            "state": "SP",
            "zip_code": "12345678",
        }
    )

    assert not form.is_valid()
    assert "street" in form.errors
    assert "number" in form.errors
    assert "city" in form.errors
    assert "zip_code" in form.errors
