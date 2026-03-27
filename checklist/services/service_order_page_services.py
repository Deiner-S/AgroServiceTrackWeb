from checklist.exception_handler import unwrap_repository_result
from checklist.repository import work_order_repository

STATUS_OPTIONS = [
    ("all", "Todos"),
    ("1", "Pendente"),
    ("2", "Andamento"),
    ("3", "Entrega"),
    ("4", "Finalizada"),
]


def get_next_operation_code():
    return unwrap_repository_result(work_order_repository.get_next_operation_code())


def create_order_for_client(client, work_order):
    work_order.client = client
    return unwrap_repository_result(work_order_repository.save(work_order))


def get_service_panel_context(*, status_filter="all", search_query=""):
    allowed_status = {value for value, _ in STATUS_OPTIONS}
    normalized_status = status_filter if status_filter in allowed_status else "all"
    orders = unwrap_repository_result(
        work_order_repository.list_for_panel(
            status_filter=normalized_status,
            search_query=search_query,
        )
    )
    return {
        "orders": orders,
        "selected_status": normalized_status,
        "current_search": search_query,
        "status_options": STATUS_OPTIONS,
    }


def get_service_order_detail_context(*, order_id, search_query="", status_filter="all"):
    order = unwrap_repository_result(work_order_repository.get_detail_by_id(order_id))
    return {
        "order": order,
        "current_search": search_query,
        "selected_status": status_filter,
    }
