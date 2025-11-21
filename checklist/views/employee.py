
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from checklist.forms import EmployeeForm
from django.http import HttpResponseBadRequest
from checklist.templates.templates_paths import TemplatePaths


User = get_user_model()

@login_required(login_url='gerenciador/login/')
def add_employee(request):
    if not request.headers.get("HX-Request"):
            return HttpResponseBadRequest("Acesso inválido")
    
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)  # cria sem salvar ainda
            user.set_password(form.cleaned_data["password"])  # hash da senha
            user.save()
        else:
            print("Form inválido!")
            print(form.errors)        # mostra todos os erros do form
            print(form.cleaned_data)  # mostra os dados limpos que passaram

        
    else:
        form = EmployeeForm()

    return render(request, TemplatePaths.EMPLOYEE_FORM, {"form": form})