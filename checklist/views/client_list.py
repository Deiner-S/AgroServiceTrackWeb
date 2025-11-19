from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from checklist.models import Client
from django.db import models

@login_required(login_url='gerenciador/login/')
def client_list(request):
    query = request.GET.get("search", "")
    clients = Client.objects.all()
    if query:
        clients = clients.filter(
            models.Q(name__icontains=query) | models.Q(email__icontains=query)
        )
    return render(request, "cliente/list_clients.html", {"clients": clients})


    
