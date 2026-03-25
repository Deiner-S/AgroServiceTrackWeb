import re

from django.core.exceptions import ValidationError


ONLY_NUMBERS_PATTERN = re.compile(r"^\d+$")
ONLY_LETTERS_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ]+$")
ONLY_LETTERS_AND_SPACES_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ\s]+$")
LETTERS_AND_NUMBERS_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ0-9]+$")
LETTERS_NUMBERS_AND_SPACES_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ0-9\s]+$")
CPF_FORMAT_PATTERN = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
CNPJ_FORMAT_PATTERN = re.compile(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")
PHONE_FORMAT_PATTERN = re.compile(r"^\(\d{2}\) \d{4,5}-\d{4}$")
ZIP_CODE_FORMAT_PATTERN = re.compile(r"^\d{5}-\d{3}$")
EMAIL_FORMAT_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(com|com\.br)$"
)


def _validate_by_pattern(value, pattern, error_message):
    if not value or not pattern.fullmatch(value):
        raise ValidationError(error_message)
    return value


def validate_only_numbers(value):
    return _validate_by_pattern(value, ONLY_NUMBERS_PATTERN, "O valor deve conter somente numeros.")


def validate_only_letters(value):
    return _validate_by_pattern(value, ONLY_LETTERS_PATTERN, "O valor deve conter somente letras.")


def validate_only_letters_and_spaces(value):
    return _validate_by_pattern(
        value,
        ONLY_LETTERS_AND_SPACES_PATTERN,
        "O valor deve conter somente letras e espacos.",
    )


def validate_only_letters_and_numbers(value):
    return _validate_by_pattern(
        value,
        LETTERS_AND_NUMBERS_PATTERN,
        "O valor deve conter somente letras e numeros.",
    )


def validate_only_letters_numbers_and_spaces(value):
    return _validate_by_pattern(
        value,
        LETTERS_NUMBERS_AND_SPACES_PATTERN,
        "O valor deve conter somente letras, numeros e espacos.",
    )


def validate_cpf_format(value):
    return _validate_by_pattern(
        value,
        CPF_FORMAT_PATTERN,
        "CPF invalido. Use o formato XXX.XXX.XXX-YY.",
    )


def validate_cnpj_format(value):
    return _validate_by_pattern(
        value,
        CNPJ_FORMAT_PATTERN,
        "CNPJ invalido. Use o formato XX.XXX.XXX/YYYY-ZZ.",
    )


def validate_phone_format(value):
    return _validate_by_pattern(
        value,
        PHONE_FORMAT_PATTERN,
        "Telefone invalido. Use o formato (YY) XXXXX-XXXX ou (YY) XXXX-XXXX.",
    )


def validate_zip_code_format(value):
    return _validate_by_pattern(
        value,
        ZIP_CODE_FORMAT_PATTERN,
        "CEP invalido. Use o formato XXXXX-XXX.",
    )


def validate_email_format(value):
    return _validate_by_pattern(
        value,
        EMAIL_FORMAT_PATTERN,
        "Email invalido. Use o formato nome@dominio.com ou nome@dominio.com.br.",
    )
