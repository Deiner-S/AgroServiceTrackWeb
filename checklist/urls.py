from django.urls import path
from checklist.views import *


urlpatterns = [
    path('client/', add_cliente, name='add_client'),
    path('employee/', add_employee, name='add_employee'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('clients/', client_list, name='client-list'),
    path("clients/<int:client_id>/services/", open_client_services, name="open_client_services"),
    path("clients/<int:client_id>/services/add_service", add_service, name="add_service"),

]
