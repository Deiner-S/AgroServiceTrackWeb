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
    print("\n\n\n\n========================================================")
    data = request.data
    print(data)
    return Response({"ok": True}, status=status.HTTP_200_OK)

@api_view(['POST'])
def receive_checkLists_filleds(request):
    data_list = request.data
    for data in data_list:
        img = data.get('img')

        print("\n\n\n\n========================================================")
        try:
            if img:
                print("Imagem recebida")
                print("Tipo:", type(img))            
                print("Tamanho (bytes):", len(img))
            else:
                print("Imagem, não recebida")
                print(data.keys())
                print(img)
        except TypeError:
            print("Tamanho: não foi possível calcular")

        print({
            "checklist": data.get("checklist_item_fk"),
            "serviceOrder": data.get("work_order_fk"),
            "status": data.get("status"),
        })
    return Response({"ok": True}, status=status.HTTP_200_OK)