import json
from pathlib import Path
import traceback

from django.conf import settings
from django.utils import timezone


def _get_log_dir():
    log_dir = Path(settings.BASE_DIR) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _get_request_metadata(request):
    if request is None:
        return {}

    user_id = None
    if getattr(request, "user", None) is not None and getattr(
        request.user, "is_authenticated", False
    ):
        user_id = request.user.id

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    client_ip = (
        forwarded_for.split(",")[0].strip()
        if forwarded_for
        else request.META.get("REMOTE_ADDR")
    )

    return {
        "user_id": user_id,
        "path": request.path,
        "method": request.method,
        "client_ip": client_ip,
        "user_agent": request.META.get("HTTP_USER_AGENT"),
    }


def save_log(error, request=None):
    log_data = {
        "timestamp": timezone.now().isoformat(),
        "ERROR_msg": str(error),
        "stacktrace": traceback.format_exc(),
    }

    log_data.update(_get_request_metadata(request))

    with open(_get_log_dir() / "api_errors.jsonl", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_data, ensure_ascii=False, default=str) + "\n")


def save_security_log(event, request=None, **extra_data):
    log_data = {
        "timestamp": timezone.now().isoformat(),
        "event": event,
    }
    log_data.update(_get_request_metadata(request))
    log_data.update(extra_data)

    with open(_get_log_dir() / "api_security_events.jsonl", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_data, ensure_ascii=False, default=str) + "\n")


def save_mobile_log(log_entry, request=None):
    log_data = {
        "received_at": timezone.now().isoformat(),
        **log_entry,
    }
    log_data.update(_get_request_metadata(request))

    with open(_get_log_dir() / "mobile_app_logs.jsonl", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_data, ensure_ascii=False, default=str) + "\n")
