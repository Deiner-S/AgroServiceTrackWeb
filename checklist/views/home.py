# clientes/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from checklist.templates.templates_paths import TemplatePaths

@login_required(login_url='gerenciador/login/')
def home(request):
    return render(request, TemplatePaths.HOME)
