from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from checklist.models import ChecklistItem

@api_view(['GET'])
def dowload_checklist_items(request):

    items = ChecklistItem.objects.all()
    data = [
    {
        "name": item.name,
        "status": item.status,        
    }
    for item in items
    ]

    return Response(data, status=status.HTTP_200_OK)
