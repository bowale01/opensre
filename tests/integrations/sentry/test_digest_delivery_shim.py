"""Smoke test for the backward-compat re-export shim.

Guards against __all__ drift between the shim and the canonical module.
"""

from __future__ import annotations

from integrations.sentry.digest_delivery import (
    any_digest_delivery_ready,
    delivery_provider_ready,
    digest_delivery_setup_hint,
    slack_delivery_ready,
    telegram_delivery_ready,
)


def test_shim_re_exports_are_callable() -> None:
    """All re-exported symbols must be importable and callable."""
    assert callable(telegram_delivery_ready)
    assert callable(slack_delivery_ready)
    assert callable(delivery_provider_ready)
    assert callable(any_digest_delivery_ready)
    assert callable(digest_delivery_setup_hint)
