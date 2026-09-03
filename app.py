"""Ask Fabric Mastery — Streamlit chat UI (refreshed)."""
from __future__ import annotations

import base64
import logging
import os
import traceback
from pathlib import Path
from typing import Any

import streamlit as st

from src.chat_engine import (
    Source,
    ask,
    build_chat_engine,
    finalize_stream,
    refresh_sources_index,
    start_stream,
)
from src.config import get_settings
from src.i18n import t
from src.indexer import build_index, index_stats, load_index
from src.safety import (
    admin_mode_enabled,
    can_ask_question,
    check_rate_limit,
    free_questions_left,
    gate_enabled,
    is_unlocked,
    register_question,
    unlock_form,
)

NEWSLETTER_URL = "https://blog.antoinewang-tech.com/"
LOGO_PATH = Path(__file__).parent / "assets" / "logo_substack.webp"

# Only render Python tracebacks in the UI when explicitly enabled — otherwise
# they leak file paths, dependency versions and internal state to public users.
_DEBUG_TRACEBACK = os.getenv("DEBUG_TRACEBACK", "").strip().lower() in ("1", "true", "yes", "on")
log = logging.getLogger("app")


def _report_error(language: str, exc: Exception) -> None:
    """Log the full traceback server-side and show a sanitised error to the user."""
    log.exception("UI error: %s", exc)
    st.error(t(language, "error", err=str(exc)))
    if _DEBUG_TRACEBACK:
        with st.expander("Traceback"):
            st.code(traceback.format_exc())


@st.cache_data(show_spinner=False)
def _logo_data_uri() -> str | None:
    """Return the brand logo as a data URI, or None when the asset is missing."""
    if not LOGO_PATH.is_file():
        return None
    payload = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/webp;base64,{payload}"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

st.set_page_config(
    page_title="Fabric Mastery — Ask anything",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={"About": "Ask Fabric Mastery — Grounded RAG on the Fabric Mastery newsletter archive."},
)

# ---------------------------------------------------------------------------
# Visual identity
# ---------------------------------------------------------------------------
ACCENT = "#6750A4"

CUSTOM_CSS = f"""
<style>
@import url('https://rsms.me/inter/inter.css');

#MainMenu, header, footer {{visibility: hidden;}}
[data-testid="stToolbar"] {{display: none;}}
[data-testid="stDecoration"] {{display: none;}}

html, body, .stApp {{
    background: #FAFAF7;
    color: #1D1D1F;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    font-feature-settings: "ss01", "cv11", "cv02";
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

.block-container {{
    max-width: 820px;
    padding-top: 2.5rem;
    padding-bottom: 9rem;
}}

/* ---- top bar ---- */
.afm-topbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 1.75rem 0;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    gap: 1rem;
}}
.afm-brand {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    min-width: 0;
}}
.afm-logo {{
    width: 32px;
    height: 32px;
    border-radius: 8px;
    object-fit: cover;
    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    flex-shrink: 0;
}}
.afm-brand-text {{
    display: flex;
    flex-direction: column;
    line-height: 1.1;
    min-width: 0;
}}
.afm-brand-mark {{
    font-weight: 600;
    font-size: 1.05rem;
    letter-spacing: -0.012em;
    color: #1D1D1F;
}}
.afm-brand-sub {{
    font-size: 0.72rem;
    color: #6E6E73;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}}
.afm-cta {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.45rem 0.85rem;
    border-radius: 999px;
    background: {ACCENT};
    color: #ffffff !important;
    font-size: 0.82rem;
    font-weight: 500;
    text-decoration: none !important;
    transition: transform 120ms ease, box-shadow 120ms ease, opacity 120ms ease;
    white-space: nowrap;
    box-shadow: 0 1px 3px rgba(103,80,164,0.25);
}}
.afm-cta:hover {{
    opacity: 0.92;
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(103,80,164,0.28);
}}
.afm-cta-arrow {{
    font-size: 0.95rem;
    line-height: 1;
}}

/* ---- hero ---- */
.afm-hero {{
    text-align: center;
    margin: 4rem auto 2.25rem;
    max-width: 640px;
}}
.afm-hero h1 {{
    font-size: clamp(2.1rem, 4.5vw, 3rem);
    font-weight: 600;
    letter-spacing: -0.027em;
    line-height: 1.08;
    margin: 0 0 1rem;
    color: #1D1D1F;
}}
.afm-hero p {{
    font-size: 1.05rem;
    color: #6E6E73;
    margin: 0;
    line-height: 1.55;
}}

/* ---- example cards (buttons styled as cards) ---- */
.afm-cards {{
    margin: 2.5rem auto 0;
}}
.afm-cards-label {{
    text-align: center;
    color: #86868B;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
}}
[data-testid="stButton"] > button {{
    background: white;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 14px;
    padding: 1rem 1.15rem;
    text-align: left;
    transition: all 0.18s ease;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    color: #1D1D1F;
    height: auto;
    min-height: 92px;
    white-space: normal;
    line-height: 1.4;
    font-weight: 400;
}}
[data-testid="stButton"] > button:hover {{
    border-color: rgba(103,80,164,0.45);
    box-shadow: 0 4px 14px rgba(103,80,164,0.08);
    transform: translateY(-1px);
    color: #1D1D1F;
}}
[data-testid="stButton"] > button:active,
[data-testid="stButton"] > button:focus {{
    color: #1D1D1F !important;
    background: white !important;
}}

/* ---- chat messages ---- */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    border: none !important;
    padding: 0.6rem 0 1.2rem;
}}
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {{
    background: transparent;
}}
[data-testid="stChatMessageAvatarUser"] + div p,
[data-testid="stChatMessageAvatarAssistant"] + div p {{
    color: #1D1D1F;
}}

/* user bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    display: flex;
    flex-direction: row-reverse;
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {{
    background: white !important;
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1.05rem !important;
    max-width: 80%;
}}

/* assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {{
    padding: 0.25rem 0 !important;
}}

/* ---- chat input ---- */
[data-testid="stChatInput"] {{
    background: white;
    border: 1px solid rgba(0,0,0,0.1) !important;
    border-radius: 24px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 8px 28px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
    margin: 0 auto;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: {ACCENT} !important;
    box-shadow: 0 1px 3px rgba(103,80,164,0.08), 0 8px 28px rgba(103,80,164,0.14);
}}
[data-testid="stChatInput"] textarea {{
    font-size: 1rem !important;
    color: #1D1D1F !important;
}}

/* ---- sources block ---- */
.afm-sources {{
    margin-top: 0.75rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(0,0,0,0.06);
}}
.afm-sources-label {{
    color: #86868B;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
    margin-bottom: 0.75rem;
}}
.afm-source-card {{
    display: block;
    background: white;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.5rem;
    text-decoration: none !important;
    color: inherit !important;
    transition: all 0.15s ease;
}}
.afm-source-card:hover {{
    border-color: rgba(103,80,164,0.4);
    background: #FBFAFC;
    transform: translateY(-1px);
}}
.afm-source-title {{
    font-size: 0.92rem;
    font-weight: 500;
    color: #1D1D1F;
    line-height: 1.35;
    margin-bottom: 0.2rem;
}}
.afm-source-meta {{
    font-size: 0.78rem;
    color: #86868B;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.afm-source-meta .afm-dot {{ opacity: 0.4; }}
.afm-source-snippet {{
    font-size: 0.85rem;
    color: #6E6E73;
    margin-top: 0.5rem;
    line-height: 1.45;
    border-left: 2px solid rgba(0,0,0,0.08);
    padding-left: 0.65rem;
}}

/* ---- limitation / cannot-answer ---- */
.afm-limitation {{
    background: rgba(0,0,0,0.03);
    border-left: 3px solid #C6C6C8;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    color: #6E6E73;
    font-size: 0.95rem;
    line-height: 1.5;
}}

/* ---- sidebar refinement ---- */
section[data-testid="stSidebar"] {{
    background: #F2F2EF;
    border-right: 1px solid rgba(0,0,0,0.06);
}}
section[data-testid="stSidebar"] [data-testid="stButton"] > button {{
    background: white;
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    min-height: 0;
    padding: 0.55rem 0.85rem;
    font-size: 0.92rem;
    box-shadow: none;
}}
section[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {{
    border-color: {ACCENT};
}}
section[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: #1D1D1F !important;
}}

/* ---- footer ---- */
.afm-footer {{
    text-align: center;
    color: #86868B;
    font-size: 0.78rem;
    margin: 4rem auto 0;
    padding: 1rem;
    letter-spacing: 0.01em;
}}

/* ---- confidence badge ---- */
.afm-confidence {{
    display: inline-flex;
    align-items: center;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 0 0 0.7rem 0;
    letter-spacing: 0.005em;
}}
.afm-confidence-high {{ background: rgba(34,197,94,0.12); color: #15803D; }}
.afm-confidence-medium {{ background: rgba(234,179,8,0.15); color: #854D0E; }}
.afm-confidence-low {{ background: rgba(239,68,68,0.10); color: #B91C1C; }}

/* ---- freemium demo badge + unlock panel ---- */
.afm-demo-wrap {{
    text-align: center;
    margin: 1.5rem auto 0.5rem;
}}
.afm-demo-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    background: rgba(103,80,164,0.10);
    color: #4A3B7A;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.005em;
}}
.afm-unlock-title {{
    font-size: 1.15rem;
    font-weight: 600;
    letter-spacing: -0.012em;
    color: #1D1D1F;
    margin: 0.25rem 0 0.5rem;
}}
.afm-unlock-text {{
    font-size: 0.93rem;
    color: #6E6E73;
    line-height: 1.5;
    margin: 0 0 1rem;
}}

/* ---- new-conversation bar ---- */
.afm-newconv-label {{
    text-align: right;
    font-size: 0.85rem;
    color: #6E6E73;
    padding-top: 0.55rem;
    padding-right: 0.4rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* spinner color */
[data-testid="stSpinner"] {{ color: {ACCENT} !important; }}

/* expanders */
[data-testid="stExpander"] {{
    border: 1px solid rgba(0,0,0,0.07) !important;
    border-radius: 12px !important;
    background: white !important;
}}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
def _init_state() -> None:
    s = get_settings()
    st.session_state.setdefault("language", s.default_language)
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("engine", None)
    st.session_state.setdefault("engine_language", None)
    st.session_state.setdefault("pending_question", None)


def _reset_engine() -> None:
    st.session_state["engine"] = None
    st.session_state["engine_language"] = None


def _get_engine(language: str) -> Any | None:
    if (
        st.session_state["engine"] is not None
        and st.session_state["engine_language"] == language
    ):
        return st.session_state["engine"]
    index = load_index()
    if index is None:
        return None
    engine = build_chat_engine(index, language=language)
    st.session_state["engine"] = engine
    st.session_state["engine_language"] = language
    return engine


def _stats_count() -> int:
    try:
        return int(index_stats().get("chunks") or 0)
    except Exception:  # noqa: BLE001
        return 0


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def _topbar(language: str) -> None:
    logo_uri = _logo_data_uri()
    if logo_uri:
        logo_html = (
            f'<img class="afm-logo" src="{logo_uri}" '
            f'alt="{t(language, "brand")}" />'
        )
    else:
        logo_html = '<span class="afm-logo" aria-hidden="true">📘</span>'

    st.markdown(
        f'<div class="afm-topbar">'
        f'<div class="afm-brand">'
        f'{logo_html}'
        f'<span class="afm-brand-text">'
        f'<span class="afm-brand-mark">{t(language, "brand")}</span>'
        f'<span class="afm-brand-sub">{t(language, "subbrand")}</span>'
        f'</span>'
        f'</div>'
        f'<a class="afm-cta" href="{NEWSLETTER_URL}" target="_blank" rel="noopener">'
        f'{t(language, "visit_newsletter")}'
        f'<span class="afm-cta-arrow">→</span>'
        f'</a>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _hero(language: str, n_sources: int) -> None:
    subtitle = (
        t(language, "hero_subtitle", n=n_sources)
        if n_sources
        else t(language, "hero_subtitle_empty")
    )
    st.markdown(
        f'<div class="afm-hero">'
        f'<h1>{t(language, "hero_title")}</h1>'
        f'<p>{subtitle}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _example_cards(language: str) -> None:
    """Render four prompt cards. On click, queue the prompt and rerun so
    the welcome screen disappears atomically instead of lingering for a frame.
    """
    examples = [
        ("🛡️", t(language, "ex_lakehouse_title"), t(language, "ex_lakehouse_prompt")),
        ("🏛️", t(language, "ex_agent_title"), t(language, "ex_agent_prompt")),
        ("📥", t(language, "ex_ingestion_title"), t(language, "ex_ingestion_prompt")),
        ("⚡", t(language, "ex_capacity_title"), t(language, "ex_capacity_prompt")),
    ]

    cols = st.columns(2, gap="medium")
    for i, (icon, title, prompt) in enumerate(examples):
        with cols[i % 2]:
            label = f"{icon}  **{title}**\n\n{prompt}"
            if st.button(label, key=f"example_{i}", use_container_width=True):
                st.session_state["pending_question"] = prompt
                st.rerun()


def _render_sources(sources: list[dict], language: str) -> None:
    if not sources:
        return
    cards = []
    for src in sources:
        title = src.get("title") or src["file_name"]
        url = src.get("url")
        date = src.get("date") or ""
        score = src.get("score")
        snippet = (src.get("snippet") or "").strip()

        meta_parts: list[str] = []
        if date:
            meta_parts.append(date)
        if score is not None:
            meta_parts.append(f"{t(language, 'score')}: {score:.2f}")
        meta_html = ' <span class="afm-dot">·</span> '.join(meta_parts)

        snippet_html = (
            f'<div class="afm-source-snippet">{_html_escape(snippet)}…</div>'
            if snippet else ""
        )
        # Only allow http(s) URLs; HTML-escape to neutralise any malformed input.
        if url and url.lower().startswith(("https://", "http://")):
            open_attrs = f'href="{_html_escape(url)}" target="_blank" rel="noopener noreferrer"'
        else:
            open_attrs = 'role="link" aria-disabled="true"'

        cards.append(
            f'<a class="afm-source-card" {open_attrs}>'
            f'<div class="afm-source-title">{_html_escape(title)}</div>'
            f'<div class="afm-source-meta">{meta_html}</div>'
            f'{snippet_html}'
            f'</a>'
        )
    st.markdown(
        f'<div class="afm-sources">'
        f'<div class="afm-sources-label">📚 {t(language, "sources")} · {len(sources)}</div>'
        f'{"".join(cards)}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _render_confidence(confidence: str | None, language: str) -> None:
    level = confidence if confidence in {"high", "medium", "low"} else "medium"
    label = t(language, f"confidence_{level}")
    st.markdown(
        f'<div class="afm-confidence afm-confidence-{level}">{label}</div>',
        unsafe_allow_html=True,
    )


def _demo_notice(language: str) -> None:
    """Show the remaining free questions while the visitor is still in demo mode."""
    if not gate_enabled() or is_unlocked():
        return
    left = free_questions_left()
    if left <= 0:
        return
    st.markdown(
        f'<div class="afm-demo-wrap">'
        f'<span class="afm-demo-badge">\u2728 {t(language, "demo_badge", n=left)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _unlock_panel(language: str) -> None:
    """Conversion step rendered once the free demo questions are used up."""
    with st.container(border=True):
        st.markdown(
            f'<div class="afm-unlock-title">{t(language, "auth_title")}</div>'
            f'<p class="afm-unlock-text">{t(language, "auth_subtitle")}</p>',
            unsafe_allow_html=True,
        )
        if unlock_form(language, key="afm-unlock-form"):
            st.rerun()
        st.markdown(
            f'<div class="afm-demo-wrap">'
            f'<a class="afm-cta" href="{NEWSLETTER_URL}" target="_blank" rel="noopener">'
            f'{t(language, "unlock_cta")}'
            f'<span class="afm-cta-arrow">\u2192</span>'
            f'</a>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_message(msg: dict, language: str) -> None:
    role = msg["role"]
    avatar = "🧑" if role == "user" else "📘"
    with st.chat_message(role, avatar=avatar):
        content = msg["content"]
        cannot = t(language, "cannot_answer")
        if role == "assistant":
            _render_confidence(msg.get("confidence"), language)
        if role == "assistant" and content.strip().startswith(cannot.split(".")[0]):
            st.markdown(f'<div class="afm-limitation">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(content)
        if role == "assistant":
            _render_sources(msg.get("sources", []), language)


def _sources_dict(sources: list[Source]) -> list[dict]:
    return [
        {
            "file_name": s.file_name,
            "title": s.title,
            "url": s.url,
            "date": s.date,
            "page": s.page,
            "score": s.score,
            "snippet": s.snippet,
        }
        for s in sources
    ]


def _sidebar(language: str) -> str:
    with st.sidebar:
        st.markdown(f"#### ⚙️  {t(language, 'settings')}")

        new_lang = st.radio(
            t(language, "language"),
            options=["fr", "en"],
            index=0 if language.startswith("fr") else 1,
            horizontal=True,
            format_func=lambda x: "Français" if x == "fr" else "English",
        )
        if new_lang != language:
            st.session_state["language"] = new_lang
            _reset_engine()
            st.rerun()

        st.divider()
        st.markdown(f"#### 📚  {t(language, 'index')}")

        stats = index_stats()
        chunks = int(stats.get("chunks", 0) or 0)
        st.metric(t(language, "index_chunks"), chunks)

        # Re-embedding the whole corpus costs AOAI tokens, so the control is
        # opt-in per deployment and never reachable from the public app.
        if admin_mode_enabled():
            rebuild = chunks > 0
            label = t(language, "rebuild_index") if rebuild else t(language, "build_index")
            if st.button(label, use_container_width=True, type="primary"):
                with st.spinner(t(language, "indexing")):
                    try:
                        report = build_index(rebuild=rebuild)
                    except Exception as exc:  # noqa: BLE001 — UI boundary
                        _report_error(language, exc)
                    else:
                        if report.files_indexed == 0:
                            st.warning(t(language, "no_files", dir=get_settings().data_dir))
                        else:
                            st.success(
                                t(
                                    language,
                                    "index_built",
                                    files=report.files_indexed,
                                    chunks=report.nodes_created,
                                )
                            )
                        refresh_sources_index()
                        _reset_engine()
                        st.rerun()

        if st.button(f"🗑  {t(language, 'clear_chat')}", use_container_width=True):
            st.session_state["messages"] = []
            _reset_engine()
            st.rerun()

        if admin_mode_enabled():
            st.divider()
            with st.expander("Details", expanded=False):
                st.caption(f"**{t(language, 'data_dir')}**")
                st.code(str(stats["data_dir"]), language="text")
                st.caption(f"**{t(language, 'collection')}**: `{stats['collection']}`")

    return st.session_state["language"]


def _new_conversation_bar(language: str) -> None:
    """Right-aligned label + tiny refresh button that wipes history + memory."""
    _, label_col, btn_col = st.columns([9, 2.5, 0.7])
    with label_col:
        st.markdown(
            f'<div class="afm-newconv-label">{t(language, "new_conversation")}</div>',
            unsafe_allow_html=True,
        )
    with btn_col:
        if st.button(
            "↻",
            key="afm-new-conv",
            help=t(language, "new_conversation"),
            use_container_width=True,
        ):
            st.session_state["messages"] = []
            _reset_engine()
            st.rerun()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    _init_state()

    try:
        get_settings()
    except Exception as exc:  # noqa: BLE001 — UI boundary
        lang = st.session_state.get("language", "fr")
        st.error(t(lang, "config_error", err=str(exc)))
        st.info(t(lang, "config_hint"))
        return

    language = _sidebar(st.session_state["language"])
    _topbar(language)

    engine = _get_engine(language)
    n_sources = _stats_count()

    # Freemium funnel: the demo runs code-free, the full experience needs the
    # reader code published in the newsletter.
    locked = not can_ask_question()

    # Read inputs first so the welcome screen only shows when there is genuinely
    # no history AND no prompt about to be processed this frame (typed input,
    # queued example-card click, or replayed pending question).
    typed_prompt = st.chat_input(
        t(language, "unlock_placeholder" if locked else "ask_placeholder"),
        disabled=locked,
    )
    queued_prompt = st.session_state.pop("pending_question", None)
    incoming_prompt = None if locked else (typed_prompt or queued_prompt)
    has_history = bool(st.session_state["messages"])
    starting_conversation = has_history or bool(incoming_prompt)

    if not starting_conversation:
        _hero(language, n_sources)
        if engine is None:
            st.info(t(language, "no_index"))
        elif not locked:
            _example_cards(language)
    else:
        _new_conversation_bar(language)

    # Replay history
    for msg in st.session_state["messages"]:
        _render_message(msg, language)

    if not incoming_prompt:
        if locked:
            _unlock_panel(language)
        else:
            _demo_notice(language)
        if not starting_conversation:
            st.markdown(
                f'<div class="afm-footer">{t(language, "footer")}</div>',
                unsafe_allow_html=True,
            )
        return

    prompt = incoming_prompt

    # Per-session sliding-window rate limit (caps AOAI token spend per visitor).
    allowed, _retry = check_rate_limit(language)
    if not allowed:
        return

    register_question()

    # Append + render user message
    user_msg = {"role": "user", "content": prompt}
    st.session_state["messages"].append(user_msg)
    _render_message(user_msg, language)

    if engine is None:
        engine = _get_engine(language)
    if engine is None:
        st.warning(t(language, "no_index"))
        return

    with st.chat_message("assistant", avatar="📘"):
        confidence_slot = st.empty()
        answer_slot = st.empty()
        try:
            with st.spinner(t(language, "thinking")):
                token_gen, response, prebuilt_turn = start_stream(
                    engine, prompt, language=language,
                )
            # Manual iteration + placeholder.markdown() is what actually streams;
            # st.write_stream() nested inside an st.empty().container() buffers
            # every update and reveals the whole answer at once.
            streamed_answer = ""
            for chunk in token_gen:
                streamed_answer += chunk
                answer_slot.markdown(streamed_answer + " ▌")
            answer_slot.markdown(streamed_answer)
        except Exception as exc:  # noqa: BLE001 — UI boundary
            _report_error(language, exc)
            st.session_state["messages"].append(
                {"role": "assistant", "content": t(language, "error", err=str(exc)), "sources": [], "confidence": "low"}
            )
            return

        turn = prebuilt_turn or finalize_stream(response, streamed_answer or "", language)

        with confidence_slot.container():
            _render_confidence(turn.confidence, language)

        # finalize_stream may swap the streamed body for the canonical refusal
        # (empty retrieval, empty response, etc.) — reflect that verdict in-place.
        if (streamed_answer or "").strip() != turn.answer.strip():
            answer_slot.empty()
            with answer_slot.container():
                cannot = t(language, "cannot_answer")
                if turn.answer.strip().startswith(cannot.split(".")[0]):
                    st.markdown(
                        f'<div class="afm-limitation">{turn.answer}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(turn.answer)

        sources_payload = _sources_dict(turn.sources)
        _render_sources(sources_payload, language)

    st.session_state["messages"].append(
        {"role": "assistant", "content": turn.answer, "sources": sources_payload, "confidence": turn.confidence}
    )

    # Surface the unlock step right after the answer that consumed the last
    # free question — the moment the visitor has just seen the value.
    if can_ask_question():
        _demo_notice(language)
    else:
        _unlock_panel(language)


if __name__ == "__main__":
    main()
