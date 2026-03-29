from django import forms

from checklist.forms.common import CPF_INPUT_ATTRS, INPUT_TW_CLASS, PHONE_INPUT_ATTRS
from checklist.models import Employee
from checklist.utils.validation_utils import (
    validate_cpf_format,
    validate_email_format,
    validate_only_letters_and_spaces,
    validate_only_lowercase_letters,
    validate_phone_format,
)


class EmployeeForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": INPUT_TW_CLASS})
    )

    def clean_first_name(self):
        return validate_only_letters_and_spaces(self.cleaned_data["first_name"])

    def clean_last_name(self):
        return validate_only_letters_and_spaces(self.cleaned_data["last_name"])

    def clean_cpf(self):
        return validate_cpf_format(self.cleaned_data["cpf"])

    def clean_phone(self):
        return validate_phone_format(self.cleaned_data["phone"])

    def clean_email(self):
        return validate_email_format(self.cleaned_data["email"])

    def clean_username(self):
        return validate_only_lowercase_letters(self.cleaned_data["username"])

    class Meta:
        model = Employee
        fields = [
            "first_name",
            "last_name",
            "cpf",
            "phone",
            "email",
            "position",
            "username",
            "password",
        ]
        labels = {
            "first_name": "Primeiro nome",
            "last_name": "Sobrenome",
            "cpf": "CPF",
            "phone": "Telefone/celular",
            "email": "Email",
            "position": "Cargo",
            "username": "Usuário",
            "password": "Senha",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "last_name": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "cpf": forms.TextInput(attrs={"class": INPUT_TW_CLASS, **CPF_INPUT_ATTRS}),
            "phone": forms.TextInput(attrs={"class": INPUT_TW_CLASS, **PHONE_INPUT_ATTRS}),
            "email": forms.EmailInput(attrs={"class": INPUT_TW_CLASS}),
            "position": forms.Select(attrs={"class": INPUT_TW_CLASS}),
            "username": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
        }


class EmployeeDetailForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_TW_CLASS,
                "placeholder": "Preencha apenas se quiser alterar a senha",
            }
        ),
    )

    def clean_first_name(self):
        return validate_only_letters_and_spaces(self.cleaned_data["first_name"])

    def clean_last_name(self):
        return validate_only_letters_and_spaces(self.cleaned_data["last_name"])

    def clean_cpf(self):
        return validate_cpf_format(self.cleaned_data["cpf"])

    def clean_phone(self):
        return validate_phone_format(self.cleaned_data["phone"])

    def clean_email(self):
        return validate_email_format(self.cleaned_data["email"])

    def clean_username(self):
        return validate_only_lowercase_letters(self.cleaned_data["username"])

    class Meta:
        model = Employee
        fields = [
            "first_name",
            "last_name",
            "cpf",
            "phone",
            "email",
            "position",
            "username",
            "password",
        ]
        labels = {
            "first_name": "Primeiro nome",
            "last_name": "Sobrenome",
            "cpf": "CPF",
            "phone": "Telefone/celular",
            "email": "Email",
            "position": "Cargo",
            "username": "Usuário",
            "password": "Nova senha",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "last_name": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "cpf": forms.TextInput(attrs={"class": INPUT_TW_CLASS, **CPF_INPUT_ATTRS}),
            "phone": forms.TextInput(attrs={"class": INPUT_TW_CLASS, **PHONE_INPUT_ATTRS}),
            "email": forms.EmailInput(attrs={"class": INPUT_TW_CLASS}),
            "position": forms.Select(attrs={"class": INPUT_TW_CLASS}),
            "username": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
        }
