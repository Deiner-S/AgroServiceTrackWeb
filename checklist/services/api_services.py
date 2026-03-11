from checklist.models import *
from checklist.utils.data_processing import prepare_image
import uuid

def get_pending_work_order():
    """Retorna ordens com status 1 (Pendente), 2 (Andamento) ou 3 (Entrega),
    com todos os campos que o app precisa para salvar a OS localmente."""
    items = WorkOrder.objects.filter(status__in=["1", "2", "3"]).select_related("client")
    data = []
    for item in items:
        data.append({
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
        })
    return data




def get_checklist_items():
    items = ChecklistItem.objects.all()
    data = [
        {
            "id":item.id,
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
            filename_prefix="signature_in"
        )
        signature_out_processed = prepare_image(
            work_order.get("signature_out"),
            filename_prefix="signature_out"
        )
            

        try:
            wo = WorkOrder.objects.get(
                operation_code=work_order.get("operation_code")
            )
        except WorkOrder.DoesNotExist:
            print(f"WorkOrder not found for operation_code={work_order.get('operation_code')!r}")
            # Propaga o erro para que a API retorne ok: false
            raise

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

        wo.save()
        print("save_work_orders_filleds [FINISHED]")
         


def save_checklists_filleds(checklists, employee_id):
    employee = Employee.objects.get(id=employee_id)

    for data in checklists:
        data_img = data.get("img")
        item_uuid_str = data.get("checklist_item_fk")
        operation_code = data.get("work_order_fk")
        checklist_uuid_str = data.get("id")

        image_file = prepare_image(data_img, filename_prefix="checklist")
         
        checklist_uuid = uuid.UUID(checklist_uuid_str)
        item_uuid = uuid.UUID(item_uuid_str)

        try:
            checklist_item = ChecklistItem.objects.get(id=item_uuid)
        except ChecklistItem.DoesNotExist:
            print(f"ChecklistItem not found for id={item_uuid_str!r}")
            # Propaga o erro para que a API retorne ok: false
            raise

        try:
            work_order = WorkOrder.objects.get(operation_code=operation_code)
        except WorkOrder.DoesNotExist:
            print(f"WorkOrder not found for operation_code={operation_code!r}")
            # Propaga o erro para que a API retorne ok: false
            raise

        Checklist.objects.create(
            id=checklist_uuid,
            work_order_fk=work_order,
            checklist_item_fk=checklist_item,
            employee=employee,
            status=data.get("status"),
            type=data.get("type"),
            image=image_file
        )

    print("save_checklists_filleds [FINISHED]")


