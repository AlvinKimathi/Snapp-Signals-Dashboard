from __future__ import annotations

import streamlit as st
from snapp_bot_component.snapp_bot_component import snapp_bot_component


def inject_snapp_bot_css():
    st.markdown(
        """
        <style>
        div[data-testid="stCustomComponentV2"]:has(div[id="snapp-bot-root"]),
        div[data-testid="stCustomComponentV2"]:has(#snapp-bot-root),
        .st-key-snapp_bot_dashboard_component {
            position: relative !important;
            width: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
            background: transparent !important;
            border: 0 !important;
        }

        .st-key-snapp_bot_dashboard_component > div,
        .st-key-snapp_bot_dashboard_component [data-testid="stCustomComponentV2"],
        .st-key-snapp_bot_dashboard_component iframe,
        .st-key-snapp_bot_dashboard_component [data-testid="stCustomComponentV2"] > div {
            width: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            overflow: visible !important;
            background: transparent !important;
            border: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_bot_state():
    if "snapp_bot_open" not in st.session_state:
        st.session_state["snapp_bot_open"] = False

    if "snapp_bot_messages" not in st.session_state:
        st.session_state["snapp_bot_messages"] = [
            {"role": "assistant", "content": "Hey There, Ask me anything?"}
        ]

    if "snapp_bot_last_event_id" not in st.session_state:
        st.session_state["snapp_bot_last_event_id"] = None

    if "snapp_bot_loading" not in st.session_state:
        st.session_state["snapp_bot_loading"] = False

    if "snapp_bot_pending_question" not in st.session_state:
        st.session_state["snapp_bot_pending_question"] = None


def render_launcher():
    return


def render_panel(answer_fn, dashboard_context: dict):
    display_messages = list(st.session_state["snapp_bot_messages"])

    result = snapp_bot_component(
        is_open=st.session_state["snapp_bot_open"],
        assistant_name="Snapp Bot",
        assistant_subtitle="Dashboard Assistant",
        input_placeholder="e.g. What does macro pressure mean?",
        messages=display_messages,
        key="snapp_bot_dashboard_component",
    )

    event = getattr(result, "event", None)

    if not event:
        return

    event_id = event.get("event_id")
    if event_id == st.session_state.get("snapp_bot_last_event_id"):
        return

    st.session_state["snapp_bot_last_event_id"] = event_id
    event_type = event.get("type")

    if event_type == "toggle":
        st.session_state["snapp_bot_open"] = not st.session_state["snapp_bot_open"]
        st.rerun()

    elif event_type == "close":
        st.session_state["snapp_bot_open"] = False
        st.rerun()

    elif event_type == "clear":
        st.session_state["snapp_bot_messages"] = [
            {"role": "assistant", "content": "Hey There, Ask me anything?"}
        ]
        st.rerun()

    elif event_type == "send":
        question = (event.get("message") or "").strip()
        if not question:
            return

        st.session_state["snapp_bot_open"] = True
        st.session_state["snapp_bot_messages"].append(
            {"role": "user", "content": question}
        )

        with st.spinner("Snapp Bot is thinking..."):
            try:
                answer = answer_fn(question, dashboard_context)
            except Exception as e:
                answer = f"Snapp Bot hit an error: {e}"

        st.session_state["snapp_bot_messages"].append(
            {"role": "assistant", "content": answer}
        )
        st.rerun()