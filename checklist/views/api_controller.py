from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from checklist.services import api_services
import json

@api_view(['GET'])
def send_pending_work_order(request):
    data = api_services.get_pending_work_order()
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def send_checklist_items(request):
    data = api_services.get_checklist_items()
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def receive_work_orders_api(request):
    if request.method == "POST":
        data = json.loads(request.body) 
        print(data)
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def receive_checkLists_filleds(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)

    return Response(status=status.HTTP_200_OK)