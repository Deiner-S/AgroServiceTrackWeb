from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from checklist.forms import ClientDetailForm, DataSheetCreateForm
from checklist.exception_handler import RepositoryOperationError
from checklist.permissions import (
    can_create_service_order,
    can_view_client_detail,
    can_view_service_panel,
    get_access_context,
)
from checklist.services import client_page_services, service_order_page_services
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.client_pages import _render_client_detail
from checklist.views.pages.view_utils import render_forbidden, render_repository_error


@login_required(login_url="gerenciador/login/")
def open_client_order(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")
    if not can_view_client_detail(request.user):
        return render_forbidden(request, "Seu cargo não pode inspecionar clientes.")

    try:
        client = client_page_services.get_client(client_id)
        form = ClientDetailForm(instance=client)
        return _render_client_detail(request, client, form)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def add_order(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")
    if not can_create_service_order(request.user):
        return render_forbidden(request, "Seu cargo não pode abrir novas ordens.")

    try:
        client = client_page_services.get_client(client_id)

        if request.method == "POST":
            form = DataSheetCreateForm(request.POST)
            if form.is_valid():
                service_order_page_services.create_order_for_client(
                    client,
                    form.save(commit=False),
                )
                client_form = ClientDetailForm(instance=client)
                return _render_client_detail(request, client, client_form)
        else:
            next_code = service_order_page_services.get_next_operation_code()
            form = DataSheetCreateForm(initial={"operation_code": next_code})

        return render(
            request,
            TemplatePaths.SERVICE_ORDER_FORM,
            {
                "form": form,
                "client": client,
                **get_access_context(request.user),
            },
        )
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def service_panel(request):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")
    if not can_view_service_panel(request.user):
        return render_forbidden(request, "Seu cargo não pode acessar o painel de serviço.")

    status_filter = (request.GET.get("status") or "all").strip()
    search_query = (request.GET.get("search") or "").strip()
    try:
        context = service_order_page_services.get_service_panel_context(
            status_filter=status_filter,
            search_query=search_query,
        )
        context.update(get_access_context(request.user))
        return render(request, TemplatePaths.SERVICE_ORDER_PANEL, context)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def service_order_detail(request, order_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")
    if not can_view_service_panel(request.user):
        return render_forbidden(request, "Seu cargo não pode acessar o painel de serviço.")

    try:
        context = service_order_page_services.get_service_order_detail_context(
            order_id=order_id,
            search_query=(request.GET.get("search") or "").strip(),
            status_filter=(request.GET.get("status") or "all").strip(),
        )
        context.update(get_access_context(request.user))
        return render(request, TemplatePaths.SERVICE_ORDER_DETAIL, context)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)
