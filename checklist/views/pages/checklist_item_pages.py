from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest

from checklist.forms import ChecklistItemForm
from checklist.exception_handler import RepositoryOperationError
from checklist.permissions import (
    can_manage_checklist_item,
    can_view_checklist_item_module,
    get_access_context,
)
from checklist.services import checklist_item_page_services
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.view_utils import render_forbidden, render_page, render_repository_error


def _render_checklist_item_list(request):
    query = (request.GET.get("search") or "").strip()
    context = checklist_item_page_services.get_checklist_item_list_context(
        search_query=query,
        page_number=request.GET.get("page"),
    )
    context.update(get_access_context(request.user))
    return render_page(request, TemplatePaths.CHECKLIST_ITEM_LIST, context)


def _render_checklist_item_detail(request, checklist_item, form):
    context = checklist_item_page_services.get_checklist_item_detail_context(
        checklist_item=checklist_item,
        form=form,
        search_query=(request.GET.get("search") or "").strip(),
        page_number=request.GET.get("page", ""),
    )
    context.update(get_access_context(request.user))
    return render_page(request, TemplatePaths.CHECKLIST_ITEM_DETAIL, context)


@login_required(login_url="gerenciador/login/")
def checklist_item_list(request):
    try:
        if not can_view_checklist_item_module(request.user):
            return render_forbidden(request, "Seu cargo nao pode acessar checklist.")
        return _render_checklist_item_list(request)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def add_checklist_item(request):
    if not can_manage_checklist_item(request.user):
        return render_forbidden(request, "Seu cargo nao pode cadastrar itens de checklist.")

    try:
        if request.method == "POST":
            form = ChecklistItemForm(request.POST)
            if form.is_valid():
                checklist_item_page_services.save_checklist_item(form.save(commit=False))
                return _render_checklist_item_list(request)
        else:
            form = ChecklistItemForm()

        return render_page(
            request,
            TemplatePaths.CHECKLIST_ITEM_FORM,
            {
                "form": form,
                **get_access_context(request.user),
            },
        )
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def checklist_item_detail(request, item_id):
    if not can_manage_checklist_item(request.user):
        return render_forbidden(request, "Seu cargo nao pode editar itens de checklist.")

    try:
        checklist_item = checklist_item_page_services.get_checklist_item(item_id)

        if request.method == "POST":
            form = ChecklistItemForm(request.POST, instance=checklist_item)
            if form.is_valid():
                checklist_item_page_services.save_checklist_item(form.save(commit=False))
                return _render_checklist_item_list(request)
        else:
            form = ChecklistItemForm(instance=checklist_item)

        return _render_checklist_item_detail(request, checklist_item, form)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)


@login_required(login_url="gerenciador/login/")
def toggle_checklist_item_status(request, item_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")
    if not can_manage_checklist_item(request.user):
        return render_forbidden(request, "Seu cargo nao pode alterar itens de checklist.")

    try:
        checklist_item = checklist_item_page_services.toggle_checklist_item_status(item_id)
        form = ChecklistItemForm(instance=checklist_item)
        return _render_checklist_item_detail(request, checklist_item, form)
    except RepositoryOperationError as exc:
        return render_repository_error(request, exc)
