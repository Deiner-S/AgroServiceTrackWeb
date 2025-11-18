
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from checklist.forms import WorkerForm
from django.contrib.auth import login


User = get_user_model()

@login_required(login_url='gerenciador/login/')
def worker_register(request):
    if request.method == "POST":
        form = WorkerForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)  # cria sem salvar ainda
            user.set_password(form.cleaned_data["password"])  # hash da senha
            user.save()

            login(request, user)
            return redirect('home')
    else:
        form = WorkerForm()

    return render(request, 'worker/form_worker.html', {"form": form})