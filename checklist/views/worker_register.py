
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from checklist.forms import WorkerForm
from django.shortcuts import render
import random

@login_required(login_url='gerenciador/login/')
def worker_register(request):
    if request.method == 'POST':
        form = WorkerForm(request.POST)

        if form.is_valid():
            # 1) Gera username baseado no email
            email = form.cleaned_data['email']
            username = email.split("@")[0]

            # Evitar duplicidade
            if User.objects.filter(username=username).exists():
                username = username + str(random.randint(1000, 9999))

            # 2) Gera senha automática
            senha = form["cpf"]

            # 3) Cria o usuário na auth_user
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(senha)
            )

            # 4) Cria o funcionário vinculado ao user
            funcionario = form.save(commit=False)
            funcionario.user = user
            funcionario.save()

            return render(request, 'worker/sucesso.html', {
                'username': username,
                'senha': senha
            })

    else:
        form = WorkerForm()

    return render(request, 'worker/form_worker.html', {'form': form})