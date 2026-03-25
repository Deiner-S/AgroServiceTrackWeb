from django import forms

from checklist.forms.common import CPF_INPUT_ATTRS, INPUT_TW_CLASS, LOCKED_INPUT_TW_CLASS, PHONE_INPUT_ATTRS
from checklist.models import Client
from checklist.utils.validation_utils import (
    validate_cnpj_format,
    validate_cpf_format,
    validate_email_format,
    validate_only_letters_and_spaces,
    validate_phone_format,
)


class ClientForm(forms.ModelForm):
    def clean_name(self):
        return validate_only_letters_and_spaces(self.cleaned_data["name"])

    def clean_cnpj(self):
        return validate_cnpj_format(self.cleaned_data["cnpj"])

    def clean_email(self):
        return validate_email_format(self.cleaned_data["email"])

    def clean_phone(self):
        return validate_phone_format(self.cleaned_data["phone"])

    class Meta:
        model = Client
        fields = ["cnpj", "name", "email", "phone"]
        widgets = {
            "cnpj": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "name": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "email": forms.EmailInput(attrs={"class": INPUT_TW_CLASS}),
            "phone": forms.TextInput(attrs={"class": INPUT_TW_CLASS, **PHONE_INPUT_ATTRS}),
        }


class ClientDetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cpf"].disabled = True
        self.fields["cnpj"].disabled = True
        self.fields["cpf"].widget.attrs.update(
            {
                "class": LOCKED_INPUT_TW_CLASS,
                "title": "Campo bloqueado",
                "aria-disabled": "true",
                **CPF_INPUT_ATTRS,
            }
        )
        self.fields["cnpj"].widget.attrs.update(
            {
                "class": LOCKED_INPUT_TW_CLASS,
                "title": "Campo bloqueado",
                "aria-disabled": "true",
            }
        )

    def clean_cpf(self):
        value = self.cleaned_data.get("cpf")
        return validate_cpf_format(value) if value else value

    def clean_name(self):
        return validate_only_letters_and_spaces(self.cleaned_data["name"])

    def clean_cnpj(self):
        value = self.cleaned_data.get("cnpj")
        return validate_cnpj_format(value) if value else value

    def clean_email(self):
        return validate_email_format(self.cleaned_data["email"])

    def clean_phone(self):
        return validate_phone_format(self.cleaned_data["phone"])

    class Meta:
        model = Client
        fields = ["cpf", "cnpj", "name", "email", "phone"]
        labels = {
            "cpf": "CPF",
            "cnpj": "CNPJ",
            "name": "Nome",
            "email": "Email",
            "phone": "Telefone/celular",
        }
        widgets = {
            "cpf": forms.TextInput(attrs={"class": INPUT_TW_CLASS, **CPF_INPUT_ATTRS}),
            "cnpj": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "name": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "email": forms.EmailInput(attrs={"class": INPUT_TW_CLASS}),
            "phone": forms.TextInput(attrs={"class": INPUT_TW_CLASS, **PHONE_INPUT_ATTRS}),
        }
