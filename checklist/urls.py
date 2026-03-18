from django.urls import path
from checklist.views import *
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

urlpatterns = [
    path('client/', add_cliente, name='add_client'),
    path('clients/<uuid:client_id>/detail/', client_detail, name='client-detail'),
    path('clients/<uuid:client_id>/delete/', delete_client, name='delete-client'),
    path('checklist-item/', add_checklist_item, name='add_checklist_item'),
    path('checklist-items/', checklist_item_list, name='checklist-item-list'),
    path('checklist-items/<uuid:item_id>/toggle-status/', toggle_checklist_item_status, name='toggle_checklist_item_status'),
    path('employee/', add_employee, name='add_employee'),
    path('employees/', employee_list, name='employee-list'),
    path('employees/<uuid:employee_id>/detail/', employee_detail, name='employee-detail'),
    path('employees/<uuid:employee_id>/delete/', delete_employee, name='delete-employee'),
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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
