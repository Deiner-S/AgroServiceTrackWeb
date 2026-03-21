from django.contrib.auth import get_user_model
from django.db.models import Max, Q

from checklist.models import *
from checklist.repository.base_repository import BaseRepository
from checklist.repository.exception_handler import handle_repository_exceptions


Employee = get_user_model()


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


class ClientRepository(BaseRepository):
    model = Client

    @handle_repository_exceptions
    def list_for_management(self, query=""):
        queryset = self.get_queryset().order_by("name")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(email__icontains=query)
                | Q(cpf__icontains=query)
                | Q(cnpj__icontains=query)
                | Q(phone__icontains=query)
            )
        return queryset


class EmployeeRepository(BaseRepository):
    model = Employee

    @handle_repository_exceptions
    def list_for_management(self, query=""):
        queryset = self.get_queryset().order_by("first_name")
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
                | Q(cpf__icontains=query)
            )
        return queryset

    @handle_repository_exceptions
    def find_inactive_by_username(self, username):
        return self.get_queryset().filter(username=username, is_active=False).first()

    @handle_repository_exceptions
    def toggle_active_status(self, employee):
        employee.is_active = not employee.is_active
        employee.save(update_fields=["is_active"])
        return employee


class ClientAddressRepository(BaseRepository):
    model = ClientAddress


class EmployeeAddressRepository(BaseRepository):
    model = EmployeeAddress


class WorkOrderRepository(BaseRepository):
    model = WorkOrder

    @handle_repository_exceptions
    def list_by_client(self, client):
        return self.get_queryset().filter(client=client).order_by("-insert_date")

    @handle_repository_exceptions
    def get_next_operation_code(self):
        last_code = self.model.objects.aggregate(Max("operation_code"))["operation_code__max"]
        return "000001" if not last_code else f"{int(last_code) + 1:06d}"

    @handle_repository_exceptions
    def list_for_panel(self, *, status_filter="all", search_query=""):
        queryset = self.get_queryset().select_related("client").order_by("-insert_date")

        if status_filter != "all":
            queryset = queryset.filter(status=status_filter)

        if search_query:
            queryset = queryset.filter(
                Q(operation_code__icontains=search_query)
                | Q(client__name__icontains=search_query)
                | Q(symptoms__icontains=search_query)
                | Q(service__icontains=search_query)
                | Q(chassi__icontains=search_query)
                | Q(model__icontains=search_query)
                | Q(horimetro__icontains=search_query)
            )

        return queryset

    @handle_repository_exceptions
    def get_detail_by_id(self, order_id):
        queryset = self.get_queryset().select_related("client").prefetch_related(
            "checklists__employee",
            "checklists__checklist_item_fk",
        )
        return queryset.get(id=order_id)


class ChecklistItemRepository(BaseRepository):
    model = ChecklistItem

    @handle_repository_exceptions
    def list_for_management(self, query=""):
        queryset = self.get_queryset().order_by("name")
        if query:
            queryset = queryset.filter(Q(name__icontains=query))
        return queryset

    @handle_repository_exceptions
    def toggle_status(self, checklist_item):
        checklist_item.status = 0 if checklist_item.status == 1 else 1
        checklist_item.save(update_fields=["status"])
        return checklist_item


class ChecklistRepository(BaseRepository):
    model = Checklist


address_repository = AddressRepository()
client_repository = ClientRepository()
employee_repository = EmployeeRepository()
client_address_repository = ClientAddressRepository()
employee_address_repository = EmployeeAddressRepository()
work_order_repository = WorkOrderRepository()
checklist_item_repository = ChecklistItemRepository()
checklist_repository = ChecklistRepository()
