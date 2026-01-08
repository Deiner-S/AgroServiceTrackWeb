from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def os_pending(request):
    data = [
        {
            "operation_code": 1001,
            "client": "Fazenda Santa Rita",
            "symptoms": "Motor não liga",
            "chassi": "ABC123456789",
            "model": "Trator X100",
            "date_in": "2026-01-08",
            "status": "PENDENTE",
            "service": "Manutenção Preventiva",
            "insert_date": "2026-01-07T15:30:00"
        },
        {
            "operation_code": 1002,
            "client": "Agro Vale",
            "symptoms": "Vazamento de óleo",
            # campos opcionais não incluídos
            "status": "EM ANDAMENTO",
            "insert_date": "2026-01-07T16:00:00"
        }
    ]

    return Response(data, status=status.HTTP_200_OK)
