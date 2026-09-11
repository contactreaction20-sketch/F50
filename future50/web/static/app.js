const state = { generating: false, sessionId: localStorage.getItem('future50-session') || crypto.randomUUID(), bookmarks: JSON.parse(localStorage.getItem('future50-bookmarks') || '[]'), abortController: null };
localStorage.setItem('future50-session', state.sessionId);
const messages = document.querySelector('#messages');
const welcome = document.querySelector('#welcome');
const input = document.querySelector('#messageInput');
const form = document.querySelector('#composer');
const sendButton = document.querySelector('#sendButton');
const toneSelect = document.querySelector('#toneSelect');
const modelSelect = document.querySelector('#modelSelect');
const notice = document.querySelector('#notice');

function scrollMessages() { messages.scrollTo({ top: messages.scrollHeight, behavior: 'smooth' }); }
function addMessage(role, text, actions = true) {
  welcome.style.display = 'none';
  const item = document.createElement('article');
  item.className = `message ${role}`;
  const avatar = role === 'user' ? 'You' : 'F';
  item.innerHTML = `<div class="avatar">${avatar}</div><div class="message-body"><p class="message-name">${role === 'user' ? 'You' : 'FUTURE-50'}</p><p class="message-text"></p>${actions ? '<div class="message-actions"><button data-action="copy">Copy</button><button data-action="edit">Edit</button><button data-action="share">Share</button></div>' : ''}</div>`;
  item.querySelector('.message-text').textContent = text;
  messages.appendChild(item);
  scrollMessages();
  return item;
}
function addThinking() {
  const item = document.createElement('article');
  item.className = 'message assistant thinking-row';
  item.innerHTML = '<div class="avatar">F</div><div class="message-body"><p class="message-name">FUTURE-50</p><span class="thinking"><i></i> Thinking about your request<span class="thinking-dots">...</span></span></div>';
  messages.appendChild(item);
  scrollMessages();
  return item;
}
function streamReply(item, text) {
  const target = item.querySelector('.message-text');
  let index = 0;
  const step = () => {
    target.textContent += text[index++] || '';
    scrollMessages();
    if (index < text.length) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
async function streamMessage(item, value) {
  const target = item.querySelector('.message-text');
  state.abortController = new AbortController();
  const response = await fetch('/api/chat/stream', { method: 'POST', signal: state.abortController.signal, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: value, tone: toneSelect.value, model: modelSelect.value, session_id: state.sessionId }) });
  if (!response.ok || !response.body) throw new Error('The local service is unavailable.');
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let pendingText = '';
  let paintScheduled = false;
  const paint = () => {
    target.textContent += pendingText;
    pendingText = '';
    paintScheduled = false;
    scrollMessages();
  };
  while (true) {
    const result = await reader.read();
    if (result.done) break;
    buffer += decoder.decode(result.value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() || '';
    for (const event of events) {
      if (!event.startsWith('data: ')) continue;
      const payload = JSON.parse(event.slice(6));
      if (payload.error) throw new Error(payload.error);
      if (payload.done) {
        await reader.cancel();
        buffer = '';
        if (pendingText) paint();
        return;
      }
      if (payload.token) {
        pendingText += payload.token;
        if (!paintScheduled) {
          paintScheduled = true;
          requestAnimationFrame(paint);
        }
      }
    }
  }
  if (pendingText) paint();
}
async function sendMessage(value = input.value.trim()) {
  if (state.generating) {
    state.abortController?.abort();
    state.generating = false;
    sendButton.textContent = '↗';
    sendButton.classList.remove('stop-state');
    return;
  }
  if (!value) return;
  state.generating = true;
  input.value = '';
  addMessage('user', value);
  sendButton.textContent = '■';
  sendButton.classList.add('stop-state');
  const thinking = addThinking();
  const started = Date.now();
  try {
    const assistant = addMessage('assistant', '', false);
    thinking.remove();
    await streamMessage(assistant, value);
    assistant.querySelector('.message-body').insertAdjacentHTML('beforeend', '<div class="message-actions"><button data-action="copy">Copy</button><button data-action="share">Share</button></div>');
  } catch (error) {
    thinking.remove();
    if (error.name !== 'AbortError') addMessage('assistant', error.message || 'The local service is unavailable.');
  } finally {
    state.generating = false;
    state.abortController = null;
    sendButton.textContent = '↗';
    sendButton.classList.remove('stop-state');
    input.focus();
    void (Date.now() - started);
  }
}
form.addEventListener('submit', event => { event.preventDefault(); sendMessage(); });
input.addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); sendMessage(); } });
document.querySelector('#suggestions').addEventListener('click', event => { const prompt = event.target.closest('[data-prompt]'); if (prompt) sendMessage(prompt.dataset.prompt); });
document.querySelector('#newChat').addEventListener('click', () => { messages.innerHTML = ''; welcome.style.display = ''; state.sessionId = crypto.randomUUID(); localStorage.setItem('future50-session', state.sessionId); input.focus(); });
document.querySelector('#closeNotice').addEventListener('click', () => { notice.classList.add('closed'); setTimeout(() => notice.remove(), 280); });
document.querySelector('#startFeedback').addEventListener('click', () => window.alert('Thanks. Feedback flow is ready for your note.'));
document.querySelector('#bookmark').addEventListener('click', event => { state.bookmarks.push(new Date().toISOString()); localStorage.setItem('future50-bookmarks', JSON.stringify(state.bookmarks)); event.currentTarget.textContent = '★'; });
document.querySelector('#feedback').addEventListener('click', () => window.alert('Tell us what could be improved in this answer.'));
document.querySelector('#attachment').addEventListener('change', event => { const file = event.target.files[0]; if (file) document.querySelector('#attachmentHint').textContent = file.name; });
document.querySelector('#mic').addEventListener('click', () => { const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition; if (!SpeechRecognition) return window.alert('Voice input is not available in this browser.'); const recognition = new SpeechRecognition(); recognition.onresult = event => { input.value = event.results[0][0].transcript; input.focus(); }; recognition.start(); });
messages.addEventListener('click', event => { const button = event.target.closest('[data-action]'); if (!button) return; const item = button.closest('.message'); const text = item.querySelector('.message-text').textContent; if (button.dataset.action === 'copy') navigator.clipboard?.writeText(text); if (button.dataset.action === 'share') navigator.share?.({ title: 'FUTURE-50', text }).catch(() => navigator.clipboard?.writeText(text)); if (button.dataset.action === 'edit') { input.value = text; input.focus(); } button.textContent = button.dataset.action === 'copy' ? 'Copied' : 'Done'; setTimeout(() => { button.textContent = button.dataset.action[0].toUpperCase() + button.dataset.action.slice(1); }, 900); });
