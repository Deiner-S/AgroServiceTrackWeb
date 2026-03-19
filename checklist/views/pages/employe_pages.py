from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from checklist.forms import EmployeeDetailForm, EmployeeForm
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.address_pages import get_address_section_context


User = get_user_model()


def _render_employee_list(request):
    employees = User.objects.all().order_by("first_name")
    query = (request.GET.get("search") or "").strip()

    if query:
        employees = employees.filter(
            models.Q(first_name__icontains=query)
            | models.Q(last_name__icontains=query)
            | models.Q(email__icontains=query)
            | models.Q(cpf__icontains=query)
        )

    paginator = Paginator(employees, 10)
    page_number = request.GET.get("page")
    page_employees = paginator.get_page(page_number)

    return render(
        request,
        TemplatePaths.EMPLOYEE_LIST,
        {
            "page_employees": page_employees,
            "current_search": query,
        },
    )


def _render_employee_detail(request, employee, form):
    address_context = get_address_section_context(employee, "employee")

    return render(
        request,
        TemplatePaths.EMPLOYEE_DETAIL,
        {
            "form": form,
            "employee": employee,
            "current_search": (request.GET.get("search") or "").strip(),
            "current_page": request.GET.get("page", ""),
            **address_context,
        },
    )


@login_required(login_url="gerenciador/login/")
def add_employee(request):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method == "POST":
        form = EmployeeForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return _render_employee_list(request)

        print("Form invalido!")
        print(form.errors)
        print(form.cleaned_data)
    else:
        form = EmployeeForm()

    return render(request, TemplatePaths.EMPLOYEE_FORM, {"form": form})


@login_required(login_url="gerenciador/login/")
def employee_detail(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    employee = get_object_or_404(User, id=employee_id)

    if request.method == "POST":
        form = EmployeeDetailForm(request.POST, instance=employee)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get("password")
            if new_password:
                user.set_password(new_password)
            user.save()
            return _render_employee_list(request)
    else:
        form = EmployeeDetailForm(instance=employee)

    return _render_employee_detail(request, employee, form)


@login_required(login_url="gerenciador/login/")
def delete_employee(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    employee = get_object_or_404(User, id=employee_id)
    employee.delete()
    return _render_employee_list(request)


@login_required(login_url="gerenciador/login/")
def toggle_employee_status(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    employee = get_object_or_404(User, id=employee_id)
    employee.is_active = not employee.is_active
    employee.save(update_fields=["is_active"])

    form = EmployeeDetailForm(instance=employee)
    return _render_employee_detail(request, employee, form)


@login_required(login_url="gerenciador/login/")
def employee_list(request):
    return _render_employee_list(request)
