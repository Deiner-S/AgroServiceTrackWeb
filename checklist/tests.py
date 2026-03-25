import uuid

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from checklist.api_payload_validation import (
    validate_checklist_entries,
    validate_work_order_entries,
)
from checklist.forms import AddressForm, ClientForm, EmployeeForm
from checklist.models import ChecklistItem, Client, WorkOrder
from checklist.exception_handler import (
    get_validation_error_message,
    handle_validation_exceptions,
)
from checklist.utils.validation_utils import (
    validate_cnpj_format,
    validate_cpf_format,
    validate_email_format,
    validate_only_letters_and_numbers,
    validate_only_letters_and_spaces,
    validate_only_lowercase_letters,
    validate_only_letters_numbers_and_spaces,
    validate_only_numbers,
    validate_phone_format,
    validate_zip_code_format,
)


class ValidationUtilsTests(SimpleTestCase):
    def test_validate_only_numbers(self):
        self.assertEqual(validate_only_numbers("123456"), "123456")
        with self.assertRaises(ValidationError):
            validate_only_numbers("123a")
        with self.assertRaises(ValidationError):
            validate_only_numbers("123 456")

    def test_validate_only_letters_and_spaces(self):
        self.assertEqual(validate_only_letters_and_spaces("Belo Horizonte"), "Belo Horizonte")
        self.assertEqual(validate_only_letters_and_spaces("Maria Clara"), "Maria Clara")
        with self.assertRaises(ValidationError):
            validate_only_letters_and_spaces("Cidade 2")

    def test_validate_only_lowercase_letters(self):
        self.assertEqual(validate_only_lowercase_letters("joaosilva"), "joaosilva")
        with self.assertRaises(ValidationError):
            validate_only_lowercase_letters("joao silva")
        with self.assertRaises(ValidationError):
            validate_only_lowercase_letters("Joao")
        with self.assertRaises(ValidationError):
            validate_only_lowercase_letters("joao123")

    def test_validate_only_letters_and_numbers(self):
        self.assertEqual(validate_only_letters_and_numbers("Agro123"), "Agro123")
        self.assertEqual(validate_only_letters_and_numbers("João2026"), "João2026")
        with self.assertRaises(ValidationError):
            validate_only_letters_and_numbers("Agro 123")
        with self.assertRaises(ValidationError):
            validate_only_letters_and_numbers("Agro-123")

    def test_validate_only_letters_numbers_and_spaces(self):
        self.assertEqual(
            validate_only_letters_numbers_and_spaces("Rua Projetada 12"),
            "Rua Projetada 12",
        )
        with self.assertRaises(ValidationError):
            validate_only_letters_numbers_and_spaces("Rua Projetada, 12")

    def test_validate_cpf_format(self):
        self.assertEqual(validate_cpf_format("123.456.789-00"), "123.456.789-00")
        with self.assertRaises(ValidationError):
            validate_cpf_format("12345678900")
        with self.assertRaises(ValidationError):
            validate_cpf_format("123.456.789/00")

    def test_validate_cnpj_format(self):
        self.assertEqual(validate_cnpj_format("12.345.678/0001-90"), "12.345.678/0001-90")
        with self.assertRaises(ValidationError):
            validate_cnpj_format("12345678000190")
        with self.assertRaises(ValidationError):
            validate_cnpj_format("12.345.678-0001/90")

    def test_validate_phone_format(self):
        self.assertEqual(validate_phone_format("(11) 98765-4321"), "(11) 98765-4321")
        self.assertEqual(validate_phone_format("(11) 8765-4321"), "(11) 8765-4321")
        with self.assertRaises(ValidationError):
            validate_phone_format("11987654321")
        with self.assertRaises(ValidationError):
            validate_phone_format("(11)98765-4321")

    def test_validate_email_format(self):
        self.assertEqual(validate_email_format("nome@dominio.com"), "nome@dominio.com")
        self.assertEqual(validate_email_format("nome@dominio.com.br"), "nome@dominio.com.br")
        with self.assertRaises(ValidationError):
            validate_email_format("nome@dominio.org")
        with self.assertRaises(ValidationError):
            validate_email_format("nome.dominio.com")

    def test_validate_zip_code_format(self):
        self.assertEqual(validate_zip_code_format("12345-678"), "12345-678")
        with self.assertRaises(ValidationError):
            validate_zip_code_format("12345678")


class FormValidationTests(TestCase):
    def test_employee_form_rejects_invalid_name_cpf_phone_and_email(self):
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

        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("cpf", form.errors)
        self.assertIn("phone", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("username", form.errors)

    def test_client_form_rejects_invalid_cnpj(self):
        form = ClientForm(
            data={
                "cnpj": "12345678000190",
                "name": "Cliente 1",
                "email": "cliente@empresa.com",
                "phone": "(11) 98765-4321",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("cnpj", form.errors)
        self.assertIn("name", form.errors)

    def test_address_form_rejects_invalid_street_city_and_zip_code(self):
        form = AddressForm(
            data={
                "street": "Rua das Flores, 10",
                "number": "10A",
                "city": "Sao Paulo 2",
                "state": "SP",
                "zip_code": "12345678",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("street", form.errors)
        self.assertIn("number", form.errors)
        self.assertIn("city", form.errors)
        self.assertIn("zip_code", form.errors)


class ValidationExceptionHandlerTests(SimpleTestCase):
    def test_get_validation_error_message_from_messages(self):
        exc = ValidationError(["Erro um", "Erro dois"])
        self.assertEqual(get_validation_error_message(exc), "Erro um Erro dois")

    def test_get_validation_error_message_from_message_dict(self):
        exc = ValidationError({"cpf": ["CPF invalido"], "email": ["Email invalido"]})
        self.assertEqual(get_validation_error_message(exc), "CPF invalido Email invalido")

    def test_handle_validation_exceptions_returns_error_payload(self):
        @handle_validation_exceptions
        def run_validation():
            raise ValidationError("CPF invalido")

        self.assertEqual(run_validation(), ({"error": "CPF invalido"}, 400))


class ApiPayloadValidationTests(TestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(
            name="Cliente Teste",
            email="cliente@empresa.com",
            phone="(11) 98765-4321",
        )
        self.work_order = WorkOrder.objects.create(
            operation_code="000001",
            symptoms="Falha no motor",
            client=self.client_obj,
        )
        self.checklist_item = ChecklistItem.objects.create(name="Verificar painel", status=1)

    def test_validate_work_order_entries_returns_normalized_payload(self):
        payload = [
            {
                "operation_code": "000001",
                "chassi": "1HGCM82633A123456",
                "horimetro": "12345",
                "model": "Trator2025",
                "date_in": "2026-03-25T10:00:00",
                "date_out": "2026-03-25T11:00:00",
                "status": "2",
                "service": "Troca completa",
            }
        ]

        validated = validate_work_order_entries(payload)

        self.assertEqual(validated[0]["work_order"].id, self.work_order.id)
        self.assertEqual(validated[0]["chassi"], "1HGCM82633A123456")
        self.assertEqual(validated[0]["status"], "2")

    def test_validate_work_order_entries_rejects_invalid_chassi(self):
        payload = [
            {
                "operation_code": "000001",
                "chassi": "ABC-123",
                "horimetro": "12345",
                "model": "Trator2025",
                "date_in": "2026-03-25T10:00:00",
                "date_out": "2026-03-25T11:00:00",
                "status": "2",
                "service": "Troca completa",
            }
        ]

        with self.assertRaises(ValidationError):
            validate_work_order_entries(payload)

    def test_validate_checklist_entries_returns_normalized_payload(self):
        payload = [
            {
                "id": str(uuid.uuid4()),
                "checklist_item_fk": str(self.checklist_item.id),
                "work_order_fk": str(self.work_order.id),
                "status": "1",
                "img_in": None,
                "img_out": None,
            }
        ]

        validated = validate_checklist_entries(payload)

        self.assertEqual(validated[0]["checklist_item"].id, self.checklist_item.id)
        self.assertEqual(validated[0]["work_order"].id, self.work_order.id)
        self.assertEqual(validated[0]["status"], "1")

    def test_validate_checklist_entries_rejects_invalid_image(self):
        payload = [
            {
                "id": str(uuid.uuid4()),
                "checklist_item_fk": str(self.checklist_item.id),
                "work_order_fk": str(self.work_order.id),
                "status": "1",
                "img_in": b"not-an-image",
                "img_out": None,
            }
        ]

        with self.assertRaises(ValidationError):
            validate_checklist_entries(payload)
