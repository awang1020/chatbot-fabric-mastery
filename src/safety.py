"""Lightweight in-process safety controls for the public RAG UI.

Three layers are exposed:

1. **Freemium access gate** — every visitor gets ``FREE_QUESTIONS`` demo
   questions, then must enter the shared code published in the newsletter.
   When ``APP_PASSWORD`` is unset the gate is dormant and the app is fully
   open (local development). This is intentionally *not* per-user auth: it
   is a conversion step plus a cheap anti-bot layer for a newsletter audience.

2. ``check_rate_limit`` — session-scoped sliding-window rate limiter.
   Caps how many questions a single Streamlit session can ask in a window,
   protecting AOAI token spend against a tab left open with auto-refresh
   or a curious user mashing the example cards.

3. ``admin_mode_enabled`` — keeps index-management controls hidden unless the
   deployment opts in, so a public visitor can never trigger a re-embed of
   the whole corpus.

State lives in ``st.session_state``, so it resets in a fresh browser session:
the demo quota is a conversion nudge, not a hard security boundary. The AOAI
TPM cap and the Azure budget remain the actual ceiling on spend.
"""
from __future__ import annotations

import os
import secrets
import time
from dataclasses import dataclass

import streamlit as st

from src.i18n import t


_PASSWORD_KEY = "_auth_ok"
_RATE_KEY = "_question_timestamps"
_FREE_USED_KEY = "_free_questions_used"

DEFAULT_FREE_QUESTIONS = 2


@dataclass(frozen=True)
class RateLimit:
    max_questions: int
    window_seconds: int


def _expected_password() -> str | None:
    pwd = os.getenv("APP_PASSWORD", "").strip()
    return pwd or None


def _free_quota() -> int:
    raw = os.getenv("FREE_QUESTIONS", "").strip()
    if not raw:
        return DEFAULT_FREE_QUESTIONS
    try:
        return max(0, int(raw))
    except ValueError:
        return DEFAULT_FREE_QUESTIONS


def admin_mode_enabled() -> bool:
    """True when index-management controls may be rendered. Never in production."""
    return os.getenv("ADMIN_MODE", "").strip().lower() in ("1", "true", "yes", "on")


def gate_enabled() -> bool:
    """True when this deployment publishes an access code in the newsletter."""
    return _expected_password() is not None


def is_unlocked() -> bool:
    """True when the visitor has the full experience (no gate, or valid code)."""
    if not gate_enabled():
        return True
    return st.session_state.get(_PASSWORD_KEY) is True


def free_questions_left() -> int:
    """Demo questions still available before the newsletter code is required."""
    if is_unlocked():
        return 0
    used = int(st.session_state.get(_FREE_USED_KEY, 0) or 0)
    return max(0, _free_quota() - used)


def can_ask_question() -> bool:
    return is_unlocked() or free_questions_left() > 0


def register_question() -> None:
    """Consume one demo question; no-op once the visitor has unlocked."""
    if is_unlocked():
        return
    st.session_state[_FREE_USED_KEY] = int(st.session_state.get(_FREE_USED_KEY, 0) or 0) + 1


def unlock_form(language: str, *, key: str) -> bool:
    """Render the access-code form. Returns True when it just unlocked."""
    expected = _expected_password()
    if expected is None:
        return False

    with st.form(key, clear_on_submit=False):
        pwd = st.text_input(
            t(language, "auth_password_label"),
            type="password",
            autocomplete="current-password",
        )
        submitted = st.form_submit_button(
            t(language, "auth_submit"), use_container_width=True
        )

    if not submitted:
        return False
    # Constant-time compare — avoid trivial timing oracles.
    if secrets.compare_digest(pwd, expected):
        st.session_state[_PASSWORD_KEY] = True
        return True
    st.error(t(language, "auth_invalid"))
    return False


def _rate_limit_config() -> RateLimit:
    return RateLimit(
        max_questions=int(os.getenv("RATE_LIMIT_MAX_QUESTIONS", "20") or 20),
        window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "900") or 900),
    )


def check_rate_limit(language: str) -> tuple[bool, int]:
    """Return ``(allowed, retry_after_seconds)``.

    The caller should drop the question and surface the message to the
    user when ``allowed`` is False. Each successful call records the
    current timestamp.
    """
    cfg = _rate_limit_config()
    now = time.time()
    history: list[float] = st.session_state.setdefault(_RATE_KEY, [])
    cutoff = now - cfg.window_seconds
    history[:] = [ts for ts in history if ts >= cutoff]
    if len(history) >= cfg.max_questions:
        retry = int(cfg.window_seconds - (now - history[0])) + 1
        st.warning(
            t(
                language,
                "rate_limited",
                n=cfg.max_questions,
                window_min=cfg.window_seconds // 60,
                retry=retry,
            )
        )
        return False, retry
    history.append(now)
    return True, 0
