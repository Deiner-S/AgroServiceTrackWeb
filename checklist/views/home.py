# clientes/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='gerenciador/login/')
def home(request):
    return render(request, 'home.html')



def sucesso(request):
    return render(request, 'cliente/sucesso.html')