from django import forms
from checklist.models import Client
from .models import Worker

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email']

class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['first_name',
                  'last_name', 
                  'cpf', 
                  'phone',
                  'email', 
                  'position',
                  'username',
                  'password',]