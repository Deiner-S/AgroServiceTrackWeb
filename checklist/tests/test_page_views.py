from types import SimpleNamespace
from unittest.mock import Mock

from django.test import RequestFactory

from checklist.exception_handler import RepositoryOperationError
from checklist.views.pages.address_pages import (
    add_client_address,
    add_employee_address,
    delete_client_address,
)
from checklist.views.pages.checklist_item_pages import (
    checklist_item_detail,
    checklist_item_list,
    toggle_checklist_item_status,
)
from checklist.views.pages.client_pages import add_cliente, client_detail, client_list, delete_client
from checklist.views.pages.employe_pages import add_employee, delete_employee, employee_detail, employee_list, toggle_employee_status
from checklist.views.pages.service_order_pages import add_order, open_client_order, service_order_detail, service_panel


def make_user(position="0", *, authenticated=True):
    return SimpleNamespace(is_authenticated=authenticated, position=position)


def test_client_list_renders_for_authorized_user(monkeypatch):
    request = RequestFactory().get("/gerenciador/clients/")
    request.user = make_user("1")
    render_mock = Mock(return_value="client-list-response")
    monkeypatch.setattr("checklist.views.pages.client_pages.render_page", render_mock)
    monkeypatch.setattr(
        "checklist.views.pages.client_pages.client_page_services.get_client_list_context",
        lambda **kwargs: {"page_client": [], "current_search": ""},
    )

    response = client_list(request)

    assert response == "client-list-response"


def test_client_list_returns_forbidden_when_user_has_no_access():
    request = RequestFactory().get("/gerenciador/clients/")
    request.user = make_user(None)

    response = client_list(request)

    assert response.status_code == 403


def test_add_cliente_get_renders_empty_form(monkeypatch):
    request = RequestFactory().get("/gerenciador/client/")
    request.user = make_user("0")
    form_instance = object()
    monkeypatch.setattr("checklist.views.pages.client_pages.ClientForm", lambda *args, **kwargs: form_instance)
    render_mock = Mock(return_value="client-form-response")
    monkeypatch.setattr("checklist.views.pages.client_pages.render_page", render_mock)

    response = add_cliente(request)

    assert response == "client-form-response"
    assert render_mock.call_args.args[2]["form"] is form_instance


def test_client_detail_post_forbidden_for_non_manager(monkeypatch):
    request = RequestFactory().post("/gerenciador/clients/id/detail/", data={})
    request.user = make_user("3")

    response = client_detail(request, "client-id")

    assert response.status_code == 403


def test_delete_client_requires_hx_and_post():
    request = RequestFactory().get("/gerenciador/clients/id/delete/")
    request.user = make_user("0")

    response = delete_client(request, "client-id")

    assert response.status_code == 400


def test_delete_client_handles_repository_error(monkeypatch):
    request = RequestFactory().post("/gerenciador/clients/id/delete/", HTTP_HX_REQUEST="true")
    request.user = make_user("0")
    render_repo_mock = Mock(return_value="repo-error")
    monkeypatch.setattr(
        "checklist.views.pages.client_pages.client_page_services.delete_client",
        Mock(side_effect=RepositoryOperationError("boom", 400)),
    )
    monkeypatch.setattr("checklist.views.pages.client_pages.render_repository_error", render_repo_mock)

    response = delete_client(request, "client-id")

    assert response == "repo-error"


def test_service_panel_renders_context(monkeypatch):
    request = RequestFactory().get("/gerenciador/panel/?status=2&search=teste")
    request.user = make_user("1")
    render_mock = Mock(return_value="panel-response")
    monkeypatch.setattr("checklist.views.pages.service_order_pages.render_page", render_mock)
    monkeypatch.setattr(
        "checklist.views.pages.service_order_pages.service_order_page_services.get_service_panel_context",
        lambda **kwargs: {"orders": [], "selected_status": kwargs["status_filter"], "current_search": kwargs["search_query"]},
    )

    response = service_panel(request)

    assert response == "panel-response"


def test_service_order_detail_handles_repository_error(monkeypatch):
    request = RequestFactory().get("/gerenciador/panel/id/detail/")
    request.user = make_user("0")
    monkeypatch.setattr(
        "checklist.views.pages.service_order_pages.service_order_page_services.get_service_order_detail_context",
        Mock(side_effect=RepositoryOperationError("boom", 400)),
    )
    render_repo_mock = Mock(return_value="repo-error")
    monkeypatch.setattr("checklist.views.pages.service_order_pages.render_repository_error", render_repo_mock)

    response = service_order_detail(request, "order-id")

    assert response == "repo-error"


def test_add_order_post_saves_and_returns_client_detail(monkeypatch):
    request = RequestFactory().post("/gerenciador/clients/id/services/add_service", data={})
    request.user = make_user("0")
    client = SimpleNamespace(id="client-id")
    valid_form = Mock()
    valid_form.is_valid.return_value = True
    valid_form.save.return_value = SimpleNamespace()
    client_form = object()
    monkeypatch.setattr("checklist.views.pages.service_order_pages.DataSheetCreateForm", lambda *args, **kwargs: valid_form)
    monkeypatch.setattr("checklist.views.pages.service_order_pages.ClientDetailForm", lambda *args, **kwargs: client_form)
    monkeypatch.setattr("checklist.views.pages.service_order_pages.client_page_services.get_client", lambda client_id: client)
    monkeypatch.setattr("checklist.views.pages.service_order_pages.service_order_page_services.create_order_for_client", lambda current_client, order: None)
    monkeypatch.setattr("checklist.views.pages.service_order_pages._render_client_detail", lambda request, client, form: "detail-response")

    response = add_order(request, "client-id")

    assert response == "detail-response"


def test_open_client_order_returns_forbidden_for_technician():
    request = RequestFactory().get("/gerenciador/clients/id/services/")
    request.user = make_user("3")

    response = open_client_order(request, "client-id")

    assert response.status_code == 403


def test_checklist_item_list_renders_for_manager(monkeypatch):
    request = RequestFactory().get("/gerenciador/checklist-items/")
    request.user = make_user("1")
    monkeypatch.setattr(
        "checklist.views.pages.checklist_item_pages.checklist_item_page_services.get_checklist_item_list_context",
        lambda **kwargs: {"items": []},
    )
    render_mock = Mock(return_value="checklist-list")
    monkeypatch.setattr("checklist.views.pages.checklist_item_pages.render_page", render_mock)

    response = checklist_item_list(request)

    assert response == "checklist-list"


def test_checklist_item_detail_post_forbidden_for_administrative():
    request = RequestFactory().post("/gerenciador/checklist-items/id/detail/", data={})
    request.user = make_user("2")

    response = checklist_item_detail(request, "item-id")

    assert response.status_code == 403


def test_toggle_checklist_item_status_requires_hx():
    request = RequestFactory().post("/gerenciador/checklist-items/id/toggle-status/")
    request.user = make_user("1")

    response = toggle_checklist_item_status(request, "item-id")

    assert response.status_code == 400


def test_employee_list_forbidden_for_technician():
    request = RequestFactory().get("/gerenciador/employees/")
    request.user = make_user("3")

    response = employee_list(request)

    assert response.status_code == 403


def test_add_employee_get_renders_form(monkeypatch):
    request = RequestFactory().get("/gerenciador/employee/")
    request.user = make_user("0")
    form_instance = object()
    monkeypatch.setattr("checklist.views.pages.employe_pages.EmployeeForm", lambda *args, **kwargs: form_instance)
    render_mock = Mock(return_value="employee-form")
    monkeypatch.setattr("checklist.views.pages.employe_pages.render_page", render_mock)

    response = add_employee(request)

    assert response == "employee-form"
    assert render_mock.call_args.args[2]["form"] is form_instance


def test_employee_detail_post_forbidden_when_target_not_editable(monkeypatch):
    request = RequestFactory().post("/gerenciador/employees/id/detail/", data={})
    request.user = make_user("1")
    target = SimpleNamespace(position="0")
    monkeypatch.setattr("checklist.views.pages.employe_pages.employee_page_services.get_employee", lambda employee_id: target)

    response = employee_detail(request, "employee-id")

    assert response.status_code == 403


def test_delete_employee_requires_post_and_hx():
    request = RequestFactory().get("/gerenciador/employees/id/delete/")
    request.user = make_user("0")

    response = delete_employee(request, "employee-id")

    assert response.status_code == 400


def test_toggle_employee_status_renders_detail_after_service(monkeypatch):
    request = RequestFactory().post("/gerenciador/employees/id/toggle-status/", HTTP_HX_REQUEST="true")
    request.user = make_user("0")
    current_employee = SimpleNamespace(position="2")
    updated_employee = SimpleNamespace(position="2")
    monkeypatch.setattr("checklist.views.pages.employe_pages.employee_page_services.get_employee", lambda employee_id: current_employee)
    monkeypatch.setattr("checklist.views.pages.employe_pages.employee_page_services.toggle_employee_status", lambda employee_id: updated_employee)
    monkeypatch.setattr("checklist.views.pages.employe_pages.EmployeeDetailForm", lambda *args, **kwargs: "form")
    monkeypatch.setattr("checklist.views.pages.employe_pages._render_employee_detail", lambda request, employee, form: "employee-detail")

    response = toggle_employee_status(request, "employee-id")

    assert response == "employee-detail"


def test_add_client_address_get_respects_cancel(monkeypatch):
    request = RequestFactory().get("/gerenciador/clients/id/addresses/add/?cancel=true", HTTP_HX_REQUEST="true")
    request.user = make_user("0")
    client = SimpleNamespace(id="client-id")
    monkeypatch.setattr("checklist.views.pages.address_pages.address_page_services.get_client", lambda client_id: client)
    monkeypatch.setattr("checklist.views.pages.address_pages._render_address_section_response", lambda request, entity, entity_kind, **kwargs: kwargs["show_form"])

    response = add_client_address(request, "client-id")

    assert response is False


def test_add_employee_address_invalid_method_returns_bad_request(monkeypatch):
    request = RequestFactory().put("/gerenciador/employees/id/addresses/add/", HTTP_HX_REQUEST="true")
    request.user = make_user("0")
    employee = SimpleNamespace(id="employee-id", position="2")
    monkeypatch.setattr("checklist.views.pages.address_pages.address_page_services.get_employee", lambda employee_id: employee)

    response = add_employee_address(request, "employee-id")

    assert response.status_code == 400


def test_delete_client_address_forbidden_when_user_cannot_manage(monkeypatch):
    request = RequestFactory().post("/gerenciador/clients/id/addresses/address/delete/", HTTP_HX_REQUEST="true")
    request.user = make_user("3")
    client = SimpleNamespace(id="client-id")
    monkeypatch.setattr("checklist.views.pages.address_pages.address_page_services.get_client", lambda client_id: client)

    response = delete_client_address(request, "client-id", "address-id")

    assert response.status_code == 403
