// --- User & Message Data ---
let myUsername = typeof username !== "undefined" ? username : "Me";

// Fetch and render messages
async function fetchMessages() {
  let resp = await fetch('/messages');
  let data = await resp.json();
  renderMessages(data.messages);
  scrollMessagesToBottom();
}
function escapeHTML(str) {
  return String(str).replace(/[&<>"']/g, function (m) {
    return ({'&': '&amp;','<': '&lt;','>': '&gt;','"': '&quot;',"'": '&#39;'})[m];
  });
}
function renderMessages(messages) {
  const msgSection = document.getElementById('messages');
  if (!messages.length) {
    msgSection.innerHTML = "<div style='color:#7494ec;text-align:center;margin-top:2em;'>No messages yet.</div>";
    return;
  }
  msgSection.innerHTML = messages.map(msg => `
    <div class="message-row ${msg.sender === myUsername ? "right_aligned" : "left_aligned"}">
      <div class="message-bubble">
        ${escapeHTML(msg.content)}
        <div class="message-options">
          <button title="Reply">↩️</button>
          <button title="Delete">🗑️</button>
        </div>
      </div>
      <div class="message-meta">
        <span>${escapeHTML(msg.sender)}</span>
        <span>${escapeHTML(msg.timestamp || "")}</span>
      </div>
    </div>
  `).join('');
}
function scrollMessagesToBottom() {
  const msgSection = document.getElementById('messages');
  setTimeout(() => msgSection.scrollTop = msgSection.scrollHeight, 30);
}
// Send a message
async function sendMessage() {
  const input = document.getElementById('message-input');
  let content = input.value.trim();
  if(!content) return;
  let now = new Date();
  let timestamp = now.toTimeString().slice(0,5);
  let resp = await fetch('/send', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({message: content, timestamp})
  });
  input.value = '';
  await fetchMessages();
}
// Emoji picker (demo)
document.querySelector('.emoji-btn').addEventListener('click', () => {
  const input = document.getElementById('message-input');
  input.value += '😊';
  input.focus();
});
// File upload (demo, not sent to backend)
document.getElementById('file-upload').addEventListener('change', function(e) {
  alert("File upload is a UI only demo. Use drag & drop for metadata.");
  this.value = "";
});
// Dark mode toggle (demo, background only)
document.getElementById('toggle-dark-mode').addEventListener('change', function() {
  document.body.style.background = this.checked ? "linear-gradient(90deg, #e2e2e2, #c9d6ff)" : "#232338";
});
// Send button & Enter key
document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('message-input').addEventListener('keydown', function(e) {
  if(e.key === 'Enter') sendMessage();
});
// Drag & Drop Metadata
const dropArea = document.getElementById('drop-area');
const result = document.getElementById('result');
['dragenter', 'dragover'].forEach(eventName =>
  dropArea.addEventListener(eventName, (e) => {
    e.preventDefault(); e.stopPropagation();
    dropArea.classList.add('highlight');
  }, false)
);
['dragleave', 'drop'].forEach(eventName =>
  dropArea.addEventListener(eventName, (e) => {
    e.preventDefault(); e.stopPropagation();
    dropArea.classList.remove('highlight');
  }, false)
);
dropArea.addEventListener('drop', async (e) => {
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    const metadata = { name: file.name, type: file.type, size: file.size };
    let resp = await fetch('/file-metadata', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(metadata)
    });
    let data = await resp.json();
    result.innerText = `Metadata sent! Received:\n${JSON.stringify(data.received, null, 2)}`;
  }
});
// Logout
document.getElementById('logout-form').addEventListener('submit', async function(e){
  e.preventDefault();
  await fetch('/logout', {method:'POST'});
  window.location.href = "/";
});
// Initial load and polling
fetchMessages();
setInterval(fetchMessages, 2500);