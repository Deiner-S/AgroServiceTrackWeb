from django import forms

from checklist.forms.common import INPUT_TW_CLASS
from checklist.models import ChecklistItem


class ChecklistItemForm(forms.ModelForm):
    class Meta:
        model = ChecklistItem
        fields = ["name"]
        labels = {
            "name": "Nome do item",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": INPUT_TW_CLASS,
                    "placeholder": "Ex.: Verificar pneus, luzes, óleo...",
                }
            ),
        }
