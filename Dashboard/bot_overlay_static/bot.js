(() => {
  const API_BASE =
    (window.SNAPP_BOT_API_URL && String(window.SNAPP_BOT_API_URL)) ||
    "http://localhost:8000";

  const storageKey = "snappOverlayState_v1";
  const defaultState = {
    isOpen: false,
    messages: [{ role: "assistant", content: "Hey There, Ask me anything?" }],
  };

  function loadState() {
    try {
      const raw = sessionStorage.getItem(storageKey);
      if (!raw) return { ...defaultState };
      const parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== "object") return { ...defaultState };
      return {
        ...defaultState,
        ...parsed,
        messages: Array.isArray(parsed.messages) ? parsed.messages : defaultState.messages,
      };
    } catch {
      return { ...defaultState };
    }
  }

  function saveState(state) {
    try {
      sessionStorage.setItem(storageKey, JSON.stringify(state));
    } catch {
      // ignore
    }
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  const state = loadState();

  const shell = document.createElement("div");
  shell.className = "snapp-overlay-shell";

  shell.innerHTML = `
    <div class="snapp-overlay-panel" style="display: ${state.isOpen ? "" : "none"}">
      <div class="snapp-overlay-header">
        <div>
          <div class="snapp-overlay-title">Snapp Bot</div>
          <div class="snapp-overlay-subtitle">Dashboard Assistant</div>
        </div>
        <button class="snapp-overlay-close" type="button">×</button>
      </div>
      <div class="snapp-overlay-body">
        <div class="snapp-overlay-inner">
          <div class="snapp-overlay-messages"></div>
          <div class="snapp-overlay-note">Ask a question about the dashboard</div>
          <input class="snapp-overlay-input" type="text" placeholder="e.g. What does macro pressure mean?" />
          <div class="snapp-overlay-actions">
            <button class="snapp-overlay-btn send" type="button">Send</button>
            <button class="snapp-overlay-btn clear" type="button">Clear</button>
          </div>
        </div>
      </div>
    </div>
    <button class="snapp-overlay-fab" type="button">${state.isOpen ? "×" : "💬"}</button>
  `;

  document.documentElement.appendChild(shell);

  const panel = shell.querySelector(".snapp-overlay-panel");
  const fab = shell.querySelector(".snapp-overlay-fab");
  const closeBtn = shell.querySelector(".snapp-overlay-close");
  const msgBox = shell.querySelector(".snapp-overlay-messages");
  const input = shell.querySelector(".snapp-overlay-input");
  const sendBtn = shell.querySelector(".snapp-overlay-btn.send");
  const clearBtn = shell.querySelector(".snapp-overlay-btn.clear");

  function renderMessages() {
    if (!msgBox) return;
    msgBox.innerHTML = state.messages
      .map(
        (m) => `
        <div class="snapp-overlay-msg ${m.role === "user" ? "user" : "assistant"}">
          ${escapeHtml(m.content)}
        </div>
      `
      )
      .join("");
    msgBox.scrollTop = msgBox.scrollHeight;
  }

  function setOpen(next) {
    state.isOpen = !!next;
    if (panel) panel.style.display = state.isOpen ? "" : "none";
    if (fab) fab.textContent = state.isOpen ? "×" : "💬";
    saveState(state);
    if (state.isOpen && input) setTimeout(() => input.focus(), 0);
  }

  async function ask(question) {
    state.messages.push({ role: "user", content: question });
    state.messages.push({ role: "assistant", content: "Thinking..." });
    renderMessages();
    saveState(state);

    try {
      const res = await fetch(`${API_BASE}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      const data = await res.json();
      const answer = data && data.answer ? String(data.answer) : "No answer returned.";
      state.messages[state.messages.length - 1] = { role: "assistant", content: answer };
    } catch (e) {
      state.messages[state.messages.length - 1] = {
        role: "assistant",
        content: `Snapp Bot error: ${e && e.message ? e.message : String(e)}`,
      };
    }

    renderMessages();
    saveState(state);
  }

  if (fab) fab.addEventListener("click", () => setOpen(!state.isOpen));
  if (closeBtn) closeBtn.addEventListener("click", () => setOpen(false));
  if (clearBtn)
    clearBtn.addEventListener("click", () => {
      state.messages = [{ role: "assistant", content: "Hey There, Ask me anything?" }];
      renderMessages();
      saveState(state);
      if (input) input.value = "";
    });

  function submit() {
    const q = input && input.value ? input.value.trim() : "";
    if (!q) return;
    if (input) input.value = "";
    setOpen(true);
    ask(q);
  }

  if (sendBtn) sendBtn.addEventListener("click", submit);
  if (input)
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        submit();
      }
    });

  renderMessages();
})();

