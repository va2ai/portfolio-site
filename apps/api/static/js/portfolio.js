/**
 * Portfolio Site — Chat Panel & Interactions
 */

let sessionId = '';
let chatOpen = false;

const chatPanel = document.getElementById('chatPanel');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatToggle = document.getElementById('chatToggle');

// Toggle chat panel
function toggleChat() {
  chatOpen = !chatOpen;
  chatPanel.classList.toggle('open', chatOpen);
  if (chatOpen) {
    chatInput.focus();
    chatToggle.style.transform = 'scale(0)';
  } else {
    chatToggle.style.transform = 'scale(1)';
  }
}

// Send message
async function sendChat() {
  const text = chatInput.value.trim();
  if (!text || chatSendBtn.disabled) return;

  chatInput.value = '';
  chatSendBtn.disabled = true;

  addChatMsg('user', text);
  showTyping();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        session_id: sessionId,
      }),
    });

    const data = await res.json();
    removeTyping();

    if (data.session_id) sessionId = data.session_id;
    addChatMsg('agent', data.reply);
  } catch (err) {
    removeTyping();
    addChatMsg('agent', 'Connection error. Please try again.');
  } finally {
    chatSendBtn.disabled = false;
  }
}

function addChatMsg(role, text) {
  const div = document.createElement('div');
  div.className = `chat-msg ${role}`;

  if (role === 'agent') {
    try {
      div.innerHTML = marked.parse(text);
    } catch {
      div.textContent = text;
    }
  } else {
    div.textContent = text;
  }

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping() {
  const div = document.createElement('div');
  div.id = 'typingIndicator';
  div.className = 'typing-dots';
  div.innerHTML = '<span></span><span></span><span></span>';
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

// Audience quick-start
function startChat(audience) {
  if (!chatOpen) toggleChat();
  let greeting = '';
  if (audience === 'recruiter') {
    greeting = "Hi, I'm a recruiter. Tell me about Chris's experience and what makes him stand out.";
  } else if (audience === 'client') {
    greeting = "Hi, I'm looking for someone to help me build an AI-powered application. What can Chris do for me?";
  }
  if (greeting) {
    chatInput.value = greeting;
    sendChat();
  }
}

// Scroll Animations
function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}

// ─── ElevenLabs Voice Agent — Client-Side Tool Handlers ─────────────

const PORTFOLIO_LINKS = {
  v2v_platform: 'https://vaclaims-194006.web.app',
  github: 'https://github.com/va2ai',
  portfolio_site: window.location.origin,
  bva_api: 'https://bva-api-301313738047.us-central1.run.app',
};

function initElevenLabsWidget() {
  const widget = document.querySelector('elevenlabs-convai');
  if (!widget) return;

  widget.addEventListener('elevenlabs-convai:call', (event) => {
    event.detail.config.clientTools = {
      collect_contact_info: async (params) => {
        fetch('/api/leads', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...params,
            source: 'elevenlabs_voice_agent',
          }),
        }).catch(err => console.error('Lead capture failed:', err));
        return 'Contact information saved. Chris will follow up.';
      },
      schedule_callback: async (params) => {
        fetch('/api/leads', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...params,
            lead_type: 'callback_request',
            source: 'elevenlabs_voice_agent',
          }),
        }).catch(err => console.error('Callback request failed:', err));
        return 'Callback request sent. Chris will reach out to confirm a time.';
      },
      open_portfolio_link: async (params) => {
        const url = PORTFOLIO_LINKS[params.link_type];
        if (url) {
          window.open(url, '_blank');
          return `Opened ${params.link_type} in a new tab.`;
        }
        return 'Link not found.';
      },
      notify_chris: async (params) => {
        fetch('/api/leads', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: 'Voice Agent Notification',
            topic: params.summary,
            priority: params.priority || 'normal',
            lead_type: 'notification',
            source: 'elevenlabs_voice_agent',
          }),
        }).catch(err => console.error('Notification failed:', err));
        return 'Chris has been notified.';
      },
    };
  });
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  chatToggle.addEventListener('click', toggleChat);
  chatSendBtn.addEventListener('click', sendChat);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChat();
    }
  });

  initScrollReveal();
  initElevenLabsWidget();
});
