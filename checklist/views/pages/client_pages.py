from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from checklist.forms import ClientDetailForm, ClientForm
from checklist.models import Client
from checklist.templates_paths import TemplatePaths


def _render_client_list(request):
    clients = Client.objects.all().order_by("name")
    query = (request.GET.get("search") or "").strip()

    if query:
        clients = clients.filter(
            models.Q(name__icontains=query)
            | models.Q(email__icontains=query)
            | models.Q(cpf__icontains=query)
            | models.Q(cnpj__icontains=query)
            | models.Q(phone__icontains=query)
        )

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


@login_required(login_url="gerenciador/login/")
def add_cliente(request):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return _render_client_list(request)
    else:
        form = ClientForm()

    return render(request, TemplatePaths.CLIENT_FORM, {"form": form})


@login_required(login_url="gerenciador/login/")
def client_detail(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        form = ClientDetailForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return _render_client_list(request)
    else:
        form = ClientDetailForm(instance=client)

    return render(
        request,
        TemplatePaths.CLIENT_DETAIL,
        {
            "form": form,
            "client": client,
            "current_search": (request.GET.get("search") or "").strip(),
            "current_page": request.GET.get("page", ""),
        },
    )


@login_required(login_url="gerenciador/login/")
def delete_client(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    client = get_object_or_404(Client, id=client_id)
    client.delete()
    return _render_client_list(request)


@login_required(login_url="gerenciador/login/")
def client_list(request):
    return _render_client_list(request)
