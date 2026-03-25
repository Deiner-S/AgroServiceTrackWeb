from django.db.models import Q

from checklist.models import Client
from checklist.repository.base_repository import BaseRepository
from checklist.repository.exception_handler import handle_repository_exceptions


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


client_repository = ClientRepository()
