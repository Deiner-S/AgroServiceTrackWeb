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
    "status",
}

WORK_ORDER_ALLOWED_KEYS = {
    "operation_code",
    "chassi",
    "horimetro",
    "model",
    "date_in",
    "date_out",
    "status",
    "service",
    "signature",
    "signature_in",
    "signature_out",
}

CHECKLIST_REQUIRED_KEYS = {
    "checklist_item_fk",
    "work_order_fk",
    "status",
    "img_in",
    "img_out",
}

MOBILE_LOG_REQUIRED_KEYS = {
    "id",
    "osVersion",
    "deviceModel",
    "connectionStatus",
    "user",
    "erro",
    "stacktrace",
    "horario",
    "status_sync",
}

VALID_WORK_ORDER_STATUS = {"1", "2", "3", "4"}
VALID_CHECKLIST_STATUS = {"1", "2", "3"}
VALID_MOBILE_STATUS_FILTER = {"all", "1", "2", "3", "4"}


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
        raise ValidationError(f"{label} sem chaves obrigatorias: {', '.join(missing_keys)}.")


def _reject_unexpected_keys(payload, allowed_keys, label):
    unexpected_keys = sorted(set(payload.keys()) - set(allowed_keys))
    if unexpected_keys:
        raise ValidationError(f"{label} contem chaves nao esperadas: {', '.join(unexpected_keys)}.")


def _parse_uuid(value, field_name):
    if not value:
        raise ValidationError(f"{field_name} e obrigatorio.")

    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} deve ser um UUID valido.")


def _parse_datetime(value, field_name):
    if not value:
        raise ValidationError(f"{field_name} e obrigatorio.")

    parsed = parse_datetime(str(value))
    if parsed is not None:
        return parsed

    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        raise ValidationError(f"{field_name} deve ser uma data valida.")


def _require_repository_object(result, field_name):
    if is_repository_error(result):
        raise ValidationError(f"{field_name} informado nao existe.")
    return result


def _validate_status(value, allowed_values, field_name):
    if value not in allowed_values:
        raise ValidationError(
            f"{field_name} invalido. Valores permitidos: {', '.join(sorted(allowed_values))}."
        )
    return value


def _validate_chassi(value):
    if not isinstance(value, str) or len(value) != 17 or not value.isalnum():
        raise ValidationError(
            "chassi invalido. Ele deve conter 17 caracteres, sem espacos e sem tracos."
        )
    return value


def _validate_model(value):
    if not isinstance(value, str):
        raise ValidationError("model invalido. Ele deve conter somente letras e numeros.")
    return validate_only_letters_and_numbers(value)


def _validate_mobile_sync_status(value):
    if value not in (0, 1, "0", "1"):
        raise ValidationError("status_sync invalido. Valores permitidos: 0 ou 1.")
    return int(value)


def _validate_required_string(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} deve ser um texto nao vazio.")
    return value.strip()


def validate_mobile_search_query(value):
    if value in (None, ""):
        return ""

    if not isinstance(value, str):
        raise ValidationError("search deve ser um texto.")

    normalized = value.strip()

    if len(normalized) > 120:
        raise ValidationError("search excede o tamanho maximo permitido.")

    return normalized


def validate_mobile_status_filter(value):
    normalized = "all" if value in (None, "") else str(value).strip()

    if normalized not in VALID_MOBILE_STATUS_FILTER:
        raise ValidationError("status invalido para consulta mobile.")

    return normalized


def validate_mobile_identifier(value, field_name):
    return str(_parse_uuid(value, field_name))


def validate_mobile_payload_object(payload, label, allowed_keys=None):
    data = _ensure_dict(payload, label)

    if allowed_keys is not None:
        _reject_unexpected_keys(data, allowed_keys, label)

    return data


def validate_work_order_entries(payload):
    validated_entries = []

    for index, raw_entry in enumerate(_ensure_list(payload, "work_orders"), start=1):
        entry = _ensure_dict(raw_entry, f"work_order[{index}]")
        _reject_unexpected_keys(entry, WORK_ORDER_ALLOWED_KEYS, f"work_order[{index}]")

        operation_code = entry.get("operation_code")
        if not operation_code:
            raise ValidationError("operation_code e obrigatorio.")

        status = _validate_status(entry.get("status"), VALID_WORK_ORDER_STATUS, "status")

        required_keys = set(WORK_ORDER_REQUIRED_KEYS)
        if status != "1":
            required_keys.update({"chassi", "horimetro", "model", "date_in"})
        if status in {"3", "4"}:
            required_keys.add("service")
        if status == "4":
            required_keys.add("date_out")

        _require_keys(entry, required_keys, f"work_order[{index}]")

        work_order = _require_repository_object(
            work_order_repository.get_by_operation_code(operation_code),
            "operation_code",
        )

        validated_entry = {
            "work_order": work_order,
            "status": status,
            "service": entry.get("service"),
            "date_out": None,
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

        if status != "1":
            validated_entry.update(
                {
                    "chassi": _validate_chassi(entry.get("chassi")),
                    "horimetro": validate_only_numbers(str(entry.get("horimetro"))),
                    "model": _validate_model(entry.get("model")),
                    "date_in": _parse_datetime(entry.get("date_in"), "date_in"),
                }
            )

        if status == "4":
            validated_entry["date_out"] = _parse_datetime(entry.get("date_out"), "date_out")
        elif entry.get("date_out"):
            validated_entry["date_out"] = _parse_datetime(entry.get("date_out"), "date_out")

        validated_entries.append(validated_entry)

    return validated_entries


def validate_checklist_entries(payload):
    validated_entries = []

    for index, raw_entry in enumerate(_ensure_list(payload, "checklists"), start=1):
        entry = _ensure_dict(raw_entry, f"checklist[{index}]")
        _require_keys(entry, CHECKLIST_REQUIRED_KEYS, f"checklist[{index}]")

        checklist_uuid = _parse_uuid(entry.get("id"), "id") if entry.get("id") else uuid.uuid4()
        checklist_item_uuid = _parse_uuid(entry.get("checklist_item_fk"), "checklist_item_fk")
        work_order_operation_code = entry.get("work_order_fk")
        if not isinstance(work_order_operation_code, str) or not work_order_operation_code.strip():
            raise ValidationError("work_order_fk e obrigatorio.")
        work_order_operation_code = work_order_operation_code.strip()

        checklist_item = _require_repository_object(
            checklist_item_repository.get_by_id(checklist_item_uuid),
            "checklist_item_fk",
        )
        work_order = _require_repository_object(
            work_order_repository.get_by_operation_code(work_order_operation_code),
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


def validate_mobile_log_entries(payload):
    validated_entries = []
    valid_connection_status = {"online", "offline", "unknown"}

    for index, raw_entry in enumerate(_ensure_list(payload, "mobile_logs"), start=1):
        entry = _ensure_dict(raw_entry, f"mobile_log[{index}]")
        _require_keys(entry, MOBILE_LOG_REQUIRED_KEYS, f"mobile_log[{index}]")
        _reject_unexpected_keys(entry, MOBILE_LOG_REQUIRED_KEYS, f"mobile_log[{index}]")

        validated_entries.append(
            {
                "id": str(_parse_uuid(entry.get("id"), "id")),
                "osVersion": _validate_required_string(entry.get("osVersion"), "osVersion"),
                "deviceModel": _validate_required_string(entry.get("deviceModel"), "deviceModel"),
                "connectionStatus": _validate_status(
                    entry.get("connectionStatus"),
                    valid_connection_status,
                    "connectionStatus",
                ),
                "user": _validate_required_string(entry.get("user"), "user"),
                "erro": _validate_required_string(entry.get("erro"), "erro"),
                "stacktrace": (
                    _validate_required_string(entry.get("stacktrace"), "stacktrace")
                    if entry.get("stacktrace") is not None
                    else None
                ),
                "horario": _parse_datetime(entry.get("horario"), "horario").isoformat(),
                "status_sync": _validate_mobile_sync_status(entry.get("status_sync")),
            }
        )

    return validated_entries
