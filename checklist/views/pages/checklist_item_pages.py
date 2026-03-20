from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from checklist.forms import ChecklistItemForm
from checklist.models import ChecklistItem
from checklist.templates_paths import TemplatePaths


def _render_checklist_item_list(request):
    checklist_items = ChecklistItem.objects.all().order_by("name")
    query = (request.GET.get("search") or "").strip()

    if query:
        checklist_items = checklist_items.filter(models.Q(name__icontains=query))

    paginator = Paginator(checklist_items, 10)
    page_number = request.GET.get("page")
    page_checklist_items = paginator.get_page(page_number)

    return render(
        request,
        TemplatePaths.CHECKLIST_ITEM_LIST,
        {
            "page_checklist_items": page_checklist_items,
            "current_search": query,
        },
    )


def _render_checklist_item_detail(request, checklist_item, form):
    return render(
        request,
        TemplatePaths.CHECKLIST_ITEM_DETAIL,
        {
            "form": form,
            "checklist_item": checklist_item,
            "current_search": (request.GET.get("search") or "").strip(),
            "current_page": request.GET.get("page", ""),
        },
    )


@login_required(login_url="gerenciador/login/")
def checklist_item_list(request):
    return _render_checklist_item_list(request)


@login_required(login_url="gerenciador/login/")
def add_checklist_item(request):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method == "POST":
        form = ChecklistItemForm(request.POST)
        if form.is_valid():
            form.save()
            return _render_checklist_item_list(request)
    else:
        form = ChecklistItemForm()

    return render(request, TemplatePaths.CHECKLIST_ITEM_FORM, {"form": form})


@login_required(login_url="gerenciador/login/")
def checklist_item_detail(request, item_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    checklist_item = get_object_or_404(ChecklistItem, id=item_id)

    if request.method == "POST":
        form = ChecklistItemForm(request.POST, instance=checklist_item)
        if form.is_valid():
            form.save()
            return _render_checklist_item_list(request)
    else:
        form = ChecklistItemForm(instance=checklist_item)

    return _render_checklist_item_detail(request, checklist_item, form)


@login_required(login_url="gerenciador/login/")
def toggle_checklist_item_status(request, item_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    if request.method != "POST":
        return HttpResponseBadRequest("Metodo invalido")

    checklist_item = get_object_or_404(ChecklistItem, id=item_id)
    checklist_item.status = 0 if checklist_item.status == 1 else 1
    checklist_item.save(update_fields=["status"])
    form = ChecklistItemForm(instance=checklist_item)
    return _render_checklist_item_detail(request, checklist_item, form)
