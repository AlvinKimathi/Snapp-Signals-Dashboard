let latestArgs = {
  messages: [],
  is_open: false,
  assistant_name: "Snapp Bot",
  assistant_subtitle: "Dashboard Assistant",
  input_placeholder: "e.g. What does macro pressure mean?",
};

let draftMessage = "";

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

function sendValue(payload) {
  window.Streamlit.setComponentValue(payload);
}

function setHeight() {
  const openHeight = 650;
  const closedHeight = 90;
  window.Streamlit.setFrameHeight(latestArgs.is_open ? openHeight : closedHeight);
}

function scrollMessagesToBottom() {
  const box = document.querySelector(".bot-messages");
  if (box) {
    box.scrollTop = box.scrollHeight;
  }
}

function render() {
  const app = document.getElementById("app");
  const isOpen = !!latestArgs.is_open;
  const messages = Array.isArray(latestArgs.messages) ? latestArgs.messages : [];

  const panelHtml = isOpen
    ? `
      <div class="bot-panel-wrap">
        <div class="bot-panel">
          <div class="bot-header">
            <div>
              <div class="bot-title">${escapeHtml(latestArgs.assistant_name)}</div>
              <div class="bot-subtitle">${escapeHtml(latestArgs.assistant_subtitle)}</div>
            </div>
            <button class="bot-close" id="bot-close-btn" title="Close">×</button>
          </div>
          <div class="bot-body">
            <div class="bot-inner">
              <div class="bot-messages" id="bot-messages">
                ${messages.map((msg) => `
                  <div class="bot-msg ${msg.role === "user" ? "user" : "assistant"}">
                    ${escapeHtml(msg.content)}
                  </div>
                `).join("")}
              </div>
              <div class="bot-note">Ask a question about the dashboard</div>
              <input
                id="bot-input"
                class="bot-input"
                type="text"
                placeholder="${escapeHtml(latestArgs.input_placeholder)}"
                value="${escapeHtml(draftMessage)}"
              />
              <div class="bot-actions">
                <button class="bot-btn send" id="bot-send-btn">Send</button>
                <button class="bot-btn clear" id="bot-clear-btn">Clear</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `
    : "";

  app.innerHTML = `
    <div class="bot-root">
      <div class="bot-shell">
        ${panelHtml}
        <div class="bot-bubble-wrap">
          <button class="bot-bubble" id="bot-toggle-btn" title="Snapp Bot">
            ${isOpen ? "×" : "💬"}
          </button>
        </div>
      </div>
    </div>
  `;

  const toggleBtn = document.getElementById("bot-toggle-btn");
  if (toggleBtn) {
    toggleBtn.onclick = () => sendValue(makeEvent("toggle"));
  }

  const closeBtn = document.getElementById("bot-close-btn");
  if (closeBtn) {
    closeBtn.onclick = () => sendValue(makeEvent("close"));
  }

  const clearBtn = document.getElementById("bot-clear-btn");
  if (clearBtn) {
    clearBtn.onclick = () => {
      draftMessage = "";
      sendValue(makeEvent("clear"));
    };
  }

  const input = document.getElementById("bot-input");
  if (input) {
    input.oninput = (e) => {
      draftMessage = e.target.value;
    };

    input.onkeydown = (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const message = draftMessage.trim();
        if (!message) return;
        draftMessage = "";
        sendValue(makeEvent("send", { message }));
      }
    };
  }

  const sendBtn = document.getElementById("bot-send-btn");
  if (sendBtn) {
    sendBtn.onclick = () => {
      const message = draftMessage.trim();
      if (!message) return;
      draftMessage = "";
      sendValue(makeEvent("send", { message }));
    };
  }

  setHeight();
  setTimeout(scrollMessagesToBottom, 50);
}

function onRender(event) {
  latestArgs = {
    ...latestArgs,
    ...(event.detail.args || {}),
  };
  render();
}

window.addEventListener("load", () => {
  if (!window.Streamlit) {
    document.body.innerHTML = "<div style='padding:20px;color:red;'>Streamlit component lib not loaded.</div>";
    return;
  }

  window.Streamlit.events.addEventListener(window.Streamlit.RENDER_EVENT, onRender);
  window.Streamlit.setComponentReady();
  window.Streamlit.setFrameHeight(120);
});