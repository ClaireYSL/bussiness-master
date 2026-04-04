from __future__ import annotations

import os
from typing import Any


def send_summary(message: str, *, recipient: str | None = None) -> dict[str, Any]:
    webhook = os.getenv("FEISHU_WEBHOOK_URL") or os.getenv("FEISHU_WEBHOOK")
    if not webhook:
        return {
            "provider": "feishu",
            "ok": True,
            "status": "skipped",
            "reason": "not_configured",
            "recipient": recipient,
        }

    return {
        "provider": "feishu",
        "ok": True,
        "status": "placeholder",
        "reason": "configured_but_not_sent",
        "recipient": recipient,
        "message_length": len(message),
    }
