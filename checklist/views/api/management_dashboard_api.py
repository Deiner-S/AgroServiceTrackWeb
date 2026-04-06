from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from checklist.services import api_services
from checklist.throttling import SyncReadRateThrottle
from checklist.views.api.common import system_error_response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_dashboard_api(request):
    try:
        return Response(api_services.get_mobile_dashboard(request.user), status=status.HTTP_200_OK)
    except Exception as error:
        return system_error_response(error, request)
