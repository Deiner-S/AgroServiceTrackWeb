from django.urls import path
from checklist.views import *


urlpatterns = [
    path('client/', add_cliente, name='add_client'),
    path('employee/', add_employee, name='add_employee'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('clients/', client_list, name='client-list'),
    path("clients/<uuid:client_id>/services/", open_client_order, name="open_client_order"),
    path("clients/<uuid:client_id>/services/add_service", add_order, name="add_service"),
    path("panel/", service_panel, name="service_panel"),
    path("work_order_api/", pending_work_order, name="work_order"),
    path("dowload_checklist_items_api/", dowload_checklist_items, name="dowload_checklist_items"),
]
