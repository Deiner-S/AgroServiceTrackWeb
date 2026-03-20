from django.urls import path
from checklist.views import *
from checklist.auth_views import (
    ActiveEmployeeTokenObtainPairView,
    ActiveEmployeeTokenRefreshView,
)

urlpatterns = [
    path('client/', add_cliente, name='add_client'),
    path('clients/<uuid:client_id>/detail/', client_detail, name='client-detail'),
    path('clients/<uuid:client_id>/delete/', delete_client, name='delete-client'),
    path('clients/<uuid:client_id>/addresses/add/', add_client_address, name='add-client-address'),
    path('clients/<uuid:client_id>/addresses/<uuid:address_id>/delete/', delete_client_address, name='delete-client-address'),
    path('checklist-item/', add_checklist_item, name='add_checklist_item'),
    path('checklist-items/', checklist_item_list, name='checklist-item-list'),
    path('checklist-items/<uuid:item_id>/detail/', checklist_item_detail, name='checklist-item-detail'),
    path('checklist-items/<uuid:item_id>/toggle-status/', toggle_checklist_item_status, name='toggle_checklist_item_status'),
    path('employee/', add_employee, name='add_employee'),
    path('employees/', employee_list, name='employee-list'),
    path('employees/<uuid:employee_id>/detail/', employee_detail, name='employee-detail'),
    path('employees/<uuid:employee_id>/delete/', delete_employee, name='delete-employee'),
    path('employees/<uuid:employee_id>/toggle-status/', toggle_employee_status, name='toggle-employee-status'),
    path('employees/<uuid:employee_id>/addresses/add/', add_employee_address, name='add-employee-address'),
    path('employees/<uuid:employee_id>/addresses/<uuid:address_id>/delete/', delete_employee_address, name='delete-employee-address'),
    path('login/', auth_login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('clients/', client_list, name='client-list'),
    path("clients/<uuid:client_id>/services/", open_client_order, name="open_client_order"),
    path("clients/<uuid:client_id>/services/add_service", add_order, name="add_service"),
    path("panel/", service_panel, name="service_panel"),
    path("panel/<uuid:order_id>/detail/", service_order_detail, name="service_order_detail"),
    path("send_work_orders_api/", send_pending_work_order, name="send_work_orders_api"),
    path("send_checklist_items_api/", send_checklist_items, name="send_checklist_items_api"),
    path("receive_work_orders_api/", receive_work_orders_api, name="receive_work_orders_api"),
    path("receive_checklist_api/", receive_checkLists_filleds, name="receive_checkLists_filleds"),
    path('api/token/', ActiveEmployeeTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', ActiveEmployeeTokenRefreshView.as_view(), name='token_refresh'),
]
