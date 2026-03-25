from django.contrib.auth import get_user_model
from django.db.models import Q

from checklist.repository.base_repository import BaseRepository
from checklist.repository.exception_handler import handle_repository_exceptions


Employee = get_user_model()


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

    @handle_repository_exceptions
    def get_by_identifier(self, employee_id):
        return self.get_queryset().get(id=employee_id)


employee_repository = EmployeeRepository()
