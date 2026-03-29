import uuid
from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime

from checklist.exception_handler import is_repository_error
from checklist.repository import checklist_item_repository, work_order_repository
from checklist.utils.data_processing import prepare_image
from checklist.utils.validation_utils import (
    validate_only_letters_and_numbers,
    validate_only_numbers,
)


WORK_ORDER_REQUIRED_KEYS = {
    "operation_code",
    "chassi",
    "horimetro",
    "model",
    "date_in",
    "date_out",
    "status",
    "service",
}

CHECKLIST_REQUIRED_KEYS = {
    "checklist_item_fk",
    "work_order_fk",
    "status",
    "img_in",
    "img_out",
}

VALID_WORK_ORDER_STATUS = {"1", "2", "3", "4"}
VALID_CHECKLIST_STATUS = {"1", "2", "3"}


def _ensure_list(payload, label):
    if not isinstance(payload, list):
        raise ValidationError(f"{label} deve ser uma lista.")
    return payload


def _ensure_dict(payload, label):
    if not isinstance(payload, dict):
        raise ValidationError(f"{label} deve ser um objeto JSON.")
    return payload


def _require_keys(payload, required_keys, label):
    missing_keys = sorted(required_keys - payload.keys())
    if missing_keys:
        raise ValidationError(f"{label} sem chaves obrigatórias: {', '.join(missing_keys)}.")


def _parse_uuid(value, field_name):
    if not value:
        raise ValidationError(f"{field_name} é obrigatório.")

    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} deve ser um UUID válido.")


def _parse_datetime(value, field_name):
    if not value:
        raise ValidationError(f"{field_name} é obrigatório.")

    parsed = parse_datetime(str(value))
    if parsed is not None:
        return parsed

    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        raise ValidationError(f"{field_name} deve ser uma data valida.")


def _require_repository_object(result, field_name):
    if is_repository_error(result):
        raise ValidationError(f"{field_name} informado não existe.")
    return result


def _validate_status(value, allowed_values, field_name):
    if value not in allowed_values:
        raise ValidationError(
            f"{field_name} inválido. Valores permitidos: {', '.join(sorted(allowed_values))}."
        )
    return value


def _validate_chassi(value):
    if not isinstance(value, str) or len(value) != 17 or not value.isalnum():
        raise ValidationError(
            "chassi inválido. Ele deve conter 17 caracteres, sem espaços e sem traços."
        )
    return value


def _validate_model(value):
    if not isinstance(value, str):
        raise ValidationError("model inválido. Ele deve conter somente letras e números.")
    return validate_only_letters_and_numbers(value)


def validate_work_order_entries(payload):
    validated_entries = []

    for index, raw_entry in enumerate(_ensure_list(payload, "work_orders"), start=1):
        entry = _ensure_dict(raw_entry, f"work_order[{index}]")
        _require_keys(entry, WORK_ORDER_REQUIRED_KEYS, f"work_order[{index}]")

        operation_code = entry.get("operation_code")
        if not operation_code:
            raise ValidationError("operation_code é obrigatório.")

        work_order = _require_repository_object(
            work_order_repository.get_by_operation_code(operation_code),
            "operation_code",
        )

        validated_entries.append(
            {
                "work_order": work_order,
                "chassi": _validate_chassi(entry.get("chassi")),
                "horimetro": validate_only_numbers(str(entry.get("horimetro"))),
                "model": _validate_model(entry.get("model")),
                "date_in": _parse_datetime(entry.get("date_in"), "date_in"),
                "date_out": _parse_datetime(entry.get("date_out"), "date_out"),
                "status": _validate_status(entry.get("status"), VALID_WORK_ORDER_STATUS, "status"),
                "service": entry.get("service"),
                "signature_in": prepare_image(
                    entry.get("signature_in") or entry.get("signature"),
                    filename_prefix="signature_in",
                )
                if entry.get("signature_in") or entry.get("signature")
                else None,
                "signature_out": prepare_image(
                    entry.get("signature_out"),
                    filename_prefix="signature_out",
                )
                if entry.get("signature_out")
                else None,
            }
        )

    return validated_entries


def validate_checklist_entries(payload):
    validated_entries = []

    for index, raw_entry in enumerate(_ensure_list(payload, "checklists"), start=1):
        entry = _ensure_dict(raw_entry, f"checklist[{index}]")
        _require_keys(entry, CHECKLIST_REQUIRED_KEYS, f"checklist[{index}]")

        checklist_uuid = (
            _parse_uuid(entry.get("id"), "id") if entry.get("id") else uuid.uuid4()
        )
        checklist_item_uuid = _parse_uuid(entry.get("checklist_item_fk"), "checklist_item_fk")
        work_order_uuid = _parse_uuid(entry.get("work_order_fk"), "work_order_fk")

        checklist_item = _require_repository_object(
            checklist_item_repository.get_by_id(checklist_item_uuid),
            "checklist_item_fk",
        )
        work_order = _require_repository_object(
            work_order_repository.get_by_id(work_order_uuid),
            "work_order_fk",
        )

        validated_entries.append(
            {
                "id": checklist_uuid,
                "checklist_item": checklist_item,
                "work_order": work_order,
                "status": _validate_status(entry.get("status"), VALID_CHECKLIST_STATUS, "status"),
                "image_in": prepare_image(entry.get("img_in"), filename_prefix="checklist_in")
                if entry.get("img_in")
                else None,
                "image_out": prepare_image(entry.get("img_out"), filename_prefix="checklist_out")
                if entry.get("img_out")
                else None,
            }
        )

    return validated_entries
