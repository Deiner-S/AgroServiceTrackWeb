from checklist.exception_handler import unwrap_repository_result
from checklist.repository import client_repository, work_order_repository
from checklist.services.address_page_services import get_address_section_context
from checklist.services.page_common_services import paginate_items


def get_client_list_context(*, search_query="", page_number=None):
    clients = unwrap_repository_result(client_repository.list_for_management(search_query))
    page_client = paginate_items(clients, page_number)
    return {
        "page_client": page_client,
        "current_search": search_query,
    }


def get_client(client_id):
    return unwrap_repository_result(client_repository.get_by_id(client_id))


def save_client(client):
    return unwrap_repository_result(client_repository.save(client))


def delete_client(client_id):
    client = get_client(client_id)
    unwrap_repository_result(client_repository.delete(client))


def get_client_detail_context(*, client, form, search_query="", page_number=""):
    services = unwrap_repository_result(work_order_repository.list_by_client(client))
    address_context = get_address_section_context(client, "client")
    return {
        "form": form,
        "client": client,
        "services": services,
        "current_search": search_query,
        "current_page": page_number,
        **address_context,
    }
