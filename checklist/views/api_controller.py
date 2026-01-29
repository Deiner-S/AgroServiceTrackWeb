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
    work_order_list = request.data
    user = request.user.id
     
    for data in work_order_list:
        img = data.get('signature')

        print("\n\n\n\n========================================================")
        try:
            if img:
                print("signature recebida")
                print(data.keys())
                print("Tipo:", type(img))            
                print("Tamanho (bytes):", len(img))
                
            else:
                print("signature, não recebida")
                print(data.keys())
                print(img)
        except TypeError:
            print("Tamanho: não foi possível calcular")

        print({
            "user":user,
            "operation_code":data.get("operation_code"),
            "chassi":data.get('chassi'),
            "orimento":data.get('orimento'),
            "model":data.get('model'),
            "date_in":data.get('date_in'),
            "date_out":data.get('date_out'),
            "status":data.get('status'),
            "service":data.get('service'),
        })
    print("\n\nTentando salvar work_orders")
    api_services.save_work_orders_filleds(work_order_list)
    return Response({"ok": True}, status=status.HTTP_200_OK)

@api_view(['POST'])
def receive_checkLists_filleds(request):
    checklists = request.data
    user = request.user.id
    
    for data in checklists:
        img = data.get('img')

        print("\n\n\n\n========================================================")
        try:
            if img:
                print("Imagem recebida")
                print(data.keys())
                print("Tipo:", type(img))            
                print("Tamanho (bytes):", len(img))
                
            else:
                print("Imagem, não recebida")
                print(data.keys())
                print(img)
        except TypeError:
            print("Tamanho: não foi possível calcular")

        print({
            "user":user,
            "checklist": data.get("checklist_item_fk"),
            "serviceOrder": data.get("work_order_fk"),
            "status": data.get("status"),
        })

        print("\n\nTentando salvar checklists")
        api_services.save_checklists_filleds(checklists,user)
    return Response({"ok": True}, status=status.HTTP_200_OK)