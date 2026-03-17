import streamlit as st

HTML = """
<div id="snapp-bot-root"></div>
"""

CSS = """
#snapp-bot-root {
  all: initial;
  font-family: Inter, "Segoe UI", Arial, sans-serif;
  position: relative;
  z-index: 2147483646;
}

.snapp-bot-shell {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 420px;
  max-width: min(420px, calc(100vw - 24px));
  z-index: 2147483646;
  font-family: Inter, "Segoe UI", Arial, sans-serif;
  pointer-events: none;
}

.snapp-bot-fab-wrap {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  pointer-events: none;
}

.snapp-bot-fab {
  width: 68px;
  height: 68px;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
  color: #ffffff;
  font-size: 28px;
  line-height: 1;
  box-shadow:
    0 18px 40px rgba(15, 23, 42, 0.28),
    0 0 0 1px rgba(255,255,255,0.05) inset,
    0 0 0 5px rgba(245, 158, 11, 0.08);
  pointer-events: auto;
}

.snapp-bot-panel-wrap {
  width: 100%;
  margin-bottom: 14px;
  pointer-events: none;
}

.snapp-bot-panel {
  width: 100%;
  border-radius: 26px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(245, 158, 11, 0.18);
  box-shadow:
    0 30px 80px rgba(15, 23, 42, 0.24),
    0 0 0 1px rgba(255,255,255,0.42) inset,
    0 0 0 8px rgba(245, 158, 11, 0.04);
  pointer-events: auto;
}

.snapp-bot-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 18px 14px 18px;
  background: linear-gradient(135deg, #fff8e8 0%, #fff1c7 100%);
  border-bottom: 1px solid rgba(245, 158, 11, 0.14);
}

.snapp-bot-title {
  font-size: 16px;
  font-weight: 800;
  line-height: 1.1;
  color: #0b1220;
  margin: 0;
}

.snapp-bot-subtitle {
  margin-top: 5px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(11, 18, 32, 0.58);
}

.snapp-bot-close {
  width: 42px;
  height: 42px;
  border-radius: 999px;
  border: 1px solid rgba(245, 158, 11, 0.18);
  background: rgba(255,255,255,0.74);
  color: #111827;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
}

.snapp-bot-body {
  padding: 16px;
  background: linear-gradient(180deg, rgba(255,255,255,0.78) 0%, rgba(250,250,252,0.92) 100%);
}

.snapp-bot-inner {
  background: rgba(255,255,255,0.96);
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 20px;
  box-shadow:
    0 8px 24px rgba(15, 23, 42, 0.05),
    0 0 0 1px rgba(255,255,255,0.6) inset;
  padding: 14px;
}

.snapp-bot-messages {
  height: min(320px, 42vh);
  min-height: 230px;
  overflow-y: auto;
  padding-right: 4px;
  margin-bottom: 12px;
}

.snapp-bot-msg {
  padding: 12px 14px;
  border-radius: 16px;
  margin-bottom: 10px;
  font-size: 13px;
  line-height: 1.58;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.snapp-bot-msg.assistant {
  margin-right: 26px;
  background: rgba(243, 246, 249, 0.96);
  border: 1px solid rgba(15, 23, 42, 0.08);
  color: #111827;
}

.snapp-bot-msg.user {
  margin-left: 26px;
  background: linear-gradient(135deg, rgba(245,158,11,0.10) 0%, rgba(251,191,36,0.12) 100%);
  border: 1px solid rgba(245,158,11,0.18);
  color: #111827;
}

.snapp-bot-note {
  font-size: 12px;
  font-weight: 600;
  color: rgba(11, 18, 32, 0.58);
  margin: 2px 0 8px 2px;
}

.snapp-bot-input {
  width: 100%;
  box-sizing: border-box;
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.10);
  background: rgba(255,255,255,0.98);
  color: #111827;
  padding: 14px 14px;
  font-size: 15px;
  outline: none;
}

.snapp-bot-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.snapp-bot-btn {
  width: 100%;
  border-radius: 14px;
  padding: 12px 14px;
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
}

.snapp-bot-btn.send {
  border: 1px solid rgba(245, 158, 11, 0.22);
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  color: #ffffff;
}

.snapp-bot-btn.clear {
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: rgba(248,250,252,1);
  color: #111827;
}

@media (max-width: 640px) {
  .snapp-bot-shell {
    right: 12px;
    bottom: 12px;
    width: calc(100vw - 24px);
    max-width: calc(100vw - 24px);
  }

  .snapp-bot-fab {
    width: 62px;
    height: 62px;
    font-size: 24px;
  }

  .snapp-bot-messages {
    height: min(300px, 38vh);
  }
}
"""

JS = """
export default function(component) {
  const { data, parentElement, setTriggerValue } = component;

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function makeEvent(type, extra = {}) {
    return {
      type,
      event_id: `${Date.now()}_${Math.random().toString(36).slice(2, 10)}`,
      ...extra,
    };
  }

  const mount = parentElement.querySelector("#snapp-bot-root");
  if (!mount) return;

  const isOpen = !!(data && data.is_open);
  const messages = Array.isArray(data && data.messages) ? data.messages : [];
  const assistantName = (data && data.assistant_name) || "Snapp Bot";
  const assistantSubtitle = (data && data.assistant_subtitle) || "Dashboard Assistant";
  const inputPlaceholder = (data && data.input_placeholder) || "Type here...";

  // Persist DOM + handlers across rerenders to reduce flicker.
  // Streamlit will rerun Python often; this component should only update what changed.
  const state = (mount.__snapp_bot_state ||= {});

  function renderMessages(container, nextMessages) {
    const html = nextMessages
      .map(
        (msg) => `
          <div class="snapp-bot-msg ${msg.role === "user" ? "user" : "assistant"}">
            ${escapeHtml(msg.content)}
          </div>
        `
      )
      .join("");

    if (state._messagesHtml === html) return;

    const shouldStickToBottom =
      container.scrollTop + container.clientHeight >= container.scrollHeight - 24;

    container.innerHTML = html;
    state._messagesHtml = html;

    if (shouldStickToBottom) {
      container.scrollTop = container.scrollHeight;
    }
  }

  function ensureMounted() {
    if (state._mounted) return;

    mount.innerHTML = `
      <div class="snapp-bot-shell">
        <div class="snapp-bot-panel-wrap">
          <div class="snapp-bot-panel">
            <div class="snapp-bot-header">
              <div>
                <div class="snapp-bot-title"></div>
                <div class="snapp-bot-subtitle"></div>
              </div>
              <button class="snapp-bot-close" type="button">×</button>
            </div>

            <div class="snapp-bot-body">
              <div class="snapp-bot-inner">
                <div class="snapp-bot-messages"></div>

                <div class="snapp-bot-note">Ask a question about the dashboard</div>
                <input class="snapp-bot-input" type="text" />

                <div class="snapp-bot-actions">
                  <button class="snapp-bot-btn send" type="button">Send</button>
                  <button class="snapp-bot-btn clear" type="button">Clear</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="snapp-bot-fab-wrap">
          <button class="snapp-bot-fab" type="button">💬</button>
        </div>
      </div>
    `;

    state.shell = mount.querySelector(".snapp-bot-shell");
    state.panelWrap = mount.querySelector(".snapp-bot-panel-wrap");
    state.titleEl = mount.querySelector(".snapp-bot-title");
    state.subtitleEl = mount.querySelector(".snapp-bot-subtitle");
    state.closeBtn = mount.querySelector(".snapp-bot-close");
    state.messagesBox = mount.querySelector(".snapp-bot-messages");
    state.input = mount.querySelector(".snapp-bot-input");
    state.sendBtn = mount.querySelector(".snapp-bot-btn.send");
    state.clearBtn = mount.querySelector(".snapp-bot-btn.clear");
    state.fab = mount.querySelector(".snapp-bot-fab");

    if (state.fab) {
      state.fab.onclick = () => setTriggerValue("event", makeEvent("toggle"));
    }
    if (state.closeBtn) {
      state.closeBtn.onclick = () => setTriggerValue("event", makeEvent("close"));
    }
    if (state.clearBtn) {
      state.clearBtn.onclick = () => setTriggerValue("event", makeEvent("clear"));
    }
    if (state.sendBtn && state.input) {
      const submit = () => {
        const message = state.input.value.trim();
        if (!message) return;
        state.input.value = "";
        setTriggerValue("event", makeEvent("send", { message }));
      };
      state.sendBtn.onclick = submit;
      state.input.onkeydown = (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          submit();
        }
      };
    }

    state._mounted = true;
  }

  ensureMounted();

  if (state.titleEl) state.titleEl.textContent = assistantName;
  if (state.subtitleEl) state.subtitleEl.textContent = assistantSubtitle;
  if (state.input) state.input.placeholder = inputPlaceholder;

  if (state.panelWrap) {
    state.panelWrap.style.display = isOpen ? "" : "none";
  }
  if (state.fab) {
    state.fab.textContent = isOpen ? "×" : "💬";
  }

  if (state.messagesBox) {
    renderMessages(state.messagesBox, messages);
  }

  if (isOpen && state.input) {
    // Focus without forcing a rebuild.
    setTimeout(() => state.input && state.input.focus(), 0);
  }
}
"""

_snapp_bot_component = st.components.v2.component(
    "snapp_bot_component.snapp_bot_component",
    html=HTML,
    css=CSS,
    js=JS,
    isolate_styles=False,
)


def snapp_bot_component(
    *,
    is_open: bool = True,
    assistant_name: str = "Snapp Bot",
    assistant_subtitle: str = "Dashboard Assistant",
    input_placeholder: str = "e.g. What does macro pressure mean?",
    messages: list | None = None,
    key=None,
):
    if messages is None:
        messages = [{"role": "assistant", "content": "Hey There, Ask me anything?"}]

    return _snapp_bot_component(
        key=key,
        data={
            "is_open": is_open,
            "assistant_name": assistant_name,
            "assistant_subtitle": assistant_subtitle,
            "input_placeholder": input_placeholder,
            "messages": messages,
        },
        on_event_change=lambda: None,
    )