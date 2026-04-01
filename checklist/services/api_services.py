from checklist.models import Checklist
from checklist.repository import (
    checklist_item_repository,
    checklist_repository,
    employee_repository,
    work_order_repository,
)
from checklist.exception_handler import unwrap_repository_result
from checklist.utils.data_processing import prepare_image
from checklist.utils.logging_utils import save_mobile_log


def get_pending_work_order():
    """Retorna ordens com status 1, 2 ou 3 para sincronizacao do app."""
    items = unwrap_repository_result(work_order_repository.list_pending_for_api_sync())
    data = []

    for item in items:
        data.append(
            {
                "id": item.id,
                "operation_code": item.operation_code,
                "symptoms": item.symptoms,
                "client": item.client.name,
                "status": item.status,
                "chassi": item.chassi,
                "horimetro": item.horimetro,
                "model": item.model,
                "date_in": item.date_in.isoformat() if item.date_in else None,
                "date_out": item.date_out.isoformat() if item.date_out else None,
                "service": item.service,
                "insertDate": item.insert_date.isoformat() if item.insert_date else None,
            }
        )

    return data


def get_checklist_items():
    items = unwrap_repository_result(checklist_item_repository.list_for_api_sync())
    data = [
        {
            "id": item.id,
            "name": item.name,
            "status": item.status,
        }
        for item in items
    ]
    print(data)
    return data


def save_work_orders_filleds(work_orders):
    for work_order in work_orders:
        wo = work_order["work_order"]

        wo.chassi = work_order["chassi"]
        wo.horimetro = work_order["horimetro"]
        wo.model = work_order["model"]
        wo.date_in = work_order["date_in"]
        wo.date_out = work_order["date_out"]
        wo.status = work_order["status"]
        wo.service = work_order["service"]

        if work_order["signature_in"]:
            wo.signature_in = work_order["signature_in"]

        if work_order["signature_out"]:
            wo.signature_out = work_order["signature_out"]

        unwrap_repository_result(work_order_repository.save(wo))
        print("save_work_orders_filleds [FINISHED]")


def save_checklists_filleds(checklists, employee_id):
    employee = unwrap_repository_result(employee_repository.get_by_identifier(employee_id))

    for data in checklists:
        checklist_obj = unwrap_repository_result(
            checklist_repository.find_latest_by_work_order_and_item(
                data["work_order"],
                data["checklist_item"],
            )
        )

        if checklist_obj is None:
            checklist_obj = Checklist(
                id=data["id"],
                work_order_fk=data["work_order"],
                checklist_item_fk=data["checklist_item"],
            )

        checklist_obj.employee = employee
        checklist_obj.status = data["status"] or checklist_obj.status

        if not checklist_obj.status:
            raise ValueError("Checklist status is required")

        if data["image_in"]:
            checklist_obj.image_in = data["image_in"]

        if data["image_out"]:
            checklist_obj.image_out = data["image_out"]

        unwrap_repository_result(checklist_repository.save(checklist_obj))

    print("save_checklists_filleds [FINISHED]")


def save_mobile_logs(log_entries, request=None):
    for log_entry in log_entries:
        save_mobile_log(log_entry, request=request)

    print("save_mobile_logs [FINISHED]")
