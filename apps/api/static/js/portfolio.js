/**
 * Portfolio Site — Chat Panel Logic
 */

let sessionId = '';
let chatOpen = false;

const chatPanel = document.getElementById('chatPanel');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatToggle = document.getElementById('chatToggle');

function toggleChat() {
  chatOpen = !chatOpen;
  chatPanel.classList.toggle('open', chatOpen);
  if (chatOpen) chatInput.focus();
}

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

function startChat(audience) {
  toggleChat();
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

document.addEventListener('DOMContentLoaded', () => {
  chatToggle.addEventListener('click', toggleChat);
  chatSendBtn.addEventListener('click', sendChat);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChat();
    }
  });
});
