import pytest
from django.core.exceptions import ValidationError

from checklist.utils.validation_utils import (
    validate_cnpj_format,
    validate_cpf_format,
    validate_email_format,
    validate_only_letters,
    validate_only_letters_and_numbers,
    validate_only_letters_and_spaces,
    validate_only_letters_numbers_and_spaces,
    validate_only_lowercase_letters,
    validate_only_numbers,
    validate_phone_format,
    validate_zip_code_format,
)


def test_validate_only_numbers():
    assert validate_only_numbers("123456") == "123456"

    with pytest.raises(ValidationError):
        validate_only_numbers("123a")

    with pytest.raises(ValidationError):
        validate_only_numbers("123 456")


def test_validate_only_letters_and_spaces():
    assert validate_only_letters_and_spaces("Belo Horizonte") == "Belo Horizonte"
    assert validate_only_letters_and_spaces("Maria Clara") == "Maria Clara"

    with pytest.raises(ValidationError):
        validate_only_letters_and_spaces("Cidade 2")


def test_validate_only_letters():
    assert validate_only_letters("Joao") == "Joao"
    assert validate_only_letters("Jo\u00e3o") == "Jo\u00e3o"

    with pytest.raises(ValidationError):
        validate_only_letters("Joao 2")

    with pytest.raises(ValidationError):
        validate_only_letters("Joao Silva")


def test_validate_only_lowercase_letters():
    assert validate_only_lowercase_letters("joaosilva") == "joaosilva"

    with pytest.raises(ValidationError):
        validate_only_lowercase_letters("joao silva")

    with pytest.raises(ValidationError):
        validate_only_lowercase_letters("Joao")

    with pytest.raises(ValidationError):
        validate_only_lowercase_letters("joao123")


def test_validate_only_letters_and_numbers():
    assert validate_only_letters_and_numbers("Agro123") == "Agro123"
    assert validate_only_letters_and_numbers("Jo\u00e3o2026") == "Jo\u00e3o2026"

    with pytest.raises(ValidationError):
        validate_only_letters_and_numbers("Agro 123")

    with pytest.raises(ValidationError):
        validate_only_letters_and_numbers("Agro-123")


def test_validate_only_letters_numbers_and_spaces():
    assert (
        validate_only_letters_numbers_and_spaces("Rua Projetada 12")
        == "Rua Projetada 12"
    )

    with pytest.raises(ValidationError):
        validate_only_letters_numbers_and_spaces("Rua Projetada, 12")


def test_validate_cpf_format():
    assert validate_cpf_format("123.456.789-00") == "123.456.789-00"

    with pytest.raises(ValidationError):
        validate_cpf_format("12345678900")

    with pytest.raises(ValidationError):
        validate_cpf_format("123.456.789/00")


def test_validate_cnpj_format():
    assert validate_cnpj_format("12.345.678/0001-90") == "12.345.678/0001-90"

    with pytest.raises(ValidationError):
        validate_cnpj_format("12345678000190")

    with pytest.raises(ValidationError):
        validate_cnpj_format("12.345.678-0001/90")


def test_validate_phone_format():
    assert validate_phone_format("(11) 98765-4321") == "(11) 98765-4321"
    assert validate_phone_format("(11) 8765-4321") == "(11) 8765-4321"

    with pytest.raises(ValidationError):
        validate_phone_format("11987654321")

    with pytest.raises(ValidationError):
        validate_phone_format("(11)98765-4321")


def test_validate_email_format():
    assert validate_email_format("nome@dominio.com") == "nome@dominio.com"
    assert validate_email_format("nome@dominio.com.br") == "nome@dominio.com.br"

    with pytest.raises(ValidationError):
        validate_email_format("nome@dominio.org")

    with pytest.raises(ValidationError):
        validate_email_format("nome.dominio.com")


def test_validate_zip_code_format():
    assert validate_zip_code_format("12345-678") == "12345-678"

    with pytest.raises(ValidationError):
        validate_zip_code_format("12345678")
