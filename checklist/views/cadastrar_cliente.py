

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from checklist.forms import ClienteForm

@login_required(login_url='gerenciador/login/')
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sucesso')  # redireciona pra uma tela de sucesso
    else:
        form = ClienteForm()
    
    return render(request, 'cliente/form_cliente.html', {'form': form})