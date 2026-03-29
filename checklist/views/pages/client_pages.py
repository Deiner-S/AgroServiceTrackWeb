from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from checklist.forms import ClientDetailForm, ClientForm
from checklist.exception_handler import RepositoryOperationError
from checklist.services import client_page_services
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.view_utils import render_repository_error


def _render_client_list(request):
    query = (request.GET.get("search") or "").strip()
    context = client_page_services.get_client_list_context(
        search_query=query,
        page_number=request.GET.get("page"),
    )
    return render(request, TemplatePaths.CLIENT_LIST, context)


def _render_client_detail(request, client, form):
    context = client_page_services.get_client_detail_context(
        client=client,
        form=form,
        search_query=(request.GET.get("search") or "").strip(),
        page_number=request.GET.get("page", ""),
    )
    return render(
        request,
        TemplatePaths.CLIENT_DETAIL,
        context,
    )


@login_required(login_url="gerenciador/login/")
def add_cliente(request):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")

    try:
        if request.method == "POST":
            form = ClientForm(request.POST)
            if form.is_valid():
                client_page_services.save_client(form.save(commit=False))
                return _render_client_list(request)
        else:
            form = ClientForm()

        return render(request, TemplatePaths.CLIENT_FORM, {"form": form})
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def client_detail(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")

    try:
        client = client_page_services.get_client(client_id)

        if request.method == "POST":
            form = ClientDetailForm(request.POST, instance=client)
            if form.is_valid():
                client_page_services.save_client(form.save(commit=False))
                return _render_client_list(request)
        else:
            form = ClientDetailForm(instance=client)

        return _render_client_detail(request, client, form)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def delete_client(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")

    if request.method != "POST":
        return HttpResponseBadRequest("Método inválido")

    try:
        client_page_services.delete_client(client_id)
        return _render_client_list(request)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def client_list(request):
    try:
        return _render_client_list(request)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)
