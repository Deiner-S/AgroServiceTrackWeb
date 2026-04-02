import json
import traceback
import uuid
from datetime import date, datetime
from pathlib import Path

from django.conf import settings
from django.utils import timezone


class LogPersistenceError(RuntimeError):
    pass


def _get_log_dir():
    log_dir = Path(settings.BASE_DIR) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _serialize_for_log(value):
    if isinstance(value, uuid.UUID):
        return str(value)

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {str(key): _serialize_for_log(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_serialize_for_log(item) for item in value]

    if isinstance(value, BaseException):
        return {
            "type": value.__class__.__name__,
            "message": str(value),
        }

    return value


def _resolve_stacktrace(error):
    if isinstance(error, BaseException):
        if error.__traceback__ is not None:
            return "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
        return "".join(traceback.format_exception_only(type(error), error))

    formatted = traceback.format_exc()
    return "" if formatted == "NoneType: None\n" else formatted


def _build_request_metadata(request):
    if request is None:
        return {}

    user_id = None
    if getattr(request, "user", None) is not None and getattr(
        request.user, "is_authenticated", False
    ):
        user_id = str(request.user.id)

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


def _write_log_line(filename, payload):
    serialized_payload = _serialize_for_log(payload)

    with open(_get_log_dir() / filename, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(serialized_payload, ensure_ascii=False) + "\n")


def _write_logger_failure(filename, error, payload):
    fallback_payload = {
        "timestamp": timezone.now().isoformat(),
        "logger_error": str(error),
        "logger_stacktrace": _resolve_stacktrace(error),
        "target_file": filename,
        "original_payload": _serialize_for_log(payload),
    }

    with open(_get_log_dir() / "logging_failures.jsonl", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(fallback_payload, ensure_ascii=False) + "\n")


def _safe_write_log(filename, payload, raise_on_failure=False):
    try:
        _write_log_line(filename, payload)
        return True
    except Exception as log_error:
        try:
            _write_logger_failure(filename, log_error, payload)
        except Exception:
            # Falhas no logger nunca devem subir para o console nem interromper o fluxo principal.
            pass
        if raise_on_failure:
            raise LogPersistenceError(f"Falha ao persistir log em {filename}") from log_error
        return False


def save_log(error, request=None):
    log_data = {
        "timestamp": timezone.now().isoformat(),
        "error_message": str(error),
        "error_type": error.__class__.__name__ if isinstance(error, BaseException) else type(error).__name__,
        "stacktrace": _resolve_stacktrace(error),
    }

    log_data.update(_build_request_metadata(request))
    _safe_write_log("api_errors.jsonl", log_data)


def save_security_log(event, request=None, **extra_data):
    log_data = {
        "timestamp": timezone.now().isoformat(),
        "event": event,
    }
    log_data.update(_build_request_metadata(request))
    log_data.update(extra_data)
    _safe_write_log("api_security_events.jsonl", log_data)


def save_mobile_log(log_entry, request=None):
    log_data = {
        "received_at": timezone.now().isoformat(),
        **log_entry,
    }
    log_data.update(_build_request_metadata(request))
    return _safe_write_log("mobile_app_logs.jsonl", log_data, raise_on_failure=True)
