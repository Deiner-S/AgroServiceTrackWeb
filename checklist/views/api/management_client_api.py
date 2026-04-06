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
from checklist.permissions import (
    can_create_service_order,
    can_manage_client,
    can_manage_client_addresses,
    can_view_client_detail,
    can_view_client_list,
)
from checklist.repository import client_repository
from checklist.services import api_services
from checklist.throttling import SyncReadRateThrottle, SyncWriteRateThrottle
from checklist.views.api.common import forbid_if, system_error_response, validation_error_response
from checklist.views.api.mobile_management_shared import (
    AddressForm,
    CLIENT_ADDRESS_ALLOWED_KEYS,
    CLIENT_CREATE_ALLOWED_KEYS,
    CLIENT_SERVICE_ALLOWED_KEYS,
    CLIENT_UPDATE_ALLOWED_KEYS,
    ClientDetailForm,
    ClientForm,
    DataSheetCreateForm,
    raise_form_validation_error,
)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_clients_api(request):
    try:
        if request.method == 'GET':
            forbid_if(not can_view_client_list(request.user), "Usuario sem permissao para consultar clientes.")
            search_query = validate_mobile_search_query(request.query_params.get("search"))
            return Response(api_services.get_mobile_clients(search_query), status=status.HTTP_200_OK)

        forbid_if(not can_manage_client(request.user), "Usuario sem permissao para cadastrar clientes.")
        payload = validate_mobile_payload_object(request.data, "client_payload", CLIENT_CREATE_ALLOWED_KEYS)
        form = ClientForm(payload)

        if not form.is_valid():
            raise_form_validation_error(form)

        client = api_services.create_mobile_client(form.save(commit=False))
        return Response(
            api_services.get_mobile_client_detail(str(client.id), request.user),
            status=status.HTTP_201_CREATED,
        )
    except ValidationError as error:
        return validation_error_response(error, request)
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_client_detail_api(request, client_id):
    try:
        validated_client_id = validate_mobile_identifier(client_id, "client_id")
        client = client_repository.get_by_id(validated_client_id)
        client = client if not isinstance(client, tuple) else None
        forbid_if(client is None, "Cliente nao encontrado.")

        if request.method == 'GET':
            forbid_if(not can_view_client_detail(request.user), "Usuario sem permissao para consultar detalhes de clientes.")
            return Response(
                api_services.get_mobile_client_detail(validated_client_id, request.user),
                status=status.HTTP_200_OK,
            )

        forbid_if(not can_manage_client(request.user), "Usuario sem permissao para editar clientes.")
        payload = validate_mobile_payload_object(request.data, "client_update_payload", CLIENT_UPDATE_ALLOWED_KEYS)
        form = ClientDetailForm(payload, instance=client)

        if not form.is_valid():
            raise_form_validation_error(form)

        updated_client = api_services.update_mobile_client(form.save(commit=False))
        return Response(
            api_services.get_mobile_client_detail(str(updated_client.id), request.user),
            status=status.HTTP_200_OK,
        )
    except ValidationError as error:
        return validation_error_response(error, request)
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncWriteRateThrottle])
def mobile_add_client_address_api(request, client_id):
    try:
        validated_client_id = validate_mobile_identifier(client_id, "client_id")
        client = client_repository.get_by_id(validated_client_id)
        client = client if not isinstance(client, tuple) else None
        forbid_if(client is None, "Cliente nao encontrado.")
        forbid_if(not can_manage_client_addresses(request.user), "Usuario sem permissao para editar enderecos de clientes.")

        payload = validate_mobile_payload_object(request.data, "client_address_payload", CLIENT_ADDRESS_ALLOWED_KEYS)
        form = AddressForm(payload)

        if not form.is_valid():
            raise_form_validation_error(form)

        api_services.create_mobile_client_address(client, form.save(commit=False))
        return Response(
            api_services.get_mobile_client_detail(validated_client_id, request.user),
            status=status.HTTP_201_CREATED,
        )
    except ValidationError as error:
        return validation_error_response(error, request)
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncWriteRateThrottle])
def mobile_add_client_service_order_api(request, client_id):
    try:
        validated_client_id = validate_mobile_identifier(client_id, "client_id")
        client = client_repository.get_by_id(validated_client_id)
        client = client if not isinstance(client, tuple) else None
        forbid_if(client is None, "Cliente nao encontrado.")
        forbid_if(not can_create_service_order(request.user), "Usuario sem permissao para abrir ordens de servico.")

        payload = validate_mobile_payload_object(request.data, "client_service_payload", CLIENT_SERVICE_ALLOWED_KEYS)
        form = DataSheetCreateForm(payload)

        if not form.is_valid():
            raise_form_validation_error(form)

        api_services.create_mobile_client_order(client, form.save(commit=False))
        return Response(
            api_services.get_mobile_client_detail(validated_client_id, request.user),
            status=status.HTTP_201_CREATED,
        )
    except ValidationError as error:
        return validation_error_response(error, request)
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)
