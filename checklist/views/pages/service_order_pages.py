from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from checklist.forms import ClientDetailForm, DataSheetCreateForm
from checklist.repository import client_repository, work_order_repository
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.client_pages import _render_client_detail
from checklist.views.pages.view_utils import resolve_repository_result


@login_required(login_url="gerenciador/login/")
def open_client_order(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    client, error_response = resolve_repository_result(request, client_repository.get_by_id(client_id))
    if error_response:
        return error_response

    form = ClientDetailForm(instance=client)
    return _render_client_detail(request, client, form)


@login_required(login_url="gerenciador/login/")
def add_order(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    client, error_response = resolve_repository_result(request, client_repository.get_by_id(client_id))
    if error_response:
        return error_response

    if request.method == "POST":
        form = DataSheetCreateForm(request.POST)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.client = client
            _, error_response = resolve_repository_result(request, work_order_repository.save(work_order))
            if error_response:
                return error_response
            client_form = ClientDetailForm(instance=client)
            return _render_client_detail(request, client, client_form)
    else:
        next_code, error_response = resolve_repository_result(
            request,
            work_order_repository.get_next_operation_code(),
        )
        if error_response:
            return error_response
        form = DataSheetCreateForm(initial={"operation_code": next_code})

    return render(
        request,
        TemplatePaths.SERVICE_ORDER_FORM,
        {
            "form": form,
            "client": client,
        },
    )


@login_required(login_url="gerenciador/login/")
def service_panel(request):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    status_filter = (request.GET.get("status") or "all").strip()
    search_query = (request.GET.get("search") or "").strip()
    status_options = [
        ("all", "Todos"),
        ("1", "Pendente"),
        ("2", "Andamento"),
        ("3", "Entrega"),
        ("4", "Finalizada"),
    ]
    allowed_status = {value for value, _ in status_options}

    if status_filter not in allowed_status:
        status_filter = "all"

    orders, error_response = resolve_repository_result(
        request,
        work_order_repository.list_for_panel(
            status_filter=status_filter,
            search_query=search_query,
        ),
    )
    if error_response:
        return error_response

    return render(
        request,
        TemplatePaths.SERVICE_ORDER_PANEL,
        {
            "orders": orders,
            "selected_status": status_filter,
            "current_search": search_query,
            "status_options": status_options,
        },
    )


@login_required(login_url="gerenciador/login/")
def service_order_detail(request, order_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    order, error_response = resolve_repository_result(request, work_order_repository.get_detail_by_id(order_id))
    if error_response:
        return error_response

    return render(
        request,
        TemplatePaths.SERVICE_ORDER_DETAIL,
        {
            "order": order,
            "current_search": (request.GET.get("search") or "").strip(),
            "selected_status": (request.GET.get("status") or "all").strip(),
        },
    )
