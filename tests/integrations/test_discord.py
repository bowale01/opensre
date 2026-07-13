from __future__ import annotations

import sys
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

from integrations.discord.verifier import verify_discord


class _FakeIntents:
    def __init__(self) -> None:
        self.guilds = False

    @classmethod
    def none(cls) -> _FakeIntents:
        return cls()


def _install_fake_discord(
    monkeypatch: Any,
    *,
    run_error_factory: Callable[[type[Exception]], Exception] | None = None,
) -> list[str]:
    tokens: list[str] = []

    class LoginFailure(Exception):
        pass

    class Client:
        def __init__(self, *, intents: _FakeIntents) -> None:
            assert intents.guilds is True

        def run(self, token: str) -> None:
            tokens.append(token)
            if run_error_factory is not None:
                raise run_error_factory(LoginFailure)

    fake_discord = SimpleNamespace(
        Intents=_FakeIntents,
        Client=Client,
        LoginFailure=LoginFailure,
    )
    monkeypatch.setitem(sys.modules, "discord", fake_discord)
    return tokens


def test_verify_discord_missing_bot_token(monkeypatch: Any) -> None:
    _install_fake_discord(monkeypatch)

    result = verify_discord("local env", {})

    assert result["status"] == "missing"
    assert "bot_token" in result["detail"]


def test_verify_discord_reports_login_failure(monkeypatch: Any) -> None:
    _install_fake_discord(
        monkeypatch,
        run_error_factory=lambda login_failure_cls: login_failure_cls("bad token"),
    )

    result = verify_discord("local env", {"bot_token": "bad-token"})

    assert result["status"] == "failed"
    assert "Discord login failed" in result["detail"]


def test_verify_discord_reports_api_failure(monkeypatch: Any) -> None:
    _install_fake_discord(
        monkeypatch,
        run_error_factory=lambda _login_failure_cls: RuntimeError("gateway unavailable"),
    )

    result = verify_discord("local env", {"bot_token": "token"})

    assert result["status"] == "failed"
    assert "gateway unavailable" in result["detail"]


def test_verify_discord_accepts_running_event_loop_success(monkeypatch: Any) -> None:
    _install_fake_discord(
        monkeypatch,
        run_error_factory=lambda _login_failure_cls: RuntimeError(
            "run() cannot be called from a running event loop"
        ),
    )

    result = verify_discord("local env", {"bot_token": "token"})

    assert result["status"] == "passed"
    assert "Discord bot token accepted" in result["detail"]


def test_verify_discord_accepts_token_when_client_run_succeeds(monkeypatch: Any) -> None:
    tokens = _install_fake_discord(monkeypatch)

    result = verify_discord("local env", {"bot_token": " token "})

    assert tokens == ["token"]
    assert result["status"] == "passed"


def test_classify_validation_error_returns_none_and_reports(monkeypatch: Any) -> None:
    """SM-18: ValidationError in Discord classify() returns (None, None) and
    reports a sanitized error (no secret field values) via report_classify_failure."""
    from unittest.mock import patch

    from pydantic import ValidationError

    from integrations.discord import classify

    # Force model_validate to raise ValidationError
    def _raise_validation_error(*args: Any, **kwargs: Any) -> None:
        raise ValidationError.from_exception_data(
            title="DiscordBotConfig",
            line_errors=[],
        )

    monkeypatch.setattr(
        "integrations.discord.DiscordBotConfig.model_validate",
        _raise_validation_error,
    )

    with patch("integrations.discord.report_classify_failure") as mock_report:
        result = classify({"bot_token": "some-token"}, record_id="rec-discord")

    assert result == (None, None)
    assert mock_report.call_count == 1
    exc_arg = mock_report.call_args.args[0]
    # Must be the safe wrapper, not the raw ValidationError
    assert isinstance(exc_arg, ValueError)
    assert "DiscordBotConfig validation failed" in str(exc_arg)
