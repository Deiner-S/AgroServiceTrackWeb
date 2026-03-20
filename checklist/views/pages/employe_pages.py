from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from checklist.forms import EmployeeDetailForm, EmployeeForm
from checklist.repository import employee_repository
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.address_pages import get_address_section_context


def _render_employee_list(request):
    query = (request.GET.get("search") or "").strip()
    employees = employee_repository.list_for_management(query)

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
            employee_repository.save(user)
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

    employee = employee_repository.get_or_404(id=employee_id)

    if request.method == "POST":
        form = EmployeeDetailForm(request.POST, instance=employee)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get("password")
            if new_password:
                user.set_password(new_password)
            employee_repository.save(user)
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

    employee = employee_repository.get_or_404(id=employee_id)
    employee_repository.delete(employee)
    return _render_employee_list(request)


@login_required(login_url="gerenciador/login/")
def toggle_employee_status(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    employee = employee_repository.get_or_404(id=employee_id)
    employee_repository.toggle_active_status(employee)

    form = EmployeeDetailForm(instance=employee)
    return _render_employee_detail(request, employee, form)


@login_required(login_url="gerenciador/login/")
def employee_list(request):
    return _render_employee_list(request)
