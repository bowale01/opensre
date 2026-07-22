"""Smoke test for the backward-compat re-export shim.

Guards against __all__ drift between the shim and the canonical module.
"""

from __future__ import annotations

import integrations.sentry.digest_delivery as shim
import platform.scheduler.delivery_readiness as canonical


def test_shim_all_matches_canonical_all() -> None:
    """The shim's __all__ must match the canonical module's __all__."""
    assert set(shim.__all__) == set(canonical.__all__)


def test_shim_re_exports_are_callable() -> None:
    """All re-exported symbols must be importable and callable from the shim."""
    for name in canonical.__all__:
        obj = getattr(shim, name)
        assert callable(obj), f"{name} is not callable via the shim"
