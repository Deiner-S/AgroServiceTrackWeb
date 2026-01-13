from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from checklist.models import WorkOrder, Client

@api_view(['GET'])
def pending_work_order(request):
    items = WorkOrder.objects.all()

    for item in items:
        client = Client.objects.get(id=item.client.id)
        data = [
            {
            "operation_code" : item.operation_code,
            "symptoms" : item.symptoms,
            "client" : client.name,
            "status" : item.status,
            "insert_date" :item.insert_date,
            }            
        ]
    

    return Response(data, status=status.HTTP_200_OK)
