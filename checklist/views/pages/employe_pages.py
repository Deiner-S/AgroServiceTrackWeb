
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from checklist.forms import EmployeeForm
from django.http import HttpResponseBadRequest
from checklist.templates_paths import TemplatePaths
from django.core.paginator import Paginator
from django.db import models


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
            # after saving via HTMX, return the updated employee list fragment
            employees = User.objects.all().order_by("first_name")
            page_number = request.GET.get("page")
            paginator = Paginator(employees, 10)
            page_employees = paginator.get_page(page_number)
            return render(request, TemplatePaths.EMPLOYEE_LIST, {"page_employees": page_employees})
        else:
            print("Form inválido!")
            print(form.errors)        # mostra todos os erros do form
            print(form.cleaned_data)  # mostra os dados limpos que passaram

        
    else:
        form = EmployeeForm()

    return render(request, TemplatePaths.EMPLOYEE_FORM, {"form": form})


@login_required(login_url='gerenciador/login/')
def employee_list(request):
    employees = User.objects.all().order_by("first_name")
    query = request.GET.get("search", "")
    query = (query or "").strip()

    if query:
        employees = employees.filter(
            models.Q(first_name__icontains=query)
            | models.Q(last_name__icontains=query)
            | models.Q(email__icontains=query)
            | models.Q(cpf__icontains=query)
        )

    page_number = request.GET.get("page")
    paginator = Paginator(employees, 10)
    page_employees = paginator.get_page(page_number)
    
    return render(request, TemplatePaths.EMPLOYEE_LIST, {"page_employees": page_employees})
