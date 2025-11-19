from django.shortcuts import get_object_or_404, render #garante que, se o cliente não existir, retorna 404
from checklist.models import Client, DataSheet
from django.contrib.auth.decorators import login_required

@login_required
def open_client_services(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    services = DataSheet.objects.filter(client=client)

    return render(request, "cliente/open_services.html", {
        "client": client,
        "services": services
    })