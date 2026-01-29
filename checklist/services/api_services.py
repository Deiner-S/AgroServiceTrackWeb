from checklist.models import *
from checklist.utils.data_processing import prepare_image
import uuid

def get_pending_work_order():
    items = WorkOrder.objects.all()
    data = []
    for item in items:
        client = Client.objects.get(id=item.client.id)
        if item.status !=  "4":
            data.append(
                {
                "operation_code" : item.operation_code,
                "symptoms" : item.symptoms,
                "client" : client.name,
                "status" : item.status,
                "insert_date" :item.insert_date,
                })
        print(data)   
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
        signature_processed = prepare_image(work_order.get("signature"),filename_prefix="signature")
            

        try:
            wo = WorkOrder.objects.get(
                operation_code=work_order.get("operation_code")
            )
        except WorkOrder.DoesNotExist:
            continue  # ou loga erro

        wo.chassi = work_order.get("chassi")
        wo.orimento = work_order.get("orimento")
        wo.model = work_order.get("model")
        wo.date_in = work_order.get("date_in")
        wo.date_out = work_order.get("date_out")
        wo.status = work_order.get("status")
        wo.service = work_order.get("service")

        if signature_processed:
            wo.signature = signature_processed

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
 
        checklist_item = ChecklistItem.objects.get(id=item_uuid)  
        work_order = WorkOrder.objects.get(operation_code=operation_code)
 
        Checklist.objects.create(
            id=checklist_uuid,
            work_order_fk=work_order,
            checklist_item_fk=checklist_item,
            employee=employee,
            status=data.get("status"),
            image=image_file
        )

    print("save_checklists_filleds [FINISHED]")


