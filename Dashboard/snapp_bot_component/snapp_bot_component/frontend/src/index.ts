import { onRender } from "@streamlit/component-v2-lib";

type BotMessage = {
  role: "user" | "assistant";
  content: string;
};

type BotArgs = {
  is_open?: boolean;
  assistant_name?: string;
  assistant_subtitle?: string;
  input_placeholder?: string;
  messages?: BotMessage[];
};

function escapeHtml(value: unknown): string {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function injectStyles() {
  const styleId = "snapp-bot-styles";

  if (document.getElementById(styleId)) return;

  const style = document.createElement("style");
  style.id = styleId;
  style.textContent = `
    html, body {
      margin: 0;
      padding: 0;
      background: transparent;
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      overflow: hidden;
    }

    * {
      box-sizing: border-box;
    }

    .snapp-bot-root {
      position: relative;
      width: 100%;
      min-height: 720px;
      background: transparent;
    }

    .snapp-bot-shell {
      position: fixed;
      right: 24px;
      bottom: 24px;
      width: 420px;
      max-width: calc(100vw - 32px);
      z-index: 999999;
    }

    .snapp-bot-fab-wrap {
      position: absolute;
      right: 0;
      bottom: 0;
      display: flex;
      justify-content: flex-end;
      width: 100%;
      pointer-events: auto;
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
      transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    .snapp-bot-fab:hover {
      transform: translateY(-2px) scale(1.03);
      box-shadow:
        0 22px 52px rgba(15, 23, 42, 0.34),
        0 0 0 1px rgba(255,255,255,0.06) inset,
        0 0 0 7px rgba(245, 158, 11, 0.10);
    }

    .snapp-bot-panel-wrap {
      position: absolute;
      right: 0;
      bottom: 88px;
      width: 100%;
      pointer-events: auto;
    }

    .snapp-bot-panel {
      width: 100%;
      border-radius: 26px;
      overflow: hidden;
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid rgba(245, 158, 11, 0.18);
      box-shadow:
        0 30px 80px rgba(15, 23, 42, 0.24),
        0 0 0 1px rgba(255,255,255,0.42) inset,
        0 0 0 8px rgba(245, 158, 11, 0.04);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
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
      max-height: 320px;
      min-height: 230px;
      overflow-y: auto;
      padding-right: 4px;
      margin-bottom: 12px;
      scrollbar-width: thin;
      scrollbar-color: rgba(15,23,42,0.16) transparent;
    }

    .snapp-bot-messages::-webkit-scrollbar {
      width: 8px;
    }

    .snapp-bot-messages::-webkit-scrollbar-thumb {
      background: rgba(15, 23, 42, 0.16);
      border-radius: 999px;
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
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
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
      border-radius: 14px;
      border: 1px solid rgba(15, 23, 42, 0.10);
      background: rgba(255,255,255,0.98);
      color: #111827;
      padding: 14px 14px;
      font-size: 15px;
      outline: none;
    }

    .snapp-bot-input::placeholder {
      color: rgba(17, 24, 39, 0.42);
    }

    .snapp-bot-input:focus {
      border-color: rgba(245, 158, 11, 0.34);
      box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.10);
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
      box-shadow: 0 10px 24px rgba(245, 158, 11, 0.20);
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
    }
  `;
  document.head.appendChild(style);
}

function scrollMessagesToBottom() {
  const box = document.querySelector(".snapp-bot-messages");
  if (box) {
    box.scrollTop = box.scrollHeight;
  }
}

function mountComponent(args: BotArgs) {
  injectStyles();

  const root = document.body;
  const isOpen = !!args.is_open;
  const messages = Array.isArray(args.messages) ? args.messages : [];

  root.innerHTML = `
    <div class="snapp-bot-root">
      <div class="snapp-bot-shell">
        ${
          isOpen
            ? `
          <div class="snapp-bot-panel-wrap">
            <div class="snapp-bot-panel">
              <div class="snapp-bot-header">
                <div>
                  <div class="snapp-bot-title">${escapeHtml(args.assistant_name ?? "Snapp Bot")}</div>
                  <div class="snapp-bot-subtitle">${escapeHtml(args.assistant_subtitle ?? "Dashboard Assistant")}</div>
                </div>
                <button class="snapp-bot-close" type="button">×</button>
              </div>

              <div class="snapp-bot-body">
                <div class="snapp-bot-inner">
                  <div class="snapp-bot-messages">
                    ${messages
                      .map(
                        (msg) => `
                          <div class="snapp-bot-msg ${msg.role === "user" ? "user" : "assistant"}">
                            ${escapeHtml(msg.content)}
                          </div>
                        `
                      )
                      .join("")}
                  </div>

                  <div class="snapp-bot-note">Ask a question about the dashboard</div>
                  <input
                    class="snapp-bot-input"
                    type="text"
                    placeholder="${escapeHtml(args.input_placeholder ?? "Type here...")}"
                  />

                  <div class="snapp-bot-actions">
                    <button class="snapp-bot-btn send" type="button">Send</button>
                    <button class="snapp-bot-btn clear" type="button">Clear</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `
            : ""
        }

        <div class="snapp-bot-fab-wrap">
          <button class="snapp-bot-fab" type="button">${isOpen ? "×" : "💬"}</button>
        </div>
      </div>
    </div>
  `;

  const fab = document.querySelector(".snapp-bot-fab") as HTMLButtonElement | null;
  const closeBtn = document.querySelector(".snapp-bot-close") as HTMLButtonElement | null;
  const input = document.querySelector(".snapp-bot-input") as HTMLInputElement | null;
  const sendBtn = document.querySelector(".snapp-bot-btn.send") as HTMLButtonElement | null;
  const clearBtn = document.querySelector(".snapp-bot-btn.clear") as HTMLButtonElement | null;

  if (fab) {
    fab.onclick = () => {
      alert("Frontend shell is working. Next we will wire real events.");
    };
  }

  if (closeBtn) {
    closeBtn.onclick = () => {
      alert("Close button works visually. Real Python event wiring comes next.");
    };
  }

  if (sendBtn) {
    sendBtn.onclick = () => {
      alert(`Typed: ${input?.value ?? ""}`);
    };
  }

  if (clearBtn) {
    clearBtn.onclick = () => {
      if (input) input.value = "";
    };
  }

  setTimeout(scrollMessagesToBottom, 0);
}

onRender((event) => {
  const args = (event as { data?: BotArgs }).data ?? {};
  mountComponent(args);
});