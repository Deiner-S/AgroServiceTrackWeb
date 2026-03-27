from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from checklist.forms import AddressForm
from checklist.exception_handler import RepositoryOperationError
from checklist.services import address_page_services
from checklist.views.pages.view_utils import render_repository_error

ADDRESS_SECTION_TEMPLATE = "theme/address/cards.html"


def get_address_section_context(entity, entity_kind, *, form=None, show_form=False):
    return address_page_services.get_address_section_context(
        entity,
        entity_kind,
        form=form or AddressForm(),
        show_form=show_form,
    )


def _render_address_section_response(request, entity, entity_kind, *, form=None, show_form=False):
    context = get_address_section_context(
        entity,
        entity_kind,
        form=form,
        show_form=show_form,
    )
    return render(request, ADDRESS_SECTION_TEMPLATE, context)


@login_required(login_url="gerenciador/login/")
def add_client_address(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    try:
        client = address_page_services.get_client(client_id)

        if request.method == "GET":
            return _render_address_section_response(
                request,
                client,
                "client",
                show_form=request.GET.get("cancel") != "true",
            )

        if request.method != "POST":
            return HttpResponseBadRequest("Metodo invalido")

        form = AddressForm(request.POST)
        if form.is_valid():
            address_page_services.create_address_for_client(
                client,
                form.save(commit=False),
            )
            return _render_address_section_response(request, client, "client")

        return _render_address_section_response(
            request,
            client,
            "client",
            form=form,
            show_form=True,
        )
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def delete_client_address(request, client_id, address_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    try:
        client = address_page_services.get_client(client_id)
        address = address_page_services.get_address(address_id)
        address_page_services.delete_address_from_client(client, address)
        return _render_address_section_response(request, client, "client")
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def add_employee_address(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    try:
        employee = address_page_services.get_employee(employee_id)

        if request.method == "GET":
            return _render_address_section_response(
                request,
                employee,
                "employee",
                show_form=request.GET.get("cancel") != "true",
            )

        if request.method != "POST":
            return HttpResponseBadRequest("Metodo invalido")

        form = AddressForm(request.POST)
        if form.is_valid():
            address_page_services.create_address_for_employee(
                employee,
                form.save(commit=False),
            )
            return _render_address_section_response(request, employee, "employee")

        return _render_address_section_response(
            request,
            employee,
            "employee",
            form=form,
            show_form=True,
        )
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def delete_employee_address(request, employee_id, address_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    try:
        employee = address_page_services.get_employee(employee_id)
        address = address_page_services.get_address(address_id)
        address_page_services.delete_address_from_employee(employee, address)
        return _render_address_section_response(request, employee, "employee")
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)
