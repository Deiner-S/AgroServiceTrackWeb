from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from checklist.forms import EmployeeDetailForm, EmployeeForm
from checklist.exception_handler import RepositoryOperationError
from checklist.permissions import (
    can_create_employee,
    can_edit_employee,
    can_manage_employee_addresses,
    can_toggle_employee_status,
    can_view_employee_module,
    get_access_context,
)
from checklist.services import employee_page_services
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.view_utils import render_forbidden, render_repository_error


def _render_employee_list(request):
    query = (request.GET.get("search") or "").strip()
    context = employee_page_services.get_employee_list_context(
        search_query=query,
        page_number=request.GET.get("page"),
    )
    context.update(get_access_context(request.user))
    return render(request, TemplatePaths.EMPLOYEE_LIST, context)


def _render_employee_detail(request, employee, form):
    context = employee_page_services.get_employee_detail_context(
        employee=employee,
        form=form,
        search_query=(request.GET.get("search") or "").strip(),
        page_number=request.GET.get("page", ""),
    )
    context.update(get_access_context(request.user))
    context["can_edit_selected_employee"] = can_edit_employee(request.user, employee)
    context["can_manage_addresses"] = can_manage_employee_addresses(
        request.user,
        employee,
    )
    context["can_toggle_selected_employee_status"] = can_toggle_employee_status(
        request.user,
        employee,
    )
    return render(
        request,
        TemplatePaths.EMPLOYEE_DETAIL,
        context,
    )


@login_required(login_url="gerenciador/login/")
def add_employee(request):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")
    if not can_create_employee(request.user):
        return render_forbidden(request, "Seu cargo não pode cadastrar funcionários.")

    try:
        if request.method == "POST":
            form = EmployeeForm(request.POST, actor=request.user)

            if form.is_valid():
                user = employee_page_services.prepare_new_employee(
                    form.save(commit=False),
                    form.cleaned_data["password"],
                )
                employee_page_services.save_employee(user)
                return _render_employee_list(request)
        else:
            form = EmployeeForm(actor=request.user)

        return render(
            request,
            TemplatePaths.EMPLOYEE_FORM,
            {
                "form": form,
                **get_access_context(request.user),
            },
        )
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def employee_detail(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")
    if not can_view_employee_module(request.user):
        return render_forbidden(request, "Seu cargo não pode acessar funcionários.")

    try:
        employee = employee_page_services.get_employee(employee_id)
        can_edit_target = can_edit_employee(request.user, employee)

        if request.method == "POST":
            if not can_edit_target:
                return render_forbidden(
                    request,
                    "Seu cargo não pode editar este funcionário.",
                )

            form = EmployeeDetailForm(
                request.POST,
                instance=employee,
                actor=request.user,
            )
            if form.is_valid():
                user = employee_page_services.prepare_employee_update(
                    form.save(commit=False),
                    form.cleaned_data.get("password"),
                )
                employee_page_services.save_employee(user)
                return _render_employee_list(request)
        else:
            form = EmployeeDetailForm(
                instance=employee,
                actor=request.user,
                read_only=not can_edit_target,
            )

        return _render_employee_detail(request, employee, form)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def delete_employee(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")

    if request.method != "POST":
        return HttpResponseBadRequest("Método inválido")

    try:
        employee = employee_page_services.get_employee(employee_id)
        if not can_edit_employee(request.user, employee):
            return render_forbidden(
                request,
                "Seu cargo não pode excluir este funcionário.",
            )

        employee_page_services.delete_employee(employee_id)
        return _render_employee_list(request)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def toggle_employee_status(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")

    if request.method != "POST":
        return HttpResponseBadRequest("Método inválido")

    try:
        current_employee = employee_page_services.get_employee(employee_id)
        if not can_toggle_employee_status(request.user, current_employee):
            return render_forbidden(
                request,
                "Seu cargo não pode ativar ou desativar este funcionário.",
            )

        employee = employee_page_services.toggle_employee_status(employee_id)
        form = EmployeeDetailForm(instance=employee, actor=request.user)
        return _render_employee_detail(request, employee, form)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def employee_list(request):
    try:
        if not can_view_employee_module(request.user):
            return render_forbidden(request, "Seu cargo não pode acessar funcionários.")
        return _render_employee_list(request)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)
