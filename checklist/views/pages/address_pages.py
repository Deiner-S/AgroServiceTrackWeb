from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from checklist.forms import AddressForm
from checklist.repository import address_repository, client_repository, employee_repository
from checklist.views.pages.view_utils import resolve_repository_result

ADDRESS_SECTION_TEMPLATE = "theme/address/cards.html"


def _address_section_context(request, entity, entity_kind, *, form=None, show_form=False):
    addresses, error_response = resolve_repository_result(request, address_repository.list_for_entity(entity))
    if error_response:
        return None, error_response

    if entity_kind == "client":
        add_url_name = "add-client-address"
        delete_url_name = "delete-client-address"
        section_id = f"client-addresses-{entity.id}"
    else:
        add_url_name = "add-employee-address"
        delete_url_name = "delete-employee-address"
        section_id = f"employee-addresses-{entity.id}"

    return {
        "entity": entity,
        "entity_kind": entity_kind,
        "addresses": addresses,
        "address_form": form or AddressForm(),
        "show_address_form": show_form,
        "address_add_url_name": add_url_name,
        "address_delete_url_name": delete_url_name,
        "address_section_id": section_id,
    }


def get_address_section_context(request, entity, entity_kind, *, form=None, show_form=False):
    context = _address_section_context(
        request,
        entity,
        entity_kind,
        form=form,
        show_form=show_form,
    )
    if isinstance(context, tuple):
        return context
    return context, None


def _render_address_section_response(request, entity, entity_kind, *, form=None, show_form=False):
    context, error_response = get_address_section_context(
        request,
        entity,
        entity_kind,
        form=form,
        show_form=show_form,
    )
    if error_response:
        return error_response
    return render(request, ADDRESS_SECTION_TEMPLATE, context)


@login_required(login_url="gerenciador/login/")
def add_client_address(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    client, error_response = resolve_repository_result(request, client_repository.get_by_id(client_id))
    if error_response:
        return error_response

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
        address, error_response = resolve_repository_result(request, address_repository.save(form.save(commit=False)))
        if error_response:
            return error_response

        _, error_response = resolve_repository_result(request, address_repository.add_to_client(client, address))
        if error_response:
            return error_response

        return _render_address_section_response(request, client, "client")

    return _render_address_section_response(
        request,
        client,
        "client",
        form=form,
        show_form=True,
    )


@login_required(login_url="gerenciador/login/")
def delete_client_address(request, client_id, address_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    client, error_response = resolve_repository_result(request, client_repository.get_by_id(client_id))
    if error_response:
        return error_response

    address, error_response = resolve_repository_result(request, address_repository.get_by_id(address_id))
    if error_response:
        return error_response

    _, error_response = resolve_repository_result(request, address_repository.remove_from_client(client, address))
    if error_response:
        return error_response

    _, error_response = resolve_repository_result(request, address_repository.delete_if_orphan(address))
    if error_response:
        return error_response

    return _render_address_section_response(request, client, "client")


@login_required(login_url="gerenciador/login/")
def add_employee_address(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    employee, error_response = resolve_repository_result(request, employee_repository.get_by_id(employee_id))
    if error_response:
        return error_response

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
        address, error_response = resolve_repository_result(request, address_repository.save(form.save(commit=False)))
        if error_response:
            return error_response

        _, error_response = resolve_repository_result(request, address_repository.add_to_employee(employee, address))
        if error_response:
            return error_response

        return _render_address_section_response(request, employee, "employee")

    return _render_address_section_response(
        request,
        employee,
        "employee",
        form=form,
        show_form=True,
    )


@login_required(login_url="gerenciador/login/")
def delete_employee_address(request, employee_id, address_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    employee, error_response = resolve_repository_result(request, employee_repository.get_by_id(employee_id))
    if error_response:
        return error_response

    address, error_response = resolve_repository_result(request, address_repository.get_by_id(address_id))
    if error_response:
        return error_response

    _, error_response = resolve_repository_result(request, address_repository.remove_from_employee(employee, address))
    if error_response:
        return error_response

    _, error_response = resolve_repository_result(request, address_repository.delete_if_orphan(address))
    if error_response:
        return error_response

    return _render_address_section_response(request, employee, "employee")
