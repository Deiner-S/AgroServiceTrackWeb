from django import forms
from checklist.models import Address, ChecklistItem, Client,Employee,WorkOrder


# Shared Tailwind input class used across forms
INPUT_TW_CLASS = (
    "w-full px-4 py-3 bg-gray-700 border border-gray-500 rounded-xl shadow-sm "
    "text-white placeholder-gray-300 "
    "focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-gray-400 "
    "transition-all duration-200"
)

LOCKED_INPUT_TW_CLASS = (
    "w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-xl shadow-sm "
    "text-gray-300 cursor-not-allowed select-none opacity-100 "
    "focus:outline-none focus:ring-0 focus:border-gray-200"
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
            }
        )
        self.fields["cnpj"].widget.attrs.update(
            {
                "class": LOCKED_INPUT_TW_CLASS,
                "title": "Campo bloqueado",
                "aria-disabled": "true",
            }
        )

    class Meta:
        model = Client
        fields = ['cpf', 'cnpj', 'name', 'email', 'phone']
        labels = {
            'cpf': 'CPF',
            'cnpj': 'CNPJ',
            'name': 'Nome',
            'email': 'Email',
            'phone': 'Telefone/celular',
        }
        widgets = {
            'cpf': forms.TextInput(attrs={'class': INPUT_TW_CLASS}),
            'cnpj': forms.TextInput(attrs={'class': INPUT_TW_CLASS}),
            'name': forms.TextInput(attrs={'class': INPUT_TW_CLASS}),
            'email': forms.EmailInput(attrs={'class': INPUT_TW_CLASS}),
            'phone': forms.TextInput(attrs={'class': INPUT_TW_CLASS}),
        }


class AddressForm(forms.ModelForm):
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
            "position": forms.Select(attrs={"class": INPUT_TW_CLASS}),
            "username": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            # password widget declared above, no need to repeat here
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

    class Meta:
        model = Employee
        fields = [
            'first_name',
            'last_name',
            'cpf',
            'phone',
            'email',
            'position',
            'username',
            'password',
        ]
        labels = {
            'first_name': 'Primeiro nome',
            'last_name': 'Sobrenome',
            'cpf': 'CPF',
            'phone': 'Telefone/celular',
            'email': 'Email',
            'position': 'Cargo',
            'username': 'Usuario',
            'password': 'Nova senha',
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "last_name": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "cpf": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "phone": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
            "email": forms.EmailInput(attrs={"class": INPUT_TW_CLASS}),
            "position": forms.Select(attrs={"class": INPUT_TW_CLASS}),
            "username": forms.TextInput(attrs={"class": INPUT_TW_CLASS}),
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
            "operation_code": forms.TextInput(
                attrs={
                    "readonly": "readonly",
                    "class": LOCKED_INPUT_TW_CLASS,
                    "title": "Campo bloqueado",
                    "aria-disabled": "true",
                }
            ),
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
                    "placeholder": "Ex.: Verificar pneus, luzes, oleo...",
                }
            ),
        }
