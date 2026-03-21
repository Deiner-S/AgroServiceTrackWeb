import uuid

from checklist.models import Checklist
from checklist.repository import (
    checklist_item_repository,
    checklist_repository,
    employee_repository,
    work_order_repository,
)
from checklist.repository.exception_handler import unwrap_repository_result
from checklist.utils.data_processing import prepare_image


def get_pending_work_order():
    """Retorna ordens com status 1, 2 ou 3 para sincronizacao do app."""
    items = unwrap_repository_result(work_order_repository.list_pending_for_api_sync())
    data = []

    for item in items:
        data.append(
            {
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
        signature_in_processed = prepare_image(
            work_order.get("signature_in") or work_order.get("signature"),
            filename_prefix="signature_in",
        )
        signature_out_processed = prepare_image(
            work_order.get("signature_out"),
            filename_prefix="signature_out",
        )

        wo = unwrap_repository_result(
            work_order_repository.get_by_operation_code(work_order.get("operation_code"))
        )

        wo.chassi = work_order.get("chassi")
        wo.horimetro = work_order.get("horimetro")
        wo.model = work_order.get("model")
        wo.date_in = work_order.get("date_in")
        wo.date_out = work_order.get("date_out")
        wo.status = work_order.get("status")
        wo.service = work_order.get("service")

        if signature_in_processed:
            wo.signature_in = signature_in_processed

        if signature_out_processed:
            wo.signature_out = signature_out_processed

        unwrap_repository_result(work_order_repository.save(wo))
        print("save_work_orders_filleds [FINISHED]")


def save_checklists_filleds(checklists, employee_id):
    employee = unwrap_repository_result(employee_repository.get_by_identifier(employee_id))

    for data in checklists:
        data_img_in = data.get("img_in")
        data_img_out = data.get("img_out")

        item_uuid_str = data.get("checklist_item_fk")
        operation_code = data.get("work_order_fk")
        checklist_uuid_str = data.get("id")

        image_file_in = prepare_image(data_img_in, filename_prefix="checklist_in")
        image_file_out = prepare_image(data_img_out, filename_prefix="checklist_out")

        checklist_uuid = uuid.UUID(checklist_uuid_str) if checklist_uuid_str else uuid.uuid4()
        item_uuid = uuid.UUID(item_uuid_str)

        checklist_item = unwrap_repository_result(checklist_item_repository.get_by_id(item_uuid))
        work_order = unwrap_repository_result(
            work_order_repository.get_by_operation_code(operation_code)
        )

        checklist_obj = unwrap_repository_result(
            checklist_repository.find_latest_by_work_order_and_item(work_order, checklist_item)
        )

        if checklist_obj is None:
            checklist_obj = Checklist(
                id=checklist_uuid,
                work_order_fk=work_order,
                checklist_item_fk=checklist_item,
            )

        checklist_obj.employee = employee
        checklist_obj.status = data.get("status") or checklist_obj.status

        if not checklist_obj.status:
            raise ValueError("Checklist status is required")

        if image_file_in:
            checklist_obj.image_in = image_file_in

        if image_file_out:
            checklist_obj.image_out = image_file_out

        unwrap_repository_result(checklist_repository.save(checklist_obj))

    print("save_checklists_filleds [FINISHED]")
