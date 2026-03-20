from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Max
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from checklist.forms import ClientDetailForm, DataSheetCreateForm
from checklist.models import Client, WorkOrder
from checklist.templates_paths import TemplatePaths
from checklist.views.pages.client_pages import _render_client_detail


@login_required(login_url="gerenciador/login/")
def open_client_order(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    client = get_object_or_404(Client, id=client_id)
    form = ClientDetailForm(instance=client)
    return _render_client_detail(request, client, form)


@login_required(login_url="gerenciador/login/")
def add_order(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso invalido")

    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        form = DataSheetCreateForm(request.POST)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.client = client
            work_order.save()
            client_form = ClientDetailForm(instance=client)
            return _render_client_detail(request, client, client_form)
    else:
        last_code = WorkOrder.objects.aggregate(Max("operation_code"))["operation_code__max"]
        next_code = "000001" if not last_code else f"{int(last_code) + 1:06d}"
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

    orders = WorkOrder.objects.select_related("client").order_by("-insert_date")

    if status_filter != "all":
        orders = orders.filter(status=status_filter)

    if search_query:
        orders = orders.filter(
            models.Q(operation_code__icontains=search_query)
            | models.Q(client__name__icontains=search_query)
            | models.Q(symptoms__icontains=search_query)
            | models.Q(service__icontains=search_query)
            | models.Q(chassi__icontains=search_query)
            | models.Q(model__icontains=search_query)
            | models.Q(horimetro__icontains=search_query)
        )

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

    order = get_object_or_404(
        WorkOrder.objects.select_related("client").prefetch_related(
            "checklists__employee",
            "checklists__checklist_item_fk",
        ),
        id=order_id,
    )

    return render(
        request,
        TemplatePaths.SERVICE_ORDER_DETAIL,
        {
            "order": order,
            "current_search": (request.GET.get("search") or "").strip(),
            "selected_status": (request.GET.get("status") or "all").strip(),
        },
    )
