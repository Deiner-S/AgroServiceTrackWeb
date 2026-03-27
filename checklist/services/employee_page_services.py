from checklist.exception_handler import unwrap_repository_result
from checklist.repository import employee_repository
from checklist.services.address_page_services import get_address_section_context
from checklist.services.page_common_services import paginate_items


def get_employee_list_context(*, search_query="", page_number=None):
    employees = unwrap_repository_result(
        employee_repository.list_for_management(search_query)
    )
    page_employees = paginate_items(employees, page_number)
    return {
        "page_employees": page_employees,
        "current_search": search_query,
    }


def get_employee(employee_id):
    return unwrap_repository_result(employee_repository.get_by_id(employee_id))


def save_employee(employee):
    return unwrap_repository_result(employee_repository.save(employee))


def delete_employee(employee_id):
    employee = get_employee(employee_id)
    unwrap_repository_result(employee_repository.delete(employee))


def toggle_employee_status(employee_id):
    employee = get_employee(employee_id)
    return unwrap_repository_result(
        employee_repository.toggle_active_status(employee)
    )


def prepare_new_employee(employee, password):
    employee.set_password(password)
    return employee


def prepare_employee_update(employee, new_password):
    if new_password:
        employee.set_password(new_password)
    return employee


def get_employee_detail_context(*, employee, form, search_query="", page_number=""):
    address_context = get_address_section_context(employee, "employee")
    return {
        "form": form,
        "employee": employee,
        "current_search": search_query,
        "current_page": page_number,
        **address_context,
    }
