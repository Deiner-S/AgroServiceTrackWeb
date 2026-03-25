from django import forms

from checklist.forms.common import INPUT_TW_CLASS
from checklist.models import Address
from checklist.utils.validation_utils import (
    validate_only_letters_and_spaces,
    validate_only_letters_numbers_and_spaces,
    validate_only_numbers,
    validate_zip_code_format,
)


class AddressForm(forms.ModelForm):
    def clean_street(self):
        return validate_only_letters_numbers_and_spaces(self.cleaned_data["street"])

    def clean_number(self):
        return validate_only_numbers(self.cleaned_data["number"])

    def clean_city(self):
        return validate_only_letters_and_spaces(self.cleaned_data["city"])

    def clean_zip_code(self):
        return validate_zip_code_format(self.cleaned_data["zip_code"])

    class Meta:
        model = Address
        fields = ["street", "number", "city", "state", "zip_code"]
        labels = {
            "street": "Rua",
            "number": "Numero",
            "city": "Cidade",
            "state": "Estado",
            "zip_code": "CEP",
        }
        widgets = {
            "street": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "number": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "city": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "state": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "zip_code": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
        }
