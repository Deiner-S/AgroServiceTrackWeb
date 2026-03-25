from checklist.models import Address
from checklist.repository.base_repository import BaseRepository
from checklist.exception_handler import handle_repository_exceptions


class AddressRepository(BaseRepository):
    model = Address

    @handle_repository_exceptions
    def list_for_entity(self, entity):
        return entity.addresses.all().order_by("-created_at")

    @handle_repository_exceptions
    def add_to_client(self, client, address):
        client.addresses.add(address)

    @handle_repository_exceptions
    def remove_from_client(self, client, address):
        client.addresses.remove(address)

    @handle_repository_exceptions
    def add_to_employee(self, employee, address):
        employee.addresses.add(address)

    @handle_repository_exceptions
    def remove_from_employee(self, employee, address):
        employee.addresses.remove(address)

    @handle_repository_exceptions
    def delete_if_orphan(self, address):
        if not address.clients.exists() and not address.employees.exists():
            address.delete()


address_repository = AddressRepository()
