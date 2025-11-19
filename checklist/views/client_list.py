from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from checklist.models import Client

@login_required(login_url='gerenciador/login/')
def client_list(request):
    clients = Client.objects.all()
    return render(request, "cliente/list_clients.html", {"clients": clients})


    
