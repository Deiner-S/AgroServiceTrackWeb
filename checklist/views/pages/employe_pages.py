from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from checklist.forms import EmployeeDetailForm, EmployeeForm
from checklist.exception_handler import RepositoryOperationError
from checklist.services import employee_page_services
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.view_utils import render_repository_error


def _render_employee_list(request):
    query = (request.GET.get("search") or "").strip()
    context = employee_page_services.get_employee_list_context(
        search_query=query,
        page_number=request.GET.get("page"),
    )
    return render(request, TemplatePaths.EMPLOYEE_LIST, context)


def _render_employee_detail(request, employee, form):
    context = employee_page_services.get_employee_detail_context(
        employee=employee,
        form=form,
        search_query=(request.GET.get("search") or "").strip(),
        page_number=request.GET.get("page", ""),
    )
    return render(
        request,
        TemplatePaths.EMPLOYEE_DETAIL,
        context,
    )


@login_required(login_url="gerenciador/login/")
def add_employee(request):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    try:
        if request.method == "POST":
            form = EmployeeForm(request.POST)

            if form.is_valid():
                user = employee_page_services.prepare_new_employee(
                    form.save(commit=False),
                    form.cleaned_data["password"],
                )
                employee_page_services.save_employee(user)
                return _render_employee_list(request)

            print("Form invalido!")
            print(form.errors)
            print(form.cleaned_data)
        else:
            form = EmployeeForm()

        return render(request, TemplatePaths.EMPLOYEE_FORM, {"form": form})
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def employee_detail(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    try:
        employee = employee_page_services.get_employee(employee_id)

        if request.method == "POST":
            form = EmployeeDetailForm(request.POST, instance=employee)
            if form.is_valid():
                user = employee_page_services.prepare_employee_update(
                    form.save(commit=False),
                    form.cleaned_data.get("password"),
                )
                employee_page_services.save_employee(user)
                return _render_employee_list(request)
        else:
            form = EmployeeDetailForm(instance=employee)

        return _render_employee_detail(request, employee, form)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def delete_employee(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    try:
        employee_page_services.delete_employee(employee_id)
        return _render_employee_list(request)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def toggle_employee_status(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    try:
        employee = employee_page_services.toggle_employee_status(employee_id)
        form = EmployeeDetailForm(instance=employee)
        return _render_employee_detail(request, employee, form)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def employee_list(request):
    try:
        return _render_employee_list(request)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)
