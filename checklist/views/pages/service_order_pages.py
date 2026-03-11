from django.shortcuts import get_object_or_404, render
from checklist.models import Client, WorkOrder
from django.contrib.auth.decorators import login_required
from checklist.templates_paths import TemplatePaths
from checklist.forms import DataSheetCreateForm
from django.db.models import Max
from django.http import HttpResponseBadRequest

@login_required(login_url='gerenciador/login/')
def open_client_order(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")

    client = get_object_or_404(Client, id=client_id)
    services = WorkOrder.objects.filter(client=client).order_by("-insert_date")

    return render(request, TemplatePaths.SERVICE_ORDER_LIST, {
        "client": client,
        "services": services
    })

@login_required(login_url='gerenciador/login/')
def add_order(request, client_id):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")

    client = get_object_or_404(Client, id=client_id)


    if request.method == "POST":
        form = DataSheetCreateForm(request.POST)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.client = client
            work_order.save()
            services = WorkOrder.objects.filter(client=client).order_by("-insert_date")
            return render(request, TemplatePaths.SERVICE_ORDER_LIST, {
                "client": client,
                "services": services
            })
            
    else:
        last_code = WorkOrder.objects.aggregate(Max("operation_code"))["operation_code__max"]
        next_code = "000001" if not last_code else f"{int(last_code) + 1:06d}"

        form = DataSheetCreateForm(initial={"operation_code": next_code})

    return render(request, TemplatePaths.SERVICE_ORDER_FORM, {
        "form": form,
        "client": client,
    })


@login_required(login_url='gerenciador/login/')
def service_panel(request):
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Acesso inválido")

    status_filter = (request.GET.get("status") or "all").strip()
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

    return render(
        request,
        TemplatePaths.SERVICE_ORDER_PANEL,
        {
            "orders": orders,
            "selected_status": status_filter,
            "status_options": status_options,
        },
    )