import json
from types import SimpleNamespace
from uuid import uuid4

from checklist.utils.logging_utils import save_log, save_mobile_log, save_security_log


def test_save_log_serializes_non_json_types(tmp_path, settings):
    settings.BASE_DIR = tmp_path
    request = SimpleNamespace(
        path="/gerenciador/receive_work_orders_api/",
        method="POST",
        META={"REMOTE_ADDR": "127.0.0.1"},
        user=SimpleNamespace(is_authenticated=True, id=uuid4()),
    )

    save_log(RuntimeError("falha"), request=request)

    log_file = tmp_path / "logs" / "api_errors.jsonl"
    content = log_file.read_text(encoding="utf-8").strip()
    payload = json.loads(content)

    assert payload["ERROR_msg"] == "falha"
    assert isinstance(payload["user_id"], str)


def test_save_security_log_persists_extra_data(tmp_path, settings):
    settings.BASE_DIR = tmp_path

    save_security_log("throttled", ip_count=3)

    log_file = tmp_path / "logs" / "api_security_events.jsonl"
    payload = json.loads(log_file.read_text(encoding="utf-8").strip())

    assert payload["event"] == "throttled"
    assert payload["ip_count"] == 3


def test_save_mobile_log_keeps_return_shape_serializable(tmp_path, settings):
    settings.BASE_DIR = tmp_path
    log_entry = {
        "id": str(uuid4()),
        "status_sync": 0,
    }

    save_mobile_log(log_entry)

    log_file = tmp_path / "logs" / "mobile_app_logs.jsonl"
    payload = json.loads(log_file.read_text(encoding="utf-8").strip())

    assert payload["id"] == log_entry["id"]
    assert payload["status_sync"] == 0
