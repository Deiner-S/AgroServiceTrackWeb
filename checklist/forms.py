from django import forms
from checklist.models import Client,Employee,WorkOrder


# Shared Tailwind input class used across forms
INPUT_TW_CLASS = (
    "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl shadow-sm "
    "focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 "
    "transition-all duration-200"
)


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['cnpj','name', 'email','phone']
        widgets = {
            'cnpj': forms.TextInput(attrs={'class': INPUT_TW_CLASS}),
            'name': forms.TextInput(attrs={'class': INPUT_TW_CLASS}),
            'email': forms.EmailInput(attrs={'class': INPUT_TW_CLASS}),
            'phone': forms.TextInput(attrs={'class': INPUT_TW_CLASS}),
        }


class EmployeeForm(forms.ModelForm):
    # define password field explicitly so we can attach Tailwind classes
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": INPUT_TW_CLASS})
    )
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
        
        widgets = {
            "first_name": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "last_name": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "cpf": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "phone": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "email": forms.EmailInput(attrs={"class": INPUT_TW_CLASS}),
            "position": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "username": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            # password widget declared above, no need to repeat here
        }
        

class DataSheetCreateForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ["operation_code", "symptoms"]

        labels = {
            'operation_code': 'Ordem de serviço',
            'symptoms': 'Descrição do problema'
        }

        widgets = {
            "operation_code": forms.TextInput(attrs={"readonly": "readonly", 'class': INPUT_TW_CLASS}),
            "symptoms": forms.Textarea(attrs={"rows": 4, 'class': INPUT_TW_CLASS}),
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
            "chassi": forms.TextInput(attrs={'class': INPUT_TW_CLASS}),
            "horimetro": forms.NumberInput(attrs={'class': INPUT_TW_CLASS}),
            "model": forms.TextInput(attrs={'class': INPUT_TW_CLASS}),
            "date_in": forms.DateTimeInput(attrs={"type": "datetime-local", 'class': INPUT_TW_CLASS}),
            "date_out": forms.DateTimeInput(attrs={"type": "datetime-local", 'class': INPUT_TW_CLASS}),
            "service": forms.Textarea(attrs={'class': INPUT_TW_CLASS, 'rows': 3}),
            "status": forms.Select(attrs={'class': INPUT_TW_CLASS}),
        }