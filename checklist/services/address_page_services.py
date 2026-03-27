from checklist.exception_handler import unwrap_repository_result
from checklist.repository import address_repository, client_repository, employee_repository


def get_address_section_context(entity, entity_kind, *, form=None, show_form=False):
    addresses = unwrap_repository_result(address_repository.list_for_entity(entity))

    if entity_kind == "client":
        add_url_name = "add-client-address"
        delete_url_name = "delete-client-address"
        section_id = f"client-addresses-{entity.id}"
    else:
        add_url_name = "add-employee-address"
        delete_url_name = "delete-employee-address"
        section_id = f"employee-addresses-{entity.id}"

    return {
        "entity": entity,
        "entity_kind": entity_kind,
        "addresses": addresses,
        "address_form": form,
        "show_address_form": show_form,
        "address_add_url_name": add_url_name,
        "address_delete_url_name": delete_url_name,
        "address_section_id": section_id,
    }


def get_client(client_id):
    return unwrap_repository_result(client_repository.get_by_id(client_id))


def get_employee(employee_id):
    return unwrap_repository_result(employee_repository.get_by_id(employee_id))


def get_address(address_id):
    return unwrap_repository_result(address_repository.get_by_id(address_id))


def create_address_for_client(client, address):
    saved_address = unwrap_repository_result(address_repository.save(address))
    unwrap_repository_result(address_repository.add_to_client(client, saved_address))
    return saved_address


def delete_address_from_client(client, address):
    unwrap_repository_result(address_repository.remove_from_client(client, address))
    unwrap_repository_result(address_repository.delete_if_orphan(address))


def create_address_for_employee(employee, address):
    saved_address = unwrap_repository_result(address_repository.save(address))
    unwrap_repository_result(address_repository.add_to_employee(employee, saved_address))
    return saved_address


def delete_address_from_employee(employee, address):
    unwrap_repository_result(address_repository.remove_from_employee(employee, address))
    unwrap_repository_result(address_repository.delete_if_orphan(address))
