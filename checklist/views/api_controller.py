from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, throttle_classes
from rest_framework import status
from rest_framework.response import Response

from checklist.api_payload_validation import (
    validate_checklist_entries,
    validate_work_order_entries,
)
from checklist.exception_handler import get_validation_error_message
from checklist.throttling import SyncReadRateThrottle, SyncWriteRateThrottle
from checklist.services import api_services
from checklist.utils.logging_utils import save_log
import traceback


@api_view(['GET'])
@throttle_classes([SyncReadRateThrottle])
def send_pending_work_order(request):
    try:
        print("\n\nTry get pending_work_order")
        data = api_services.get_pending_work_order()
    except Exception as e:
        print("\n\nFailed to get pending_work_order")
        save_log(e, request)
        data = None
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@throttle_classes([SyncReadRateThrottle])
def send_checklist_items(request):
    try:
        print("\n\nTry get checklist_items")
        data = api_services.get_checklist_items()
    except Exception as e:
        print("\n\nFailed to get checklist_items")
        save_log(e, request)
        data = None
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@throttle_classes([SyncWriteRateThrottle])
def receive_work_orders_api(request):
    try:
        print("\n\nTry save work_orders")
        validated_work_orders = validate_work_order_entries(request.data)
        api_services.save_work_orders_filleds(validated_work_orders)        
        response = True
    except ValidationError as e:
        save_log(e, request)
        response = False
        return Response(
            {"ok": response, "error": get_validation_error_message(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        save_log(e, request)
        response = False
        print("\n\nFailed to save work_orders:", repr(e))
        traceback.print_exc()

    return Response({"ok": response}, status=status.HTTP_200_OK)




@api_view(['POST'])
@throttle_classes([SyncWriteRateThrottle])
def receive_checkLists_filleds(request):
    user = request.user.id
    
    try:
        print("\n\nTry save checklists")
        validated_checklists = validate_checklist_entries(request.data)
        api_services.save_checklists_filleds(validated_checklists, user)
        response = True
    except ValidationError as e:
        save_log(e, request)
        response = False
        return Response(
            {"ok": response, "error": get_validation_error_message(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        save_log(e, request)
        response = False
        print("\n\nFailed to save checklist:", repr(e))
        traceback.print_exc()

    return Response({"ok": response}, status=status.HTTP_200_OK)
