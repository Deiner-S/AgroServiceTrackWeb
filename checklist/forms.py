from django import forms
from checklist.models import Client,Employee,DataSheet


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['cnpj','name', 'email','phone']

class EmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Employee        
        fields = ['first_name',
                  'last_name', 
                  'cpf', 
                  'phone',
                  'email', 
                  'position',
                  'username',
                  'password',]
        
        labels = {'first_name':'Primeiro nome',
                  'last_name':'Sobrenome', 
                  'cpf':'CPF', 
                  'phone':'Telefone/celular',
                  'email':'Email', 
                  'position':'Cargo',
                  'username':'Usuário',
                  'password':'Senha'}
        
class DataSheetCreateForm(forms.ModelForm):
    class Meta:
        model = DataSheet
        fields = ["operation_code", "symptoms"]

        labels = {
            'operation_code': 'Ordem de serviço',
            'symptoms': 'Descrição do problema'
        }

        widgets = {
            "operation_code": forms.TextInput(attrs={"readonly": "readonly"}),
            "symptoms": forms.Textarea(attrs={"rows": 4}),
        }

class DataSheetUpdateForm(forms.ModelForm):
    class Meta:
        model = DataSheet
        fields = [
            "chassi",
            "orimento",
            "model",
            "date_in",
            "date_out",
            "service",
            "status",
        ]
        widgets = {
            "date_in": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "date_out": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "status": forms.Select(),
        }