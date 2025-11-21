

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from checklist.forms import ClientForm
from django.http import HttpResponseBadRequest
from checklist.templates.templates_paths import TemplatePaths
from checklist.models import Client
from django.db import models
from django.core.paginator import Paginator




@login_required(login_url='gerenciador/login/')
def add_cliente(request):
    if not request.headers.get("HX-Request"):
            return HttpResponseBadRequest("Acesso inválido")
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ClientForm()
    
    return render(request, TemplatePaths.CLIENT_FORM, {'form': form})




@login_required(login_url='gerenciador/login/')
def client_list(request):
    clients = Client.objects.all().order_by("name")
    query = request.GET.get("search", "")
    

    if query:
        clients = clients.filter(
            models.Q(name__icontains=query) | models.Q(email__icontains=query)
        )

    page_number = request.GET.get("page")
    paginator = Paginator(clients, 10)
    page_client = paginator.get_page(page_number)
    
    return render(request, TemplatePaths.CLIENT_LIST, {"page_client": page_client})