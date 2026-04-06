from django.core.exceptions import ValidationError

from checklist.forms import (
    AddressForm,
    ChecklistItemForm,
    ClientDetailForm,
    ClientForm,
    DataSheetCreateForm,
    EmployeeDetailForm,
)


CLIENT_CREATE_ALLOWED_KEYS = {"cnpj", "name", "email", "phone"}
CLIENT_UPDATE_ALLOWED_KEYS = {"cpf", "cnpj", "name", "email", "phone"}
CLIENT_ADDRESS_ALLOWED_KEYS = {"street", "number", "complement", "city", "state", "zip_code"}
CLIENT_SERVICE_ALLOWED_KEYS = {"operation_code", "symptoms"}
CHECKLIST_ITEM_ALLOWED_KEYS = {"name"}
EMPLOYEE_UPDATE_ALLOWED_KEYS = {
    "first_name",
    "last_name",
    "cpf",
    "phone",
    "email",
    "position",
    "username",
    "password",
}
EMPLOYEE_ADDRESS_ALLOWED_KEYS = {"street", "number", "complement", "city", "state", "zip_code"}


def raise_form_validation_error(form):
    raise ValidationError(form.errors)
