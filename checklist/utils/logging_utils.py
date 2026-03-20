import json
from pathlib import Path
import traceback

from django.conf import settings
from django.utils import timezone


def save_log(error, request=None):
    log_dir = Path(settings.BASE_DIR) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    user_id = None
    if request is not None and getattr(request, "user", None) is not None:
        if getattr(request.user, "is_authenticated", False):
            user_id = request.user.id

    log_data = {
        "user_id": user_id,
        "timestamp": timezone.now().isoformat(),
        "ERROR_msg": str(error),
        "stacktrace": traceback.format_exc(),
    }

    if request is not None:
        log_data["path"] = request.path
        log_data["method"] = request.method

    with open(log_dir / "api_errors.jsonl", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_data, ensure_ascii=False) + "\n")
