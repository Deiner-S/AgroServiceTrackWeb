import uuid

import pytest
from django.core.exceptions import ValidationError

from checklist.api_payload_validation import (
    _ensure_dict,
    _ensure_list,
    _parse_datetime,
    _parse_uuid,
    _require_keys,
    _require_repository_object,
    _validate_chassi,
    _validate_model,
    validate_mobile_identifier,
    validate_mobile_log_entries,
    validate_mobile_payload_object,
    validate_mobile_search_query,
    validate_mobile_status_filter,
    _validate_status,
    validate_checklist_entries,
    validate_work_order_entries,
)


@pytest.mark.django_db
def test_validate_work_order_entries_returns_normalized_payload(work_order):
    payload = [
        {
            "operation_code": "000001",
            "chassi": "1HGCM82633A123456",
            "horimetro": "12345",
            "model": "Trator2025",
            "date_in": "2026-03-25T10:00:00",
            "date_out": "2026-03-25T11:00:00",
            "status": "2",
            "service": "Troca completa",
        }
    ]

    validated = validate_work_order_entries(payload)

    assert validated[0]["work_order"].id == work_order.id
    assert validated[0]["chassi"] == "1HGCM82633A123456"
    assert validated[0]["status"] == "2"


@pytest.mark.django_db
def test_validate_work_order_entries_rejects_invalid_chassi(work_order):
    payload = [
        {
            "operation_code": "000001",
            "chassi": "ABC-123",
            "horimetro": "12345",
            "model": "Trator2025",
            "date_in": "2026-03-25T10:00:00",
            "date_out": "2026-03-25T11:00:00",
            "status": "2",
            "service": "Troca completa",
        }
    ]

    with pytest.raises(ValidationError):
        validate_work_order_entries(payload)


@pytest.mark.django_db
def test_validate_checklist_entries_returns_normalized_payload(work_order, checklist_item):
    payload = [
        {
            "id": str(uuid.uuid4()),
            "checklist_item_fk": str(checklist_item.id),
            "work_order_fk": str(work_order.id),
            "status": "1",
            "img_in": None,
            "img_out": None,
        }
    ]

    validated = validate_checklist_entries(payload)

    assert validated[0]["checklist_item"].id == checklist_item.id
    assert validated[0]["work_order"].id == work_order.id
    assert validated[0]["status"] == "1"


@pytest.mark.django_db
def test_validate_checklist_entries_rejects_invalid_image(work_order, checklist_item):
    payload = [
        {
            "id": str(uuid.uuid4()),
            "checklist_item_fk": str(checklist_item.id),
            "work_order_fk": str(work_order.id),
            "status": "1",
            "img_in": b"not-an-image",
            "img_out": None,
        }
    ]

    with pytest.raises(ValidationError):
        validate_checklist_entries(payload)


def test_ensure_list_raises_for_invalid_payload_type():
    with pytest.raises(ValidationError, match="work_orders deve ser uma lista."):
        _ensure_list({}, "work_orders")


def test_ensure_dict_raises_for_invalid_payload_type():
    with pytest.raises(ValidationError, match="work_order\\[1\\] deve ser um objeto JSON."):
        _ensure_dict([], "work_order[1]")


def test_require_keys_raises_when_required_keys_are_missing():
    with pytest.raises(ValidationError, match="sem chaves obrigatorias"):
        _require_keys({"operation_code": "1"}, {"operation_code", "status"}, "work_order[1]")


def test_parse_uuid_raises_for_missing_value():
    with pytest.raises(ValidationError, match="id e obrigatorio."):
        _parse_uuid(None, "id")


def test_parse_uuid_raises_for_invalid_value():
    with pytest.raises(ValidationError, match="checklist_item_fk deve ser um UUID valido."):
        _parse_uuid("abc", "checklist_item_fk")


def test_parse_datetime_raises_for_missing_value():
    with pytest.raises(ValidationError, match="date_in e obrigatorio."):
        _parse_datetime(None, "date_in")


def test_parse_datetime_raises_for_invalid_value():
    with pytest.raises(ValidationError, match="date_out deve ser uma data valida."):
        _parse_datetime("data-invalida", "date_out")


def test_require_repository_object_raises_for_repository_error_payload():
    with pytest.raises(ValidationError, match="operation_code informado nao existe."):
        _require_repository_object(({"error": "Nao encontrado"}, 404), "operation_code")


def test_validate_status_raises_for_invalid_work_order_status():
    with pytest.raises(ValidationError, match="status invalido"):
        _validate_status("9", {"1", "2"}, "status")


def test_validate_chassi_raises_for_invalid_value():
    with pytest.raises(ValidationError, match="chassi invalido"):
        _validate_chassi("ABC-123")


def test_validate_model_raises_for_invalid_type():
    with pytest.raises(ValidationError, match="model invalido"):
        _validate_model(123)


def test_validate_mobile_log_entries_returns_normalized_payload():
    payload = [
        {
            "id": str(uuid.uuid4()),
            "osVersion": "35",
            "deviceModel": "Pixel 9",
            "user": "deiner",
            "erro": "Falha ao salvar checklist",
            "stacktrace": "trace",
            "horario": "2026-03-31T12:00:00",
            "status_sync": 0,
        }
    ]

    validated = validate_mobile_log_entries(payload)

    assert validated[0]["osVersion"] == "35"
    assert validated[0]["status_sync"] == 0


def test_validate_mobile_log_entries_rejects_unexpected_keys():
    payload = [
        {
            "id": str(uuid.uuid4()),
            "osVersion": "35",
            "deviceModel": "Pixel 9",
            "user": "deiner",
            "erro": "Falha ao salvar checklist",
            "stacktrace": "trace",
            "horario": "2026-03-31T12:00:00",
            "status_sync": 0,
            "extra": True,
        }
    ]

    with pytest.raises(ValidationError, match="chaves nao esperadas"):
        validate_mobile_log_entries(payload)


def test_validate_mobile_log_entries_rejects_invalid_status_sync():
    payload = [
        {
            "id": str(uuid.uuid4()),
            "osVersion": "35",
            "deviceModel": "Pixel 9",
            "user": "deiner",
            "erro": "Falha ao salvar checklist",
            "stacktrace": "trace",
            "horario": "2026-03-31T12:00:00",
            "status_sync": 9,
        }
    ]

    with pytest.raises(ValidationError, match="status_sync invalido"):
        validate_mobile_log_entries(payload)


def test_validate_mobile_search_query_normalizes_blank_values():
    assert validate_mobile_search_query("   ") == ""


def test_validate_mobile_search_query_rejects_large_values():
    with pytest.raises(ValidationError, match="maximo permitido"):
        validate_mobile_search_query("a" * 121)


def test_validate_mobile_status_filter_returns_all_by_default():
    assert validate_mobile_status_filter(None) == "all"


def test_validate_mobile_status_filter_rejects_invalid_values():
    with pytest.raises(ValidationError, match="status invalido"):
        validate_mobile_status_filter("9")


def test_validate_mobile_identifier_returns_uuid_string():
    value = "11111111-1111-4111-8111-111111111111"
    assert validate_mobile_identifier(value, "client_id") == value


def test_validate_mobile_payload_object_rejects_unexpected_keys():
    with pytest.raises(ValidationError, match="chaves nao esperadas"):
        validate_mobile_payload_object({"name": "Cliente", "extra": True}, "client_payload", {"name"})


@pytest.mark.django_db
def test_validate_work_order_entries_raises_for_non_list_payload():
    with pytest.raises(ValidationError, match="work_orders deve ser uma lista."):
        validate_work_order_entries({})


@pytest.mark.django_db
def test_validate_work_order_entries_raises_for_missing_required_keys():
    payload = [{"operation_code": "000001"}]

    with pytest.raises(ValidationError, match="sem chaves obrigatorias"):
        validate_work_order_entries(payload)


@pytest.mark.django_db
def test_validate_work_order_entries_raises_for_missing_operation_code():
    payload = [
        {
            "operation_code": "",
            "chassi": "1HGCM82633A123456",
            "horimetro": "12345",
            "model": "Trator2025",
            "date_in": "2026-03-25T10:00:00",
            "date_out": "2026-03-25T11:00:00",
            "status": "2",
            "service": "Troca completa",
        }
    ]

    with pytest.raises(ValidationError, match="operation_code e obrigatorio."):
        validate_work_order_entries(payload)


@pytest.mark.django_db
def test_validate_work_order_entries_raises_for_missing_repository_object(monkeypatch):
    monkeypatch.setattr(
        "checklist.api_payload_validation.work_order_repository.get_by_operation_code",
        lambda operation_code: ({"error": "Nao encontrado"}, 404),
    )

    payload = [
        {
            "operation_code": "000001",
            "chassi": "1HGCM82633A123456",
            "horimetro": "12345",
            "model": "Trator2025",
            "date_in": "2026-03-25T10:00:00",
            "date_out": "2026-03-25T11:00:00",
            "status": "2",
            "service": "Troca completa",
        }
    ]

    with pytest.raises(ValidationError, match="operation_code informado nao existe."):
        validate_work_order_entries(payload)


@pytest.mark.django_db
def test_validate_checklist_entries_raises_for_non_list_payload():
    with pytest.raises(ValidationError, match="checklists deve ser uma lista."):
        validate_checklist_entries({})


@pytest.mark.django_db
def test_validate_checklist_entries_raises_for_missing_required_keys():
    payload = [{"id": str(uuid.uuid4())}]

    with pytest.raises(ValidationError, match="sem chaves obrigatorias"):
        validate_checklist_entries(payload)


@pytest.mark.django_db
def test_validate_checklist_entries_raises_for_invalid_checklist_item_uuid():
    payload = [
        {
            "id": str(uuid.uuid4()),
            "checklist_item_fk": "uuid-invalido",
            "work_order_fk": str(uuid.uuid4()),
            "status": "1",
            "img_in": None,
            "img_out": None,
        }
    ]

    with pytest.raises(ValidationError, match="checklist_item_fk deve ser um UUID valido."):
        validate_checklist_entries(payload)


@pytest.mark.django_db
def test_validate_checklist_entries_raises_for_missing_repository_object(monkeypatch):
    monkeypatch.setattr(
        "checklist.api_payload_validation.checklist_item_repository.get_by_id",
        lambda checklist_item_id: ({"error": "Nao encontrado"}, 404),
    )

    payload = [
        {
            "id": str(uuid.uuid4()),
            "checklist_item_fk": str(uuid.uuid4()),
            "work_order_fk": str(uuid.uuid4()),
            "status": "1",
            "img_in": None,
            "img_out": None,
        }
    ]

    with pytest.raises(ValidationError, match="checklist_item_fk informado nao existe."):
        validate_checklist_entries(payload)
