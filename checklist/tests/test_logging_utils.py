import json
import uuid
from types import SimpleNamespace

from django.test import RequestFactory

import pytest

from checklist.utils.logging_utils import (
    LogPersistenceError,
    save_log,
    save_mobile_log,
    save_security_log,
)


def _build_authenticated_request():
    request = RequestFactory().post("/gerenciador/receive_mobile_logs_api/")
    request.user = type(
        "AuthenticatedUser",
        (),
        {
            "is_authenticated": True,
            "id": uuid.uuid4(),
        },
    )()
    return request


def test_save_log_serializes_uuid_request_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr("checklist.utils.logging_utils._get_log_dir", lambda: tmp_path)

    request = _build_authenticated_request()
    error = ValueError("falha de teste")

    save_log(error, request=request)

    lines = (tmp_path / "api_errors.jsonl").read_text(encoding="utf-8").strip().splitlines()
    payload = json.loads(lines[-1])

    assert payload["error_message"] == "falha de teste"
    assert payload["user_id"] == str(request.user.id)
    assert "ValueError: falha de teste" in payload["stacktrace"]


def test_save_mobile_log_serializes_uuid_and_request_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr("checklist.utils.logging_utils._get_log_dir", lambda: tmp_path)

    request = _build_authenticated_request()
    log_entry = {
        "id": str(uuid.uuid4()),
        "status_sync": 0,
        "user_uuid": uuid.uuid4(),
    }

    assert save_mobile_log(log_entry, request=request) is True

    lines = (tmp_path / "mobile_app_logs.jsonl").read_text(encoding="utf-8").strip().splitlines()
    payload = json.loads(lines[-1])

    assert payload["user_id"] == str(request.user.id)
    assert payload["user_uuid"] == str(log_entry["user_uuid"])


def test_save_mobile_log_serializes_nested_objects_with_uuid(tmp_path, monkeypatch):
    monkeypatch.setattr("checklist.utils.logging_utils._get_log_dir", lambda: tmp_path)

    request = _build_authenticated_request()
    log_entry = {
        "id": str(uuid.uuid4()),
        "payload": SimpleNamespace(user_uuid=uuid.uuid4(), attempt=2),
    }

    assert save_mobile_log(log_entry, request=request) is True

    lines = (tmp_path / "mobile_app_logs.jsonl").read_text(encoding="utf-8").strip().splitlines()
    payload = json.loads(lines[-1])

    assert payload["payload"]["attempt"] == 2
    assert isinstance(payload["payload"]["user_uuid"], str)


def test_save_mobile_log_raises_when_primary_writer_breaks(tmp_path, monkeypatch):
    monkeypatch.setattr("checklist.utils.logging_utils._get_log_dir", lambda: tmp_path)

    def failing_write_log_line(filename, payload):
        raise TypeError("writer failure")

    monkeypatch.setattr("checklist.utils.logging_utils._write_log_line", failing_write_log_line)

    with pytest.raises(LogPersistenceError, match="mobile_app_logs.jsonl"):
        save_mobile_log({"id": str(uuid.uuid4())}, request=_build_authenticated_request())

    lines = (tmp_path / "logging_failures.jsonl").read_text(encoding="utf-8").strip().splitlines()
    payload = json.loads(lines[-1])

    assert payload["logger_error"] == "writer failure"
    assert payload["target_file"] == "mobile_app_logs.jsonl"


def test_save_security_log_falls_back_to_logging_failures_when_writer_breaks(tmp_path, monkeypatch):
    monkeypatch.setattr("checklist.utils.logging_utils._get_log_dir", lambda: tmp_path)

    def failing_write_log_line(filename, payload):
        raise TypeError("writer failure")

    monkeypatch.setattr("checklist.utils.logging_utils._write_log_line", failing_write_log_line)

    save_security_log("security_event", request=_build_authenticated_request(), context_uuid=uuid.uuid4())

    lines = (tmp_path / "logging_failures.jsonl").read_text(encoding="utf-8").strip().splitlines()
    payload = json.loads(lines[-1])

    assert payload["logger_error"] == "writer failure"
    assert payload["target_file"] == "api_security_events.jsonl"
    assert payload["original_payload"]["event"] == "security_event"
