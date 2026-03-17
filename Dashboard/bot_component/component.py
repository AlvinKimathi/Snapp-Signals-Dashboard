from pathlib import Path
import streamlit.components.v1 as components

_FRONTEND_DIR = Path(__file__).parent / "frontend"
_INDEX_FILE = _FRONTEND_DIR / "index.html"

print("SNAPP BOT FRONTEND DIR:", _FRONTEND_DIR.resolve())
print("SNAPP BOT INDEX EXISTS:", _INDEX_FILE.exists())

_snapp_bot_component = components.declare_component(
    "snapp_bot_overlay",
    path=str(_FRONTEND_DIR.resolve()),
)


def render_snapp_bot_component(
    *,
    messages,
    is_open,
    assistant_name="Snapp Bot",
    assistant_subtitle="Dashboard Assistant",
    input_placeholder="e.g. What does macro pressure mean?",
    key="snapp_bot_overlay",
):
    return _snapp_bot_component(
        messages=messages,
        is_open=is_open,
        assistant_name=assistant_name,
        assistant_subtitle=assistant_subtitle,
        input_placeholder=input_placeholder,
        default=None,
        key=key,
    )