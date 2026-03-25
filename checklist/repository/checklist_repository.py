from checklist.models import Checklist
from checklist.repository.base_repository import BaseRepository
from checklist.exception_handler import handle_repository_exceptions


class ChecklistRepository(BaseRepository):
    model = Checklist

    @handle_repository_exceptions
    def find_latest_by_work_order_and_item(self, work_order, checklist_item):
        return (
            self.get_queryset()
            .filter(work_order_fk=work_order, checklist_item_fk=checklist_item)
            .order_by("-insert_date")
            .first()
        )


checklist_repository = ChecklistRepository()
