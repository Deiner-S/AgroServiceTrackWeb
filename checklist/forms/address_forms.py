from django import forms
from django.core.exceptions import ValidationError

from checklist.forms.common import INPUT_TW_CLASS, ZIP_CODE_INPUT_ATTRS
from checklist.models import Address
from checklist.utils.validation_utils import (
    validate_only_letters_and_spaces,
    validate_only_letters_numbers_and_spaces,
    validate_only_numbers,
    validate_zip_code_format,
)

BRAZILIAN_STATE_CHOICES = [
    ("Acre", "Acre"),
    ("Alagoas", "Alagoas"),
    ("Amapa", "Amapa"),
    ("Amazonas", "Amazonas"),
    ("Bahia", "Bahia"),
    ("Ceara", "Ceara"),
    ("Distrito Federal", "Distrito Federal"),
    ("Espirito Santo", "Espirito Santo"),
    ("Goias", "Goias"),
    ("Maranhao", "Maranhao"),
    ("Mato Grosso", "Mato Grosso"),
    ("Mato Grosso do Sul", "Mato Grosso do Sul"),
    ("Minas Gerais", "Minas Gerais"),
    ("Para", "Para"),
    ("Paraiba", "Paraiba"),
    ("Parana", "Parana"),
    ("Pernambuco", "Pernambuco"),
    ("Piaui", "Piaui"),
    ("Rio de Janeiro", "Rio de Janeiro"),
    ("Rio Grande do Norte", "Rio Grande do Norte"),
    ("Rio Grande do Sul", "Rio Grande do Sul"),
    ("Rondonia", "Rondonia"),
    ("Roraima", "Roraima"),
    ("Santa Catarina", "Santa Catarina"),
    ("Sao Paulo", "Sao Paulo"),
    ("Sergipe", "Sergipe"),
    ("Tocantins", "Tocantins"),
]


class AddressForm(forms.ModelForm):
    state = forms.ChoiceField(
        choices=[("", "Selecione um estado"), *BRAZILIAN_STATE_CHOICES],
        widget=forms.Select(attrs={"class": INPUT_TW_CLASS}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        current_state = getattr(self.instance, "state", None)
        available_states = {value for value, _label in BRAZILIAN_STATE_CHOICES}
        state_choices = [("", "Selecione um estado"), *BRAZILIAN_STATE_CHOICES]

        if current_state and current_state not in available_states:
            state_choices = [
                ("", "Selecione um estado"),
                (current_state, current_state),
                *BRAZILIAN_STATE_CHOICES,
            ]

        self.fields["state"].choices = state_choices

    def clean_street(self):
        return validate_only_letters_numbers_and_spaces(self.cleaned_data["street"])

    def clean_number(self):
        return validate_only_numbers(self.cleaned_data["number"])

    def clean_complement(self):
        complement = self.cleaned_data["complement"]
        if not complement:
            return complement
        return validate_only_letters_numbers_and_spaces(complement)

    def clean_city(self):
        return validate_only_letters_and_spaces(self.cleaned_data["city"])

    def clean_state(self):
        state = self.cleaned_data["state"]
        allowed_states = {value for value, _label in BRAZILIAN_STATE_CHOICES}
        current_state = getattr(self.instance, "state", None)

        if state in allowed_states or (current_state and state == current_state):
            return state

        raise ValidationError("Selecione um estado válido.")

    def clean_zip_code(self):
        return validate_zip_code_format(self.cleaned_data["zip_code"])

    class Meta:
        model = Address
        fields = ["street", "number", "complement", "city", "state", "zip_code"]
        labels = {
            "street": "Rua",
            "number": "Número",
            "complement": "Complemento",
            "city": "Cidade",
            "state": "Estado",
            "zip_code": "CEP",
        }
        widgets = {
            "street": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "number": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "complement": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "city": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "zip_code": forms.TextInput(
                attrs={"class": INPUT_TW_CLASS, **ZIP_CODE_INPUT_ATTRS}
            ),
        }
