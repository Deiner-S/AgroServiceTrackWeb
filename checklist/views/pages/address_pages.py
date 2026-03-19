from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from checklist.forms import AddressForm
from checklist.models import Address, Client


User = get_user_model()

ADDRESS_SECTION_TEMPLATE = "theme/address/cards.html"


def _address_section_context(entity, entity_kind, *, form=None, show_form=False):
    addresses = entity.addresses.all().order_by("-created_at")

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


def get_address_section_context(entity, entity_kind, *, form=None, show_form=False):
    return _address_section_context(
        entity,
        entity_kind,
        form=form,
        show_form=show_form,
    )


def _render_address_section_response(request, entity, entity_kind, *, form=None, show_form=False):
    context = _address_section_context(
        entity,
        entity_kind,
        form=form,
        show_form=show_form,
    )
    return render(request, ADDRESS_SECTION_TEMPLATE, context)


def _delete_orphan_address(address):
    if not address.clients.exists() and not address.employees.exists():
        address.delete()


@login_required(login_url="gerenciador/login/")
def add_client_address(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    client = get_object_or_404(Client, id=client_id)

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
        address = form.save()
        client.addresses.add(address)
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

    client = get_object_or_404(Client, id=client_id)
    address = get_object_or_404(Address, id=address_id)
    client.addresses.remove(address)
    _delete_orphan_address(address)
    return _render_address_section_response(request, client, "client")


@login_required(login_url="gerenciador/login/")
def add_employee_address(request, employee_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    employee = get_object_or_404(User, id=employee_id)

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
        address = form.save()
        employee.addresses.add(address)
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

    employee = get_object_or_404(User, id=employee_id)
    address = get_object_or_404(Address, id=address_id)
    employee.addresses.remove(address)
    _delete_orphan_address(address)
    return _render_address_section_response(request, employee, "employee")
