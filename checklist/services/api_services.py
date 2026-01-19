from checklist.models import WorkOrder
from checklist.models import *

def get_pending_work_order():
    items = WorkOrder.objects.all()
    for item in items:
        client = Client.objects.get(id=item.client.id)
        if item.status !=  "4":
            data = [
                {
                "operation_code" : item.operation_code,
                "symptoms" : item.symptoms,
                "client" : client.name,
                "status" : item.status,
                "insert_date" :item.insert_date,
                }            
            ]
    return data

def get_checklist_items():
    items = ChecklistItem.objects.all()
    data = [
        {
            "name": item.name,
            "status": item.status,        
        }
        for item in items
    ]
    return data