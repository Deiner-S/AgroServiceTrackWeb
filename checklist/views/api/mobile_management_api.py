from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from checklist.api_payload_validation import (
    validate_mobile_identifier,
    validate_mobile_search_query,
)
from checklist.permissions import (
    can_manage_checklist_item,
    can_toggle_employee_status,
    can_view_checklist_item_module,
    can_view_client_detail,
    can_view_client_list,
    can_view_employee_module,
)
from checklist.repository import employee_repository
from checklist.services import api_services
from checklist.throttling import SyncReadRateThrottle, SyncWriteRateThrottle
from checklist.views.api.common import forbid_if, validation_error_response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_dashboard_api(request):
    return Response(api_services.get_mobile_dashboard(request.user), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_clients_api(request):
    try:
        forbid_if(not can_view_client_list(request.user), "Usuario sem permissao para consultar clientes.")
        search_query = validate_mobile_search_query(request.query_params.get("search"))
        return Response(api_services.get_mobile_clients(search_query), status=status.HTTP_200_OK)
    except ValidationError as error:
        return validation_error_response(error, request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_client_detail_api(request, client_id):
    try:
        forbid_if(not can_view_client_detail(request.user), "Usuario sem permissao para consultar detalhes de clientes.")
        validated_client_id = validate_mobile_identifier(client_id, "client_id")
        return Response(api_services.get_mobile_client_detail(validated_client_id), status=status.HTTP_200_OK)
    except ValidationError as error:
        return validation_error_response(error, request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_employees_api(request):
    try:
        forbid_if(not can_view_employee_module(request.user), "Usuario sem permissao para consultar funcionarios.")
        search_query = validate_mobile_search_query(request.query_params.get("search"))
        return Response(api_services.get_mobile_employees(search_query), status=status.HTTP_200_OK)
    except ValidationError as error:
        return validation_error_response(error, request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_employee_detail_api(request, employee_id):
    try:
        forbid_if(not can_view_employee_module(request.user), "Usuario sem permissao para consultar funcionario.")
        validated_employee_id = validate_mobile_identifier(employee_id, "employee_id")
        return Response(api_services.get_mobile_employee_detail(validated_employee_id, request.user), status=status.HTTP_200_OK)
    except ValidationError as error:
        return validation_error_response(error, request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncWriteRateThrottle])
def mobile_toggle_employee_status_api(request, employee_id):
    try:
        validated_employee_id = validate_mobile_identifier(employee_id, "employee_id")
        employee = employee_repository.get_by_identifier(validated_employee_id)
        employee = employee if not isinstance(employee, tuple) else None
        forbid_if(employee is None, "Funcionario nao encontrado.")
        forbid_if(
            not can_toggle_employee_status(request.user, employee),
            "Usuario sem permissao para alterar o funcionario.",
        )
        return Response(
            api_services.toggle_mobile_employee_status(validated_employee_id),
            status=status.HTTP_200_OK,
        )
    except ValidationError as error:
        return validation_error_response(error, request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_checklist_items_api(request):
    try:
        forbid_if(
            not can_view_checklist_item_module(request.user),
            "Usuario sem permissao para consultar itens de checklist.",
        )
        search_query = validate_mobile_search_query(request.query_params.get("search"))
        return Response(api_services.get_mobile_checklist_items(search_query), status=status.HTTP_200_OK)
    except ValidationError as error:
        return validation_error_response(error, request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_checklist_item_detail_api(request, item_id):
    try:
        forbid_if(
            not can_view_checklist_item_module(request.user),
            "Usuario sem permissao para consultar item de checklist.",
        )
        validated_item_id = validate_mobile_identifier(item_id, "item_id")
        return Response(
            api_services.get_mobile_checklist_item_detail(validated_item_id, request.user),
            status=status.HTTP_200_OK,
        )
    except ValidationError as error:
        return validation_error_response(error, request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncWriteRateThrottle])
def mobile_toggle_checklist_item_status_api(request, item_id):
    try:
        forbid_if(
            not can_manage_checklist_item(request.user),
            "Usuario sem permissao para alterar item de checklist.",
        )
        validated_item_id = validate_mobile_identifier(item_id, "item_id")
        return Response(
            api_services.toggle_mobile_checklist_item_status(validated_item_id),
            status=status.HTTP_200_OK,
        )
    except ValidationError as error:
        return validation_error_response(error, request)
