from django import forms
from checklist.models import Client
from .models import Employee

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