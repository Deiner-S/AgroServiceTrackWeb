from types import SimpleNamespace

from checklist.models import STATUS_CHOICES_POSITION
from checklist.permissions import (
    ADMINISTRATIVE,
    DIRECTOR,
    MANAGER,
    TECHNICIAN,
    can_assign_employee_position,
    can_create_employee,
    can_manage_checklist_item,
    can_toggle_employee_status,
    can_view_checklist_item_module,
    can_view_client_detail,
    can_view_client_list,
    can_view_employee_module,
    get_access_context,
    get_allowed_employee_positions,
    get_user_position,
)


def make_user(*, authenticated=True, position=None):
    return SimpleNamespace(is_authenticated=authenticated, position=position)


def test_get_user_position_returns_none_for_anonymous_user():
    assert get_user_position(make_user(authenticated=False, position=DIRECTOR)) is None


def test_employee_module_access_by_role():
    assert can_view_employee_module(make_user(position=DIRECTOR)) is True
    assert can_view_employee_module(make_user(position=MANAGER)) is True
    assert can_view_employee_module(make_user(position=ADMINISTRATIVE)) is True
    assert can_view_employee_module(make_user(position=TECHNICIAN)) is False


def test_assign_employee_position_rules():
    assert can_assign_employee_position(make_user(position=DIRECTOR), DIRECTOR) is True
    assert can_assign_employee_position(make_user(position=MANAGER), ADMINISTRATIVE) is True
    assert can_assign_employee_position(make_user(position=MANAGER), DIRECTOR) is False
    assert can_assign_employee_position(make_user(position=TECHNICIAN), ADMINISTRATIVE) is False


def test_get_allowed_employee_positions_respects_role():
    assert get_allowed_employee_positions(make_user(position=DIRECTOR)) == STATUS_CHOICES_POSITION
    assert get_allowed_employee_positions(make_user(position=MANAGER)) == [
        choice for choice in STATUS_CHOICES_POSITION if choice[0] in {ADMINISTRATIVE, TECHNICIAN}
    ]
    assert get_allowed_employee_positions(make_user(position=TECHNICIAN)) == []


def test_client_permissions_block_technician_detail_access():
    technician = make_user(position=TECHNICIAN)

    assert can_view_client_list(technician) is True
    assert can_view_client_detail(technician) is False


def test_toggle_employee_status_uses_edit_permission_rules():
    manager = make_user(position=MANAGER)
    manageable_employee = SimpleNamespace(position=ADMINISTRATIVE)
    blocked_employee = SimpleNamespace(position=DIRECTOR)

    assert can_toggle_employee_status(manager, manageable_employee) is True
    assert can_toggle_employee_status(manager, blocked_employee) is False


def test_checklist_permissions_and_access_context():
    manager = make_user(position=MANAGER)
    administrative = make_user(position=ADMINISTRATIVE)

    assert can_create_employee(manager) is True
    assert can_view_checklist_item_module(manager) is True
    assert can_manage_checklist_item(manager) is True
    assert can_view_checklist_item_module(administrative) is False

    context = get_access_context(manager)

    assert context["is_manager"] is True
    assert context["can_view_employee_module"] is True
    assert context["can_manage_checklist_item"] is True
