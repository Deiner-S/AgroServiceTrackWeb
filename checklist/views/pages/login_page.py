from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from checklist.templates.templates_paths import TemplatePaths
from django.urls import reverse

def login(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')

        # 1) Autentica usuário
        user = authenticate(request, username=usuario, password=senha)

        # 2) Se autenticou com sucesso
        if user is not None:
            # 3) Gera a sessão de login
            login(request, user)
            return redirect('home')

        # 4) Se falhar, volta para o login com erro
        return render(request, TemplatePaths.LOGIN, {'erro': 'Usuário ou senha inválidos.'})

    # GET → mostra tela de login
    return render(request, TemplatePaths.LOGIN)

def logout_view(request):
    logout(request)   # Encerra a sessão
    return redirect(reverse("login"))