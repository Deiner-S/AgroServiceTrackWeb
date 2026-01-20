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
def save_work_orders_filleds(work_orders):    
    for work_order in work_orders:
        WorkOrder.objects.filter(operation_code=work_order.get("operation_code")).update(
                            operation_code=work_order.get("operation_code"),
                            client=work_order.get('client'),
                            symptoms=work_order.get('symptoms'),
                            chassi=work_order.get('chassi'),
                            orimento=work_order.get('orimento'),
                            model=work_order.get('model'),
                            date_in=work_order.get('date_in'),
                            date_out=work_order.get('date_out'),
                            status=work_order.get('status'),
                            service=work_order.get('service'),
                            )

def save_checklists_filleds(checklists):
    for checklist in checklists:
        Checklist.objects.create()