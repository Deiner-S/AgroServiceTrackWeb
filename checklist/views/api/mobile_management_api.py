from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from checklist.api_payload_validation import (
    validate_mobile_payload_object,
    validate_mobile_identifier,
    validate_mobile_search_query,
)
from checklist.exception_handler import RepositoryOperationError
from checklist.forms import AddressForm, ChecklistItemForm, ClientDetailForm, ClientForm, DataSheetCreateForm, EmployeeDetailForm
from checklist.permissions import (
    can_edit_employee,
    can_manage_checklist_item,
    can_manage_client,
    can_manage_client_addresses,
    can_manage_employee_addresses,
    can_create_service_order,
    can_toggle_employee_status,
    can_view_checklist_item_module,
    can_view_client_detail,
    can_view_client_list,
    can_view_employee_module,
)
from checklist.repository import address_repository, client_repository, employee_repository
from checklist.services import api_services
from checklist.throttling import SyncReadRateThrottle, SyncWriteRateThrottle
from checklist.views.api.common import (
    forbid_if,
    repository_error_response,
    system_error_response,
    validation_error_response,
)


CLIENT_CREATE_ALLOWED_KEYS = {"cnpj", "name", "email", "phone"}
CLIENT_UPDATE_ALLOWED_KEYS = {"cpf", "cnpj", "name", "email", "phone"}
CLIENT_ADDRESS_ALLOWED_KEYS = {"street", "number", "complement", "city", "state", "zip_code"}
CLIENT_SERVICE_ALLOWED_KEYS = {"operation_code", "symptoms"}
CHECKLIST_ITEM_ALLOWED_KEYS = {"name"}
EMPLOYEE_UPDATE_ALLOWED_KEYS = {
    "first_name",
    "last_name",
    "cpf",
    "phone",
    "email",
    "position",
    "username",
    "password",
}
EMPLOYEE_ADDRESS_ALLOWED_KEYS = {"street", "number", "complement", "city", "state", "zip_code"}


def _raise_form_validation_error(form):
    raise ValidationError(form.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_dashboard_api(request):
    try:
        return Response(api_services.get_mobile_dashboard(request.user), status=status.HTTP_200_OK)
    except Exception as error:
        return system_error_response(error, request)


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
        payload = validate_mobile_payload_object(
            request.data,
            "client_payload",
            CLIENT_CREATE_ALLOWED_KEYS,
        )
        form = ClientForm(payload)

        if not form.is_valid():
            _raise_form_validation_error(form)

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
        payload = validate_mobile_payload_object(
            request.data,
            "client_update_payload",
            CLIENT_UPDATE_ALLOWED_KEYS,
        )
        form = ClientDetailForm(payload, instance=client)

        if not form.is_valid():
            _raise_form_validation_error(form)

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

        payload = validate_mobile_payload_object(
            request.data,
            "client_address_payload",
            CLIENT_ADDRESS_ALLOWED_KEYS,
        )
        form = AddressForm(payload)

        if not form.is_valid():
            _raise_form_validation_error(form)

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

        payload = validate_mobile_payload_object(
            request.data,
            "client_service_payload",
            CLIENT_SERVICE_ALLOWED_KEYS,
        )
        form = DataSheetCreateForm(payload)

        if not form.is_valid():
            _raise_form_validation_error(form)

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
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_employee_detail_api(request, employee_id):
    try:
        validated_employee_id = validate_mobile_identifier(employee_id, "employee_id")
        employee = employee_repository.get_by_identifier(validated_employee_id)
        employee = employee if not isinstance(employee, tuple) else None
        forbid_if(employee is None, "Funcionario nao encontrado.")

        if request.method == 'GET':
            forbid_if(not can_view_employee_module(request.user), "Usuario sem permissao para consultar funcionario.")
            return Response(
                api_services.get_mobile_employee_detail(validated_employee_id, request.user),
                status=status.HTTP_200_OK,
            )

        forbid_if(not can_edit_employee(request.user, employee), "Usuario sem permissao para editar o funcionario.")
        payload = validate_mobile_payload_object(
            request.data,
            "employee_update_payload",
            EMPLOYEE_UPDATE_ALLOWED_KEYS,
        )
        form = EmployeeDetailForm(
            payload,
            instance=employee,
            actor=request.user,
        )

        if not form.is_valid():
            _raise_form_validation_error(form)

        updated_employee = form.save(commit=False)
        new_password = form.cleaned_data.get("password")
        if new_password:
            updated_employee.set_password(new_password)

        saved_employee = api_services.update_mobile_employee(updated_employee)
        return Response(
            api_services.get_mobile_employee_detail(str(saved_employee.id), request.user),
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
def mobile_add_employee_address_api(request, employee_id):
    try:
        validated_employee_id = validate_mobile_identifier(employee_id, "employee_id")
        employee = employee_repository.get_by_identifier(validated_employee_id)
        employee = employee if not isinstance(employee, tuple) else None
        forbid_if(employee is None, "Funcionario nao encontrado.")
        forbid_if(
            not can_manage_employee_addresses(request.user, employee),
            "Usuario sem permissao para editar enderecos deste funcionario.",
        )

        payload = validate_mobile_payload_object(
            request.data,
            "employee_address_payload",
            EMPLOYEE_ADDRESS_ALLOWED_KEYS,
        )
        form = AddressForm(payload)

        if not form.is_valid():
            _raise_form_validation_error(form)

        api_services.create_mobile_employee_address(employee, form.save(commit=False))
        return Response(
            api_services.get_mobile_employee_detail(validated_employee_id, request.user),
            status=status.HTTP_201_CREATED,
        )
    except ValidationError as error:
        return validation_error_response(error, request)
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncWriteRateThrottle])
def mobile_delete_employee_address_api(request, employee_id, address_id):
    try:
        validated_employee_id = validate_mobile_identifier(employee_id, "employee_id")
        validated_address_id = validate_mobile_identifier(address_id, "address_id")
        employee = employee_repository.get_by_identifier(validated_employee_id)
        employee = employee if not isinstance(employee, tuple) else None
        forbid_if(employee is None, "Funcionario nao encontrado.")
        forbid_if(
            not can_manage_employee_addresses(request.user, employee),
            "Usuario sem permissao para editar enderecos deste funcionario.",
        )

        address = address_repository.get_by_id(validated_address_id)
        address = address if not isinstance(address, tuple) else None
        forbid_if(address is None, "Endereco nao encontrado.")

        api_services.delete_mobile_employee_address(employee, address)
        return Response(
            api_services.get_mobile_employee_detail(validated_employee_id, request.user),
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
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_checklist_items_api(request):
    try:
        if request.method == 'GET':
            forbid_if(
                not can_view_checklist_item_module(request.user),
                "Usuario sem permissao para consultar itens de checklist.",
            )
            search_query = validate_mobile_search_query(request.query_params.get("search"))
            return Response(api_services.get_mobile_checklist_items(search_query), status=status.HTTP_200_OK)

        forbid_if(
            not can_manage_checklist_item(request.user),
            "Usuario sem permissao para cadastrar item de checklist.",
        )
        payload = validate_mobile_payload_object(
            request.data,
            "checklist_item_payload",
            CHECKLIST_ITEM_ALLOWED_KEYS,
        )
        form = ChecklistItemForm(payload)

        if not form.is_valid():
            _raise_form_validation_error(form)

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
            forbid_if(
                not can_view_checklist_item_module(request.user),
                "Usuario sem permissao para consultar item de checklist.",
            )
            return Response(
                api_services.get_mobile_checklist_item_detail(validated_item_id, request.user),
                status=status.HTTP_200_OK,
            )

        forbid_if(
            not can_manage_checklist_item(request.user),
            "Usuario sem permissao para excluir item de checklist.",
        )
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
    except RepositoryOperationError as error:
        return repository_error_response(error, request)
