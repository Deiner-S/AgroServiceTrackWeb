from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from checklist.api_payload_validation import (
    validate_mobile_identifier,
    validate_mobile_payload_object,
    validate_mobile_search_query,
)
from checklist.exception_handler import RepositoryOperationError
from checklist.permissions import can_manage_checklist_item, can_view_checklist_item_module
from checklist.services import api_services
from checklist.throttling import SyncReadRateThrottle, SyncWriteRateThrottle
from checklist.views.api.common import (
    forbid_if,
    repository_error_response,
    system_error_response,
    validation_error_response,
)
from checklist.views.api.mobile_management_shared import (
    CHECKLIST_ITEM_ALLOWED_KEYS,
    ChecklistItemForm,
    raise_form_validation_error,
)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_checklist_items_api(request):
    try:
        if request.method == 'GET':
            forbid_if(not can_view_checklist_item_module(request.user), "Usuario sem permissao para consultar itens de checklist.")
            search_query = validate_mobile_search_query(request.query_params.get("search"))
            return Response(api_services.get_mobile_checklist_items(search_query), status=status.HTTP_200_OK)

        forbid_if(not can_manage_checklist_item(request.user), "Usuario sem permissao para cadastrar item de checklist.")
        payload = validate_mobile_payload_object(request.data, "checklist_item_payload", CHECKLIST_ITEM_ALLOWED_KEYS)
        form = ChecklistItemForm(payload)

        if not form.is_valid():
            raise_form_validation_error(form)

        checklist_item = api_services.create_mobile_checklist_item(form.save(commit=False))
        return Response(
            api_services.get_mobile_checklist_item_detail(str(checklist_item.id), request.user),
            status=status.HTTP_201_CREATED,
        )
    except ValidationError as error:
        return validation_error_response(error, request)
    except RepositoryOperationError as error:
        return repository_error_response(error, request)
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_checklist_item_detail_api(request, item_id):
    try:
        validated_item_id = validate_mobile_identifier(item_id, "item_id")

        if request.method == 'GET':
            forbid_if(not can_view_checklist_item_module(request.user), "Usuario sem permissao para consultar item de checklist.")
            return Response(
                api_services.get_mobile_checklist_item_detail(validated_item_id, request.user),
                status=status.HTTP_200_OK,
            )

        forbid_if(not can_manage_checklist_item(request.user), "Usuario sem permissao para excluir item de checklist.")
        api_services.delete_mobile_checklist_item(validated_item_id)
        return Response({"ok": True}, status=status.HTTP_200_OK)
    except ValidationError as error:
        return validation_error_response(error, request)
    except RepositoryOperationError as error:
        return repository_error_response(error, request)
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncWriteRateThrottle])
def mobile_toggle_checklist_item_status_api(request, item_id):
    try:
        forbid_if(not can_manage_checklist_item(request.user), "Usuario sem permissao para alterar item de checklist.")
        validated_item_id = validate_mobile_identifier(item_id, "item_id")
        return Response(
            api_services.toggle_mobile_checklist_item_status(validated_item_id),
            status=status.HTTP_200_OK,
        )
    except ValidationError as error:
        return validation_error_response(error, request)
    except RepositoryOperationError as error:
        return repository_error_response(error, request)
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)
