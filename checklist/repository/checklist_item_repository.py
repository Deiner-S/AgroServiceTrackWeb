from django.db.models import Q

from checklist.models import ChecklistItem
from checklist.repository.base_repository import BaseRepository
from checklist.repository.exception_handler import handle_repository_exceptions


class ChecklistItemRepository(BaseRepository):
    model = ChecklistItem

    @handle_repository_exceptions
    def list_for_api_sync(self):
        return self.get_queryset().all()

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


checklist_item_repository = ChecklistItemRepository()
