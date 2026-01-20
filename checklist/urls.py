from django.urls import path
from checklist.views import *


urlpatterns = [
    path('client/', add_cliente, name='add_client'),
    path('employee/', add_employee, name='add_employee'),
    path('login/', auth_login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('clients/', client_list, name='client-list'),
    path("clients/<uuid:client_id>/services/", open_client_order, name="open_client_order"),
    path("clients/<uuid:client_id>/services/add_service", add_order, name="add_service"),
    path("panel/", service_panel, name="service_panel"),
    path("send_work_orders_api/", send_pending_work_order, name="send_work_orders_api"),
    path("send_checklist_items_api/", send_checklist_items, name="send_checklist_items_api"),
    path("receive_work_orders_api/", receive_work_orders_api, name="receive_work_orders_api"),
    path("receive_checklist_api/", receive_checkLists_filleds, name="receive_checkLists_filleds"),
]
