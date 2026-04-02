from django.contrib.auth import get_user_model

from checklist.models import Checklist, ChecklistItem, Client, WorkOrder
from checklist.repository import (
    address_repository,
    checklist_item_repository,
    checklist_repository,
    client_repository,
    employee_repository,
    work_order_repository,
)
from checklist.exception_handler import unwrap_repository_result
from checklist.utils.data_processing import prepare_image
from checklist.utils.logging_utils import save_mobile_log
from checklist.permissions import (
    can_create_service_order,
    can_manage_client,
    can_manage_client_addresses,
    get_access_context,
)


Employee = get_user_model()


def get_pending_work_order():
    """Retorna ordens com status 1, 2 ou 3 para sincronizacao do app."""
    items = unwrap_repository_result(work_order_repository.list_pending_for_api_sync())
    data = []

    for item in items:
        data.append(
            {
                "id": item.id,
                "operation_code": item.operation_code,
                "symptoms": item.symptoms,
                "client": item.client.name,
                "status": item.status,
                "status_sync": 1,
                "chassi": item.chassi,
                "horimetro": item.horimetro,
                "model": item.model,
                "date_in": item.date_in.isoformat() if item.date_in else None,
                "date_out": item.date_out.isoformat() if item.date_out else None,
                "service": item.service,
                "insertDate": item.insert_date.isoformat() if item.insert_date else None,
            }
        )

    return data


def get_checklist_items():
    items = unwrap_repository_result(checklist_item_repository.list_for_api_sync())
    return [
        {
            "id": item.id,
            "name": item.name,
            "status": item.status,
        }
        for item in items
    ]


def save_work_orders_filleds(work_orders):
    for work_order in work_orders:
        wo = work_order["work_order"]

        wo.chassi = work_order["chassi"]
        wo.horimetro = work_order["horimetro"]
        wo.model = work_order["model"]
        wo.date_in = work_order["date_in"]
        wo.date_out = work_order["date_out"]
        wo.status = work_order["status"]
        wo.service = work_order["service"]

        if work_order["signature_in"]:
            wo.signature_in = work_order["signature_in"]

        if work_order["signature_out"]:
            wo.signature_out = work_order["signature_out"]

        unwrap_repository_result(work_order_repository.save(wo))


def save_checklists_filleds(checklists, employee_id):
    employee = unwrap_repository_result(employee_repository.get_by_identifier(employee_id))

    for data in checklists:
        checklist_obj = unwrap_repository_result(
            checklist_repository.find_latest_by_work_order_and_item(
                data["work_order"],
                data["checklist_item"],
            )
        )

        if checklist_obj is None:
            checklist_obj = Checklist(
                id=data["id"],
                work_order_fk=data["work_order"],
                checklist_item_fk=data["checklist_item"],
            )

        checklist_obj.employee = employee
        checklist_obj.status = data["status"] or checklist_obj.status

        if not checklist_obj.status:
            raise ValueError("Checklist status is required")

        if data["image_in"]:
            checklist_obj.image_in = data["image_in"]

        if data["image_out"]:
            checklist_obj.image_out = data["image_out"]

        unwrap_repository_result(checklist_repository.save(checklist_obj))


def save_mobile_logs(log_entries, request=None):
    for log_entry in log_entries:
        save_mobile_log(log_entry, request=request)


def _build_address_payload(address):
    return {
        "id": str(address.id),
        "label": str(address),
    }


def _build_client_payload(client):
    return {
        "id": str(client.id),
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "cpf": client.cpf,
        "cnpj": client.cnpj,
        "addressCount": client.addresses.count(),
        "insertDate": client.insert_date.isoformat() if client.insert_date else None,
    }


def _build_employee_payload(employee):
    full_name = f"{employee.first_name} {employee.last_name}".strip() or employee.username

    return {
        "id": str(employee.id),
        "username": employee.username,
        "fullName": full_name,
        "email": employee.email,
        "cpf": employee.cpf,
        "phone": employee.phone,
        "position": employee.position,
        "positionLabel": employee.get_position_display(),
        "isActive": bool(employee.is_active),
        "addressCount": employee.addresses.count(),
        "insertDate": employee.insert_date.isoformat() if employee.insert_date else None,
    }


def _build_checklist_item_payload(item):
    return {
        "id": str(item.id),
        "name": item.name,
        "status": int(item.status),
        "statusLabel": "Ativo" if item.status == 1 else "Inativo",
        "usageCount": item.executions.count(),
        "insertDate": item.insert_date.isoformat() if item.insert_date else None,
    }


def _build_related_order_payload(order):
    return {
        "id": str(order.id),
        "operationCode": order.operation_code,
        "status": order.status,
        "statusLabel": order.get_status_display(),
        "insertDate": order.insert_date.isoformat() if order.insert_date else None,
    }


def _build_client_detail_permissions(user):
    can_create_order = can_create_service_order(user)

    return {
        "canEditClient": can_manage_client(user),
        "canManageAddresses": can_manage_client_addresses(user),
        "canCreateServiceOrder": can_create_order,
        "nextOperationCode": (
            unwrap_repository_result(work_order_repository.get_next_operation_code())
            if can_create_order
            else None
        ),
    }


def get_mobile_dashboard(user):
    access_context = get_access_context(user)

    modules = [
        {
            "id": "orders",
            "title": "Ordens",
            "description": "Acompanhe o fluxo operacional das ordens em campo.",
            "icon": "assignment",
            "route": "ordersScreen",
            "count": WorkOrder.objects.exclude(status="4").count(),
            "enabled": access_context["can_view_service_panel"],
        },
        {
            "id": "clients",
            "title": "Clientes",
            "description": "Consulte cadastros e relacoes de atendimento.",
            "icon": "groups",
            "route": "clientsScreen",
            "count": Client.objects.count(),
            "enabled": access_context["can_view_client_list"],
        },
        {
            "id": "employees",
            "title": "Funcionarios",
            "description": "Gerencie equipe, status e acessos.",
            "icon": "badge",
            "route": "employeesScreen",
            "count": Employee.objects.count(),
            "enabled": access_context["can_view_employee_module"],
        },
        {
            "id": "checklist_items",
            "title": "Checklist",
            "description": "Acompanhe os itens usados nas inspeções.",
            "icon": "fact-check",
            "route": "checklistItemsScreen",
            "count": ChecklistItem.objects.count(),
            "enabled": access_context["can_view_checklist_item_module"],
        },
    ]

    full_name = f"{user.first_name} {user.last_name}".strip() or user.username

    return {
        "user": {
            "username": user.username,
            "fullName": full_name,
            "position": user.get_position_display(),
        },
        "summary": {
            "pendingOrders": WorkOrder.objects.filter(status="1").count(),
            "inProgressOrders": WorkOrder.objects.filter(status="2").count(),
            "deliveryOrders": WorkOrder.objects.filter(status="3").count(),
            "completedOrders": WorkOrder.objects.filter(status="4").count(),
            "clients": Client.objects.count(),
            "employees": Employee.objects.count(),
            "checklistItems": ChecklistItem.objects.count(),
        },
        "modules": modules,
        "access": access_context,
    }


def get_mobile_clients(search_query=""):
    clients = unwrap_repository_result(client_repository.list_for_management(search_query))
    return [_build_client_payload(client) for client in clients]


def get_mobile_client_detail(client_id, user):
    client = unwrap_repository_result(client_repository.get_by_id(client_id))
    orders = unwrap_repository_result(work_order_repository.list_by_client(client))

    return {
        **_build_client_payload(client),
        "addresses": [_build_address_payload(address) for address in client.addresses.all()],
        "recentOrders": [_build_related_order_payload(order) for order in orders[:10]],
        "permissions": _build_client_detail_permissions(user),
    }


def create_mobile_client(client):
    saved_client = unwrap_repository_result(client_repository.save(client))
    return saved_client


def update_mobile_client(client):
    saved_client = unwrap_repository_result(client_repository.save(client))
    return saved_client


def create_mobile_client_address(client, address):
    saved_address = unwrap_repository_result(address_repository.save(address))
    unwrap_repository_result(address_repository.add_to_client(client, saved_address))
    return saved_address


def create_mobile_client_order(client, work_order):
    work_order.client = client
    return unwrap_repository_result(work_order_repository.save(work_order))


def get_mobile_employees(search_query=""):
    employees = unwrap_repository_result(employee_repository.list_for_management(search_query))
    return [_build_employee_payload(employee) for employee in employees]


def get_mobile_employee_detail(employee_id):
    employee = unwrap_repository_result(employee_repository.get_by_identifier(employee_id))

    return {
        **_build_employee_payload(employee),
        "addresses": [_build_address_payload(address) for address in employee.addresses.all()],
    }


def toggle_mobile_employee_status(employee_id):
    employee = unwrap_repository_result(employee_repository.get_by_identifier(employee_id))
    updated = unwrap_repository_result(employee_repository.toggle_active_status(employee))
    return {"ok": True, "isActive": bool(updated.is_active)}


def get_mobile_checklist_items(search_query=""):
    items = unwrap_repository_result(checklist_item_repository.list_for_management(search_query))
    return [_build_checklist_item_payload(item) for item in items]


def get_mobile_checklist_item_detail(item_id):
    item = unwrap_repository_result(checklist_item_repository.get_by_id(item_id))
    return _build_checklist_item_payload(item)


def toggle_mobile_checklist_item_status(item_id):
    item = unwrap_repository_result(checklist_item_repository.get_by_id(item_id))
    updated = unwrap_repository_result(checklist_item_repository.toggle_status(item))
    return {"ok": True, "status": int(updated.status)}
