from django.urls import path
from checklist.views import *


urlpatterns = [
    path('client/', cadastrar_cliente, name='register_client'),
    path('sucesso/', sucesso, name='success'),
    path('worker/', worker_register, name='register_worker'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('clients/', client_list, name='client-list')
]
