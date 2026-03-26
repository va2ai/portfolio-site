/**
 * Agent Workspace - Advanced Frontend Logic
 */

// Core Elements
const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const modelSelect = document.getElementById('modelSelect');
const agentSelect = document.getElementById('agentSelect');
const inspectorPane = document.getElementById('inspectorPane');
const commandPalette = document.getElementById('commandPalette');
const paletteInput = document.getElementById('paletteInput');
const paletteResults = document.getElementById('paletteResults');

// State
let msgCount = 0;
let totalTokens = 0;
let totalLatency = 0;
let welcomeVisible = true;
let sessionId = '';
let totalToolCalls = 0;
let currentApp = 'chat';
let localHistory = [];
let lastResearchFindings = [];
let activityPoll = null;
let themes = ["dark", "light", "cupcake", "emerald", "corporate", "synthwave", "retro", "cyberpunk", "valentine", "halloween", "garden", "forest", "aqua", "lofi", "pastel", "fantasy", "wireframe", "black", "luxury", "dracula", "cmyk", "autumn", "business", "acid", "lemonade", "night", "coffee", "winter", "dim", "nord", "sunset"];
let currentThemeIdx = 0;

// Icons mapping for Lucide
const TOOL_ICONS = {
  tavily_search: 'search',
  exa_search: 'globe',
  calculator: 'calculator',
  get_current_datetime: 'clock',
  read_url: 'file-text',
  reddit_search: 'hash',
  reddit_read_post: 'hash',
  reddit_subreddit: 'hash',
  delegate_to_agent: 'bot',
};

/**
 * Initialization
 */
document.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  initListeners();
  initData();
});

function initListeners() {
  // Chat Input
  inputEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Command Palette
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      openCommandPalette();
    }
  });

  paletteInput.addEventListener('input', e => updatePaletteResults(e.target.value));
}

/**
 * App Logic
 */
function switchApp(appId) {
  currentApp = appId;
  document.querySelectorAll('nav .btn').forEach(b => b.classList.remove('active'));
  const btn = document.querySelector(`nav .btn[onclick*="${appId}"]`);
  if (btn) btn.classList.add('active');
  
  const titles = { chat: 'General Assistant', research: 'Research Lab', reddit: 'Social Explorer' };
  document.getElementById('currentAppTitle').textContent = titles[appId] || 'Assistant';
  
  // Auto-set agent based on app
  if (appId === 'research') agentSelect.value = 'research';
  else if (appId === 'reddit') agentSelect.value = 'reddit';
  else agentSelect.value = '';
}

function toggleInspector() {
  inspectorPane.classList.toggle('collapsed');
}

function toggleTheme() {
  currentThemeIdx = (currentThemeIdx + 1) % themes.length;
  const newTheme = themes[currentThemeIdx];
  document.documentElement.setAttribute('data-theme', newTheme);
}

function fillInput(text) {
  inputEl.value = text;
  inputEl.style.height = '56px';
  inputEl.style.height = inputEl.scrollHeight + 'px';
  inputEl.focus();
}

/**
 * Command Palette
 */
function openCommandPalette() {
  commandPalette.showModal();
  paletteInput.value = '';
  updatePaletteResults('');
  setTimeout(() => paletteInput.focus(), 10);
}

function updatePaletteResults(query) {
  const q = query.toLowerCase();
  const commands = [
    { name: 'Switch to Research', icon: 'search', action: () => switchApp('research') },
    { name: 'Switch to Reddit', icon: 'hash', action: () => switchApp('reddit') },
    { name: 'Clear History', icon: 'trash-2', action: clearChat, color: 'text-error' },
    { name: 'Toggle Inspector', icon: 'sidebar', action: toggleInspector },
    { name: 'Export Report', icon: 'download', action: exportReport },
    { name: 'Model: Gemini 3.1 Pro', icon: 'cpu', action: () => modelSelect.value = 'gemini-3.1-pro-preview' },
    { name: 'Model: Gemini 3 Flash', icon: 'zap', action: () => modelSelect.value = 'gemini-3-flash-preview' },
    { name: 'Model: Gemini 3.1 Flash Lite', icon: 'zap-off', action: () => modelSelect.value = 'gemini-3.1-flash-lite-preview' },
    { name: 'Model: Gemini 2.5 Pro', icon: 'cpu', action: () => modelSelect.value = 'gemini-2.5-pro' },
    { name: 'Model: Gemini 2.5 Flash', icon: 'zap', action: () => modelSelect.value = 'gemini-2.5-flash' },
  ];

  const filtered = commands.filter(c => c.name.toLowerCase().includes(q));
  paletteResults.innerHTML = filtered.map((c, i) => `
    <div class="palette-item p-3 rounded-xl flex items-center gap-3 ${c.color || ''}" onclick="runPaletteCommand(${i})">
      <i data-lucide="${c.icon}" class="w-4 h-4"></i>
      <span class="font-medium text-sm">${c.name}</span>
    </div>
  `).join('');
  
  lucide.createIcons();
  window._paletteFiltered = filtered;
}

function runPaletteCommand(idx) {
  const cmd = window._paletteFiltered[idx];
  if (cmd) {
    cmd.action();
    commandPalette.close();
  }
}

/**
 * Messaging & Rendering
 */
async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || sendBtn.disabled) return;

  inputEl.value = '';
  inputEl.style.height = '56px';
  sendBtn.disabled = true;
  
  if (welcomeVisible) {
    messagesEl.innerHTML = '';
    welcomeVisible = false;
  }

  addMessage('user', text);
  showTyping();
  startBlinking();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        model: modelSelect.value,
        session_id: sessionId,
        system: document.getElementById('systemPrompt').value.trim(),
        tool_mode: document.getElementById('toolMode').value,
        agent: agentSelect.value,
        google_search: document.getElementById('googleSearch').checked,
        research_depth: parseInt(document.getElementById('researchDepth').value, 10)
      }),
    });
    
    const data = await res.json();
    removeTyping();

    if (data.tool_steps) {
      renderToolSteps(data.tool_steps);
    }

    addMessage('model', data.reply, data.model);
    
    if (data.session_id) sessionId = data.session_id;
    updateStats(data);
    stopBlinking(data.tool_calls || []);

  } catch (err) {
    removeTyping();
    stopBlinking([]);
    addMessage('system', 'System Error: ' + err.message);
  } finally {
    sendBtn.disabled = false;
  }
}

function addMessage(role, text, meta = '') {
  const div = document.createElement('div');
  const isUser = role === 'user';
  
  if (role === 'system') {
    div.className = 'flex justify-center my-6';
    div.innerHTML = `<span class="badge badge-ghost text-[10px] font-bold uppercase tracking-widest py-3 px-4 opacity-40 border-none bg-base-100/50">${escHtml(text)}</span>`;
    messagesEl.appendChild(div);
    return;
  }

  div.className = `chat ${isUser ? 'chat-end' : 'chat-start'} group animate-in fade-in slide-in-from-bottom-4 duration-500`;
  
  let content;
  if (!isUser) {
    const research = tryParseResearch(text);
    content = research ? renderResearch(research) : renderMd(text);
  } else {
    content = `<p class="whitespace-pre-wrap">${escHtml(text)}</p>`;
  }

  div.innerHTML = `
    <div class="chat-header opacity-50 text-[10px] mb-2 font-bold uppercase tracking-widest flex items-center gap-2">
      ${isUser ? 'Client Terminal' : 'Intelligence Engine'}
      ${meta ? `<span class="opacity-20">|</span> <span class="text-primary font-black opacity-100">${meta}</span>` : ''}
    </div>
    <div class="chat-bubble ${isUser ? 'chat-bubble-primary' : 'bg-base-100'} prose prose-sm">
      ${content}
    </div>
  `;

  messagesEl.appendChild(div);
  scrollMessages();
  Prism.highlightAllUnder(div);
}

function renderToolSteps(steps) {
  const liveActivity = document.getElementById('liveActivity');
  liveActivity.innerHTML = steps.map(step => {
    const hasError = step.calls.some(c => !c.success);
    return `
      <div class="p-3 bg-base-100 border-l-2 ${hasError ? 'border-l-error' : 'border-l-primary'} rounded-xl text-[10px] space-y-2">
        <div class="flex items-center justify-between opacity-60 font-bold uppercase tracking-tighter">
          <span>Round ${step.round}</span>
          <span>${step.calls.length} Executions</span>
        </div>
        ${step.calls.map(c => `
          <div class="flex items-center gap-2">
            <i data-lucide="${TOOL_ICONS[c.tool] || 'settings'}" class="w-3 h-3 ${c.success ? 'text-success' : 'text-error'}"></i>
            <span class="font-mono truncate">${c.tool}</span>
          </div>
        `).join('')}
      </div>
    `;
  }).join('');
  lucide.createIcons();
}

/**
 * Helpers
 */
function escHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function renderMd(text) {
  try { return marked.parse(text); } catch { return escHtml(text); }
}

function scrollMessages() {
  messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: 'smooth' });
}

function showTyping() {
  const div = document.createElement('div');
  div.id = 'typing';
  div.className = 'chat chat-start opacity-50';
  div.innerHTML = `
    <div class="chat-bubble bg-base-100 border border-base-content/5 flex gap-1 items-center py-4 px-6">
      <span class="w-1 h-1 bg-primary rounded-full animate-bounce"></span>
      <span class="w-1 h-1 bg-primary rounded-full animate-bounce [animation-delay:0.2s]"></span>
      <span class="w-1 h-1 bg-primary rounded-full animate-bounce [animation-delay:0.4s]"></span>
    </div>
  `;
  messagesEl.appendChild(div);
  scrollMessages();
  document.getElementById('activityStatus').textContent = 'thinking';
}

function removeTyping() {
  const el = document.getElementById('typing');
  if (el) el.remove();
  document.getElementById('activityStatus').textContent = 'idle';
}

function updateStats(data) {
  const tokens = (data.input_tokens || 0) + (data.output_tokens || 0);
  totalTokens += tokens;
  msgCount++;
  
  document.getElementById('statMessages').textContent = msgCount;
  document.getElementById('statTokens').textContent = totalTokens.toLocaleString();
  document.getElementById('statToolCalls').textContent = totalToolCalls += (data.tool_calls ? data.tool_calls.length : 0);
  document.getElementById('statLatency').textContent = `${data.latency_ms.toFixed(0)}ms`;
  document.getElementById('modelBadge').textContent = data.model;
}

function startBlinking() {
  document.getElementById('activityStatus').classList.add('heartbeat');
}

function stopBlinking() {
  document.getElementById('activityStatus').classList.remove('heartbeat');
}

async function initData() {
  try {
    const [agents, tools] = await Promise.all([
      fetch('/api/agents').then(r => r.json()),
      fetch('/api/tools').then(r => r.json())
    ]);

    document.getElementById('agentsList').innerHTML = agents.agents.map(a => `
      <div class="flex justify-between items-center py-2 border-b border-base-content/5 last:border-0">
        <span class="text-[11px] font-medium opacity-80">${a.name}</span>
        <div class="w-1.5 h-1.5 rounded-full bg-base-300" id="agent-chip-${a.name}"></div>
      </div>
    `).join('');

    document.getElementById('toolsList').innerHTML = tools.tools.map(t => `
      <div class="flex items-center gap-2 py-2">
        <i data-lucide="${TOOL_ICONS[t.name] || 'settings'}" class="w-3 h-3 opacity-40"></i>
        <span class="text-[11px] font-mono opacity-60 flex-1 truncate">${t.name}</span>
      </div>
    `).join('');
    
    lucide.createIcons();
  } catch {}
}

function tryParseResearch(text) {
  let json = text;
  const match = text.match(/```json\s*([\s\S]*?)```/);
  if (match) json = match[1].trim();
  try {
    const data = JSON.parse(json);
    if (data.key_findings) return data;
  } catch {}
  return null;
}

function renderResearch(data) {
  lastResearchFindings = data.key_findings || [];
  return `
    <div class="space-y-6">
      <div class="bg-primary/5 p-6 rounded-3xl border border-primary/10">
        <h2 class="text-xl font-black tracking-tight text-primary mb-2">${escHtml(data.title || 'Analysis Results')}</h2>
        <p class="text-sm leading-relaxed opacity-70">${escHtml(data.summary || '')}</p>
      </div>
      <div class="grid gap-3">
        ${data.key_findings.map((f, i) => `
          <div class="collapse bg-base-200/50 border border-base-content/5 rounded-2xl transition-all hover:bg-base-200">
            <input type="checkbox" /> 
            <div class="collapse-title text-sm font-bold flex items-center gap-3">
              <span class="badge badge-primary badge-outline badge-xs font-black">${i+1}</span>
              ${escHtml(f.headline)}
            </div>
            <div class="collapse-content text-xs opacity-70 leading-relaxed">
              ${renderMd(f.detail)}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

async function clearChat() {
  location.reload();
}

function closeReport() {
  const reportOverlay = document.getElementById('reportOverlay');
  reportOverlay.classList.remove('opacity-100');
  setTimeout(() => reportOverlay.classList.add('hidden'), 500);
}

async function exportReport() {
  if (!sessionId) return alert('No active session. Send a message first.');
  
  const reportOverlay = document.getElementById('reportOverlay');
  const reportContent = document.getElementById('reportContent');
  const reportActions = document.getElementById('reportActions');
  const reportTitle = document.getElementById('reportTitle');

  reportOverlay.classList.remove('hidden');
  setTimeout(() => reportOverlay.classList.add('opacity-100'), 10);
  reportContent.innerHTML = `
    <div class="flex flex-col items-center justify-center py-20 gap-6">
      <span class="loading loading-ring loading-lg text-primary"></span>
      <div class="text-center">
        <p class="font-black uppercase tracking-[0.2em] text-xs opacity-40">Intelligence Synthesis</p>
        <p class="text-sm opacity-60">Compiling multi-source research data...</p>
      </div>
    </div>
  `;

  try {
    const res = await fetch('/api/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, title: '' }),
    });
    const data = await res.json();

    if (data.error) throw new Error(data.error);

    reportTitle.textContent = `Research Synthesis (${data.total_sources} Sources)`;
    reportContent.innerHTML = renderMd(data.report);
    
    reportActions.innerHTML = `
      <button class="btn btn-sm btn-ghost gap-2" onclick="navigator.clipboard.writeText(\`${data.report.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`); this.innerHTML='<i data-lucide=&quot;check&quot; class=&quot;w-4 h-4&quot;></i> Copied!'">
        <i data-lucide="copy" class="w-4 h-4"></i> Copy
      </button>
      <button class="btn btn-sm btn-primary gap-2" onclick="downloadReport(\`${data.report.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">
        <i data-lucide="download" class="w-4 h-4"></i> Download .md
      </button>
    `;
    lucide.createIcons();
  } catch (err) {
    reportContent.innerHTML = `
      <div class="alert alert-error bg-error/10 border-error/20 text-error rounded-3xl p-8">
        <i data-lucide="alert-circle" class="w-8 h-8"></i>
        <div>
          <h3 class="font-bold">Synthesis Failed</h3>
          <p class="text-sm opacity-80">${err.message}</p>
        </div>
      </div>
    `;
    lucide.createIcons();
  }
}
