from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Agent Platform</title>
<style>
  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #242736;
    --border: #2e3244;
    --text: #e4e4e7;
    --text2: #a1a1aa;
    --accent: #6366f1;
    --accent-hover: #818cf8;
    --green: #22c55e;
    --red: #ef4444;
    --yellow: #eab308;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 12px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }

  header h1 {
    font-size: 18px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  header h1 .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--green);
    display: inline-block;
  }

  .status-bar {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: var(--text2);
  }

  .status-bar .badge {
    background: var(--surface2);
    padding: 4px 10px;
    border-radius: 12px;
    border: 1px solid var(--border);
  }

  .main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  .sidebar {
    width: 280px;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow-y: auto;
    flex-shrink: 0;
  }

  .panel {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
  }

  .panel h3 {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text2);
    margin-bottom: 10px;
  }

  .panel-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 0;
    font-size: 13px;
    border-bottom: 1px solid var(--border);
  }

  .panel-item:last-child { border-bottom: none; }

  .panel-item .label { color: var(--text2); }
  .panel-item .value { font-weight: 500; }

  .tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 500;
  }

  .tag-green { background: #16532d; color: #4ade80; }
  .tag-blue { background: #1e3a5f; color: #60a5fa; }
  .tag-yellow { background: #422006; color: #fbbf24; }

  .empty-list {
    color: var(--text2);
    font-size: 12px;
    font-style: italic;
    padding: 4px 0;
  }

  .chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .msg {
    max-width: 720px;
    line-height: 1.6;
    font-size: 14px;
  }

  .msg.user {
    align-self: flex-end;
    background: var(--accent);
    color: white;
    padding: 10px 16px;
    border-radius: 16px 16px 4px 16px;
  }

  .msg.assistant {
    align-self: flex-start;
    background: var(--surface2);
    border: 1px solid var(--border);
    padding: 12px 16px;
    border-radius: 16px 16px 16px 4px;
  }

  .msg.assistant .meta {
    margin-top: 8px;
    font-size: 11px;
    color: var(--text2);
  }

  .msg.system {
    align-self: center;
    color: var(--text2);
    font-size: 12px;
    font-style: italic;
  }

  .msg .msg-actions {
    display: none;
    gap: 6px;
    margin-top: 6px;
  }

  .msg:hover .msg-actions { display: flex; }

  .msg-actions button {
    background: none;
    border: 1px solid var(--border);
    color: var(--text2);
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .msg-actions button:hover {
    color: var(--text);
    border-color: var(--text2);
  }

  .msg-actions button.delete:hover {
    color: var(--red);
    border-color: var(--red);
  }

  .msg .edit-area {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .msg .edit-area textarea {
    background: var(--bg);
    border: 1px solid var(--accent);
    border-radius: 6px;
    color: var(--text);
    font-size: 13px;
    font-family: inherit;
    padding: 8px;
    resize: vertical;
    min-height: 60px;
    outline: none;
  }

  .msg .edit-area .edit-btns {
    display: flex;
    gap: 6px;
  }

  .msg .edit-area .edit-btns button {
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 4px;
    border: none;
    cursor: pointer;
  }

  .msg .edit-area .edit-btns .save-btn {
    background: var(--accent);
    color: white;
  }

  .msg .edit-area .edit-btns .cancel-btn {
    background: var(--surface2);
    color: var(--text2);
    border: 1px solid var(--border);
  }

  .clear-btn {
    background: none;
    border: 1px solid var(--border);
    color: var(--text2);
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .clear-btn:hover {
    color: var(--red);
    border-color: var(--red);
  }

  .welcome {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: var(--text2);
  }

  .welcome h2 {
    font-size: 24px;
    color: var(--text);
    font-weight: 600;
  }

  .welcome p { font-size: 14px; }

  .input-area {
    padding: 16px 24px;
    border-top: 1px solid var(--border);
    background: var(--surface);
    flex-shrink: 0;
  }

  .input-row {
    display: flex;
    gap: 8px;
    max-width: 760px;
    margin: 0 auto;
  }

  .input-row select {
    background: var(--surface2);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0 10px;
    font-size: 12px;
    cursor: pointer;
    outline: none;
  }

  .input-row input {
    flex: 1;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    color: var(--text);
    font-size: 14px;
    outline: none;
    transition: border-color 0.15s;
  }

  .input-row input:focus { border-color: var(--accent); }

  .input-row button {
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s;
  }

  .input-row button:hover { background: var(--accent-hover); }
  .input-row button:disabled { opacity: 0.5; cursor: not-allowed; }

  .typing {
    display: inline-flex;
    gap: 4px;
    padding: 4px 0;
  }
  .typing span {
    width: 6px; height: 6px;
    background: var(--text2);
    border-radius: 50%;
    animation: bounce 1.4s infinite;
  }
  .typing span:nth-child(2) { animation-delay: 0.2s; }
  .typing span:nth-child(3) { animation-delay: 0.4s; }

  @keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-6px); }
  }
</style>
</head>
<body>

<header>
  <h1><span class="dot"></span> AI Agent Platform</h1>
  <div class="status-bar">
    <span class="badge" id="statusBadge">Checking...</span>
    <span class="badge" id="modelBadge">--</span>
    <button class="clear-btn" onclick="clearChat()">Clear chat</button>
  </div>
</header>

<div class="main">
  <div class="sidebar">
    <div class="panel">
      <h3>System</h3>
      <div class="panel-item">
        <span class="label">Health</span>
        <span class="value" id="healthStatus">--</span>
      </div>
      <div class="panel-item">
        <span class="label">Provider</span>
        <span class="value">Gemini</span>
      </div>
      <div class="panel-item">
        <span class="label">Vector DB</span>
        <span class="value">pgvector</span>
      </div>
      <div class="panel-item">
        <span class="label">Runtime</span>
        <span class="value">Custom</span>
      </div>
    </div>

    <div class="panel">
      <h3>Registered Agents</h3>
      <div id="agentsList"><span class="empty-list">Loading...</span></div>
    </div>

    <div class="panel">
      <h3>Available Tools</h3>
      <div id="toolsList"><span class="empty-list">Loading...</span></div>
    </div>

    <div class="panel">
      <h3>Session Stats</h3>
      <div class="panel-item">
        <span class="label">Messages</span>
        <span class="value" id="statMessages">0</span>
      </div>
      <div class="panel-item">
        <span class="label">Tokens Used</span>
        <span class="value" id="statTokens">0</span>
      </div>
      <div class="panel-item">
        <span class="label">Avg Latency</span>
        <span class="value" id="statLatency">--</span>
      </div>
    </div>
  </div>

  <div class="chat-area">
    <div class="messages" id="messages">
      <div class="welcome">
        <h2>Welcome</h2>
        <p>Send a message to start chatting with the AI agent.</p>
        <p style="font-size:12px">Select a model below, then type your message.</p>
      </div>
    </div>

    <div class="input-area">
      <div class="input-row">
        <select id="modelSelect">
          <option value="gemini-3.1-pro-preview">Gemini 3.1 Pro</option>
          <option value="gemini-3-flash-preview">Gemini 3 Flash</option>
          <option value="gemini-3.1-flash-lite-preview">Gemini 3.1 Flash Lite</option>
          <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
          <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
        </select>
        <input type="text" id="chatInput" placeholder="Type a message..." autocomplete="off" />
        <button id="sendBtn" onclick="sendMessage()">Send</button>
      </div>
      <div style="max-width:760px;margin:8px auto 0;display:flex;align-items:center;gap:8px;">
        <label style="font-size:11px;color:var(--text2);white-space:nowrap;">System prompt:</label>
        <input type="text" id="systemPrompt" value="You are a helpful AI assistant. You have access to a tavily_search tool for searching the web. When the user asks about current events, recent information, or anything you're unsure about, use the tavily_search tool to find accurate answers."
          style="flex:1;background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:6px 10px;color:var(--text);font-size:12px;outline:none;" />
      </div>
    </div>
  </div>
</div>

<script>
  const messagesEl = document.getElementById('messages');
  const inputEl = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const modelSelect = document.getElementById('modelSelect');
  const systemPromptEl = document.getElementById('systemPrompt');

  let msgCount = 0;
  let totalTokens = 0;
  let totalLatency = 0;
  let welcomeVisible = true;
  let sessionId = '';
  // Local mirror of message history (index, role, text)
  let localHistory = [];

  inputEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !sendBtn.disabled) sendMessage();
  });

  function escHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function renderMessages() {
    if (welcomeVisible) return;
    messagesEl.innerHTML = '';
    localHistory.forEach((m, idx) => {
      const div = document.createElement('div');
      const uiRole = m.role === 'model' ? 'assistant' : m.role;
      div.className = 'msg ' + uiRole;
      div.dataset.idx = idx;

      let inner = '<div class="msg-text">' + escHtml(m.text) + '</div>';
      if (m.meta) inner += '<div class="meta">' + m.meta + '</div>';

      if (uiRole !== 'system') {
        inner += '<div class="msg-actions">'
          + '<button onclick="startEdit(' + idx + ')">Edit</button>'
          + '<button class="delete" onclick="deleteMsg(' + idx + ')">Delete</button>'
          + '</div>';
      }

      div.innerHTML = inner;
      messagesEl.appendChild(div);
    });
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addMessage(role, content, meta) {
    if (welcomeVisible) {
      messagesEl.innerHTML = '';
      welcomeVisible = false;
    }
    localHistory.push({ role, text: content, meta: meta || '' });
    renderMessages();
  }

  function startEdit(idx) {
    const msg = localHistory[idx];
    const el = messagesEl.querySelector('[data-idx="' + idx + '"]');
    if (!el) return;
    const textEl = el.querySelector('.msg-text');
    const actionsEl = el.querySelector('.msg-actions');
    if (actionsEl) actionsEl.style.display = 'none';

    const editDiv = document.createElement('div');
    editDiv.className = 'edit-area';
    editDiv.innerHTML = '<textarea>' + escHtml(msg.text) + '</textarea>'
      + '<div class="edit-btns">'
      + '<button class="save-btn" onclick="saveEdit(' + idx + ', this)">Save</button>'
      + '<button class="cancel-btn" onclick="renderMessages()">Cancel</button>'
      + '</div>';

    textEl.style.display = 'none';
    el.appendChild(editDiv);
    editDiv.querySelector('textarea').focus();
  }

  async function saveEdit(idx, btn) {
    const el = messagesEl.querySelector('[data-idx="' + idx + '"]');
    const newText = el.querySelector('.edit-area textarea').value.trim();
    if (!newText) return;

    btn.disabled = true;
    btn.textContent = 'Saving...';

    try {
      const res = await fetch('/api/history/edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, index: idx, text: newText }),
      });
      const data = await res.json();
      if (data.ok) {
        // Update local: change text and truncate after
        localHistory[idx].text = newText;
        localHistory = localHistory.slice(0, idx + 1);
        renderMessages();
      }
    } catch (err) {
      addMessage('system', 'Edit failed: ' + err.message);
    }
  }

  async function deleteMsg(idx) {
    try {
      const res = await fetch('/api/history/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, index: idx }),
      });
      const data = await res.json();
      if (data.ok) {
        localHistory.splice(idx, 1);
        if (localHistory.length === 0) {
          welcomeVisible = true;
          messagesEl.innerHTML = '<div class="welcome"><h2>Welcome</h2><p>Send a message to start chatting.</p></div>';
        } else {
          renderMessages();
        }
      }
    } catch (err) {
      addMessage('system', 'Delete failed: ' + err.message);
    }
  }

  async function clearChat() {
    if (!sessionId) {
      welcomeVisible = true;
      localHistory = [];
      messagesEl.innerHTML = '<div class="welcome"><h2>Welcome</h2><p>Send a message to start chatting.</p></div>';
      return;
    }
    try {
      await fetch('/api/history/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch {}
    sessionId = '';
    localHistory = [];
    msgCount = 0; totalTokens = 0; totalLatency = 0;
    welcomeVisible = true;
    messagesEl.innerHTML = '<div class="welcome"><h2>Welcome</h2><p>Send a message to start chatting.</p></div>';
    document.getElementById('statMessages').textContent = '0';
    document.getElementById('statTokens').textContent = '0';
    document.getElementById('statLatency').textContent = '--';
  }

  function showTyping() {
    const div = document.createElement('div');
    div.className = 'msg assistant';
    div.id = 'typing';
    div.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function removeTyping() {
    const el = document.getElementById('typing');
    if (el) el.remove();
  }

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;

    inputEl.value = '';
    sendBtn.disabled = true;
    addMessage('user', text);
    showTyping();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          model: modelSelect.value,
          session_id: sessionId,
          system: systemPromptEl.value.trim() || 'You are a helpful AI assistant.',
        }),
      });
      const data = await res.json();
      removeTyping();

      const tokens = (data.input_tokens || 0) + (data.output_tokens || 0);
      const latency = data.latency_ms || 0;
      let meta = data.model + ' &middot; ' + tokens + ' tokens &middot; ' + latency.toFixed(0) + 'ms';
      if (data.tool_calls && data.tool_calls.length > 0) {
        const toolInfo = data.tool_calls.map(tc => tc.tool + ': "' + tc.query + '"').join(', ');
        meta += ' &middot; searched: ' + toolInfo;
      }

      addMessage('model', data.reply, meta);

      if (data.session_id) sessionId = data.session_id;
      msgCount++;
      totalTokens += tokens;
      totalLatency += latency;
      document.getElementById('statMessages').textContent = msgCount;
      document.getElementById('statTokens').textContent = totalTokens.toLocaleString();
      document.getElementById('statLatency').textContent = (totalLatency / msgCount).toFixed(0) + 'ms';
      document.getElementById('modelBadge').textContent = data.model;

    } catch (err) {
      removeTyping();
      addMessage('system', 'Error: ' + err.message);
    }

    sendBtn.disabled = false;
    inputEl.focus();
  }

  async function loadStatus() {
    try {
      const res = await fetch('/health');
      const data = await res.json();
      document.getElementById('healthStatus').innerHTML = '<span class="tag tag-green">' + data.status + '</span>';
      document.getElementById('statusBadge').textContent = 'Online';
    } catch {
      document.getElementById('healthStatus').innerHTML = '<span class="tag" style="background:#5b2121;color:#fca5a5">offline</span>';
      document.getElementById('statusBadge').textContent = 'Offline';
    }
  }

  async function loadAgents() {
    try {
      const res = await fetch('/api/agents');
      const data = await res.json();
      const el = document.getElementById('agentsList');
      if (data.agents.length === 0) {
        el.innerHTML = '<span class="empty-list">No agents registered yet</span>';
      } else {
        el.innerHTML = data.agents.map(a =>
          '<div class="panel-item"><span class="value">' + a.name + '</span><span class="tag tag-blue">active</span></div>'
        ).join('');
      }
    } catch { }
  }

  async function loadTools() {
    try {
      const res = await fetch('/api/tools');
      const data = await res.json();
      const el = document.getElementById('toolsList');
      if (data.tools.length === 0) {
        el.innerHTML = '<span class="empty-list">No tools registered yet</span>';
      } else {
        el.innerHTML = data.tools.map(t => {
          const tagClass = t.safety === 'safe' ? 'tag-green' : t.safety === 'requires_approval' ? 'tag-yellow' : 'tag-blue';
          return '<div class="panel-item"><span class="value">' + t.name + '</span><span class="tag ' + tagClass + '">' + t.safety + '</span></div>';
        }).join('');
      }
    } catch { }
  }

  loadStatus();
  loadAgents();
  loadTools();
</script>
</body>
</html>"""
