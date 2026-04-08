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
    can_create_employee,
    can_edit_employee,
    can_manage_employee_addresses,
    can_toggle_employee_status,
    can_view_employee_module,
)
from checklist.repository import address_repository, employee_repository
from checklist.services import api_services
from checklist.throttling import SyncReadRateThrottle, SyncWriteRateThrottle
from checklist.views.api.common import forbid_if, system_error_response, validation_error_response
from checklist.views.api.mobile_management_shared import (
    AddressForm,
    EMPLOYEE_CREATE_ALLOWED_KEYS,
    EMPLOYEE_ADDRESS_ALLOWED_KEYS,
    EMPLOYEE_UPDATE_ALLOWED_KEYS,
    EmployeeForm,
    EmployeeDetailForm,
    raise_form_validation_error,
)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SyncReadRateThrottle])
def mobile_employees_api(request):
    try:
        if request.method == 'GET':
            forbid_if(not can_view_employee_module(request.user), "Usuario sem permissao para consultar funcionarios.")
            search_query = validate_mobile_search_query(request.query_params.get("search"))
            return Response(api_services.get_mobile_employees(search_query), status=status.HTTP_200_OK)

        forbid_if(not can_create_employee(request.user), "Usuario sem permissao para cadastrar funcionarios.")
        payload = validate_mobile_payload_object(request.data, "employee_create_payload", EMPLOYEE_CREATE_ALLOWED_KEYS)
        form = EmployeeForm(payload, actor=request.user)

        if not form.is_valid():
            raise_form_validation_error(form)

        created_employee = api_services.create_mobile_employee(
            form.save(commit=False),
            form.cleaned_data["password"],
        )
        return Response(
            api_services.get_mobile_employee_detail(str(created_employee.id), request.user),
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
def mobile_employee_create_form_api(request):
    try:
        forbid_if(not can_create_employee(request.user), "Usuario sem permissao para cadastrar funcionarios.")
        return Response(
            api_services.get_mobile_employee_create_options(request.user),
            status=status.HTTP_200_OK,
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
        payload = validate_mobile_payload_object(request.data, "employee_update_payload", EMPLOYEE_UPDATE_ALLOWED_KEYS)
        form = EmployeeDetailForm(payload, instance=employee, actor=request.user)

        if not form.is_valid():
            raise_form_validation_error(form)

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
        forbid_if(not can_manage_employee_addresses(request.user, employee), "Usuario sem permissao para editar enderecos deste funcionario.")

        payload = validate_mobile_payload_object(request.data, "employee_address_payload", EMPLOYEE_ADDRESS_ALLOWED_KEYS)
        form = AddressForm(payload)

        if not form.is_valid():
            raise_form_validation_error(form)

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
        forbid_if(not can_manage_employee_addresses(request.user, employee), "Usuario sem permissao para editar enderecos deste funcionario.")

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
        forbid_if(not can_toggle_employee_status(request.user, employee), "Usuario sem permissao para alterar o funcionario.")
        return Response(api_services.toggle_mobile_employee_status(validated_employee_id), status=status.HTTP_200_OK)
    except ValidationError as error:
        return validation_error_response(error, request)
    except PermissionDenied:
        raise
    except Exception as error:
        return system_error_response(error, request)
