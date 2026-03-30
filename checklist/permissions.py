from checklist.models import STATUS_CHOICES_POSITION

DIRECTOR = "0"
MANAGER = "1"
ADMINISTRATIVE = "2"
TECHNICIAN = "3"

MANAGEABLE_BY_MANAGER = {ADMINISTRATIVE, TECHNICIAN}


def get_user_position(user):
    if not getattr(user, "is_authenticated", False):
        return None
    return getattr(user, "position", None)


def is_director(user):
    return get_user_position(user) == DIRECTOR


def is_manager(user):
    return get_user_position(user) == MANAGER


def is_administrative(user):
    return get_user_position(user) == ADMINISTRATIVE


def is_technician(user):
    return get_user_position(user) == TECHNICIAN


def can_view_employee_module(user):
    return is_director(user) or is_manager(user) or is_administrative(user)


def can_create_employee(user):
    return is_director(user) or is_manager(user)


def can_assign_employee_position(user, position):
    if is_director(user):
        return True
    if is_manager(user):
        return position in MANAGEABLE_BY_MANAGER
    return False


def get_allowed_employee_positions(user):
    if is_director(user):
        return STATUS_CHOICES_POSITION
    if is_manager(user):
        return [
            choice
            for choice in STATUS_CHOICES_POSITION
            if choice[0] in MANAGEABLE_BY_MANAGER
        ]
    return []


def can_edit_employee(user, employee):
    if is_director(user):
        return True
    if is_manager(user):
        return employee.position in MANAGEABLE_BY_MANAGER
    return False


def can_toggle_employee_status(user, employee):
    return can_edit_employee(user, employee)


def can_manage_employee_addresses(user, employee):
    return can_edit_employee(user, employee)


def can_view_client_list(user):
    return any(
        (
            is_director(user),
            is_manager(user),
            is_administrative(user),
            is_technician(user),
        )
    )


def can_view_client_detail(user):
    return can_view_client_list(user) and not is_technician(user)


def can_manage_client(user):
    return can_view_client_detail(user)


def can_manage_client_addresses(user):
    return can_manage_client(user)


def can_create_service_order(user):
    return can_manage_client(user)


def can_view_checklist_item_module(user):
    return is_director(user) or is_manager(user)


def can_manage_checklist_item(user):
    return can_view_checklist_item_module(user)


def can_view_service_panel(user):
    return any(
        (
            is_director(user),
            is_manager(user),
            is_administrative(user),
            is_technician(user),
        )
    )


def get_access_context(user):
    return {
        "is_director": is_director(user),
        "is_manager": is_manager(user),
        "is_administrative": is_administrative(user),
        "is_technician": is_technician(user),
        "can_view_employee_module": can_view_employee_module(user),
        "can_create_employee": can_create_employee(user),
        "can_view_client_list": can_view_client_list(user),
        "can_view_client_detail": can_view_client_detail(user),
        "can_manage_client": can_manage_client(user),
        "can_create_service_order": can_create_service_order(user),
        "can_view_checklist_item_module": can_view_checklist_item_module(user),
        "can_manage_checklist_item": can_manage_checklist_item(user),
        "can_view_service_panel": can_view_service_panel(user),
    }
