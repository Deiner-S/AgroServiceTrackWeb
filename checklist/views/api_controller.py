from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from checklist.services import api_services


@api_view(['GET'])
def send_pending_work_order(request):
    try:
        print("\n\nTry get pending_work_order")
        data = api_services.get_pending_work_order()
    except Exception as e:
        print("\n\nFailed to get pending_work_order")
        #need to implement save_log(e)
        data = None
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def send_checklist_items(request):
    try:
        print("\n\nTry get checklist_items")
        data = api_services.get_checklist_items()
    except Exception as e:
        print("\n\nFailed to get checklist_items")
        #need to implement save_log(e)
        data = None
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def receive_work_orders_api(request):
    work_order_list = request.data
    user = request.user.id
     
    try:
        print("\n\nTry save work_orders")
        api_services.save_work_orders_filleds(work_order_list)        
        response = True
    except Exception as e:
        #need to implement save_log(e)
        response = False
        print("\n\nFailed to save checklist")

    return Response({"ok": response}, status=status.HTTP_200_OK)




@api_view(['POST'])
def receive_checkLists_filleds(request):
    checklists = request.data
    user = request.user.id
    
    try:
        print("\n\nTry save checklists")
        api_services.save_checklists_filleds(checklists,user)
        response = True
    except Exception as e:
        #need to implement save_log(e)
        response = False
        print("\n\nFailed to save checklist")

    return Response({"ok": response}, status=status.HTTP_200_OK)