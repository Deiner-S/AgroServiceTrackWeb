from django import forms

from checklist.forms.common import INPUT_TW_CLASS, LOCKED_INPUT_TW_CLASS
from checklist.models import WorkOrder


class DataSheetCreateForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ["operation_code", "symptoms"]
        labels = {
            "operation_code": "Ordem de serviço",
            "symptoms": "Descrição do problema",
        }
        widgets = {
            "operation_code": forms.TextInput(
                attrs={
                    "readonly": "readonly",
                    "class": LOCKED_INPUT_TW_CLASS,
                    "title": "Campo bloqueado",
                    "aria-disabled": "true",
                }
            ),
            "symptoms": forms.Textarea(attrs={"rows": 4, "class": INPUT_TW_CLASS}),
        }


class DataSheetUpdateForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = [
            "chassi",
            "horimetro",
            "model",
            "date_in",
            "date_out",
            "service",
            "status",
        ]
        widgets = {
            "chassi": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "horimetro": forms.NumberInput(attrs={"class": INPUT_TW_CLASS}),
            "model": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "date_in": forms.DateTimeInput(attrs={"type": "datetime-local", "class": INPUT_TW_CLASS}),
            "date_out": forms.DateTimeInput(attrs={"type": "datetime-local", "class": INPUT_TW_CLASS}),
            "service": forms.Textarea(attrs={"class": INPUT_TW_CLASS, "rows": 3}),
            "status": forms.Select(
                attrs={
                    "class": INPUT_TW_CLASS,
                    "data-option-text-black": "true",
                }
            ),
        }
