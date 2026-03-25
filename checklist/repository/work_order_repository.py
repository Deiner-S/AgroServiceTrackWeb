from django.db.models import Max, Q

from checklist.models import WorkOrder
from checklist.repository.base_repository import BaseRepository
from checklist.repository.exception_handler import handle_repository_exceptions


class WorkOrderRepository(BaseRepository):
    model = WorkOrder

    @handle_repository_exceptions
    def list_pending_for_api_sync(self):
        return (
            self.get_queryset()
            .filter(status__in=["1", "2", "3"])
            .select_related("client")
        )

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

    @handle_repository_exceptions
    def get_by_operation_code(self, operation_code):
        return self.get_queryset().get(operation_code=operation_code)


work_order_repository = WorkOrderRepository()
