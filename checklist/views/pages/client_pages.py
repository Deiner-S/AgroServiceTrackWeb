from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from checklist.forms import ClientDetailForm, ClientForm
from checklist.repository import client_repository, work_order_repository
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.address_pages import get_address_section_context


def _render_client_list(request):
    query = (request.GET.get("search") or "").strip()
    clients = client_repository.list_for_management(query)

    paginator = Paginator(clients, 10)
    page_number = request.GET.get("page")
    page_client = paginator.get_page(page_number)

    return render(
        request,
        TemplatePaths.CLIENT_LIST,
        {
            "page_client": page_client,
            "current_search": query,
        },
    )


def _render_client_detail(request, client, form):
    services = work_order_repository.list_by_client(client)
    address_context = get_address_section_context(client, "client")

    return render(
        request,
        TemplatePaths.CLIENT_DETAIL,
        {
            "form": form,
            "client": client,
            "services": services,
            "current_search": (request.GET.get("search") or "").strip(),
            "current_page": request.GET.get("page", ""),
            **address_context,
        },
    )


@login_required(login_url="gerenciador/login/")
def add_cliente(request):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client_repository.save(form.save(commit=False))
            return _render_client_list(request)
    else:
        form = ClientForm()

    return render(request, TemplatePaths.CLIENT_FORM, {"form": form})


@login_required(login_url="gerenciador/login/")
def client_detail(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    client = client_repository.get_or_404(id=client_id)

    if request.method == "POST":
        form = ClientDetailForm(request.POST, instance=client)
        if form.is_valid():
            client_repository.save(form.save(commit=False))
            return _render_client_list(request)
    else:
        form = ClientDetailForm(instance=client)

    return _render_client_detail(request, client, form)


@login_required(login_url="gerenciador/login/")
def delete_client(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    client = client_repository.get_or_404(id=client_id)
    client_repository.delete(client)
    return _render_client_list(request)


@login_required(login_url="gerenciador/login/")
def client_list(request):
    return _render_client_list(request)
