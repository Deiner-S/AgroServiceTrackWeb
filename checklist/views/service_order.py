from django.shortcuts import get_object_or_404, render, redirect
from checklist.models import Client, WorkOrder
from django.contrib.auth.decorators import login_required
from checklist.templates.templates_paths import TemplatePaths
from checklist.forms import DataSheetCreateForm
from django.db.models import Max

@login_required(login_url='gerenciador/login/')
def open_client_order(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    services = WorkOrder.objects.filter(client=client)

    return render(request, TemplatePaths.SERVICE_ORDER_LIST, {
        "client": client,
        "services": services
    })

@login_required(login_url='gerenciador/login/')
def add_order(request, client_id):
    client = Client.objects.get(id=client_id)


    if request.method == "POST":
        form = DataSheetCreateForm(request.POST)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.client = client
            work_order.save()
            
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
    orders = WorkOrder.objects.exclude(status="FINALIZADO")
    return render(request, TemplatePaths.SERVICE_ORDER_PANEL, {"orders": orders})