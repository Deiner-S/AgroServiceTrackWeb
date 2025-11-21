from django.shortcuts import get_object_or_404, render #garante que, se o cliente não existir, retorna 404
from checklist.models import Client, DataSheet
from django.contrib.auth.decorators import login_required
from checklist.templates.templates_paths import TemplatePaths


@login_required(login_url='gerenciador/login/')
def open_client_services(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    services = DataSheet.objects.filter(client=client)

    return render(request, TemplatePaths.SERVICE_ORDER_LIST, {
        "client": client,
        "services": services
    })

@login_required(login_url='gerenciador/login/')
def add_service(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    return render(request, TemplatePaths.SERVICE_ORDER_FORM, {
        "client": client,
        #"services": services
    })