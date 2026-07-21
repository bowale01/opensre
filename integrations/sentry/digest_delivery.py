"""Delivery readiness checks for scheduled Sentry digest tasks.

Backward-compatibility shim — the canonical implementation now lives in
``platform.scheduler.delivery_readiness``. This re-export ensures existing
consumers that import from this path continue to work without modification.
"""

from __future__ import annotations

from platform.scheduler.delivery_readiness import (
    any_digest_delivery_ready,
    delivery_provider_ready,
    digest_delivery_setup_hint,
    slack_delivery_ready,
    telegram_delivery_ready,
)

__all__ = [
    "any_digest_delivery_ready",
    "delivery_provider_ready",
    "digest_delivery_setup_hint",
    "slack_delivery_ready",
    "telegram_delivery_ready",
]
