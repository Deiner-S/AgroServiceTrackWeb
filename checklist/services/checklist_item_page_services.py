from checklist.exception_handler import unwrap_repository_result
from checklist.repository import checklist_item_repository
from checklist.services.page_common_services import paginate_items


def get_checklist_item_list_context(*, search_query="", page_number=None):
    checklist_items = unwrap_repository_result(
        checklist_item_repository.list_for_management(search_query)
    )
    page_checklist_items = paginate_items(checklist_items, page_number)
    return {
        "page_checklist_items": page_checklist_items,
        "current_search": search_query,
    }


def get_checklist_item(item_id):
    return unwrap_repository_result(checklist_item_repository.get_by_id(item_id))


def save_checklist_item(checklist_item):
    return unwrap_repository_result(checklist_item_repository.save(checklist_item))


def toggle_checklist_item_status(item_id):
    checklist_item = get_checklist_item(item_id)
    return unwrap_repository_result(
        checklist_item_repository.toggle_status(checklist_item)
    )


def get_checklist_item_detail_context(*, checklist_item, form, search_query="", page_number=""):
    return {
        "form": form,
        "checklist_item": checklist_item,
        "current_search": search_query,
        "current_page": page_number,
    }
