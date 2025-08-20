// Chat Application JavaScript - Backend Ready with File Upload and Emoji Picker

// Application Data Variables (Empty - ready for backend)
let contacts = [];
let quickContacts = [];
let currentChatId = null;
let messageHistory = {};
let selectedFile = null;

let userProfile = {
  id: null,
  name: "",
  avatar: ""
};

// Emoji data
const emojiData = {
  smileys: ['😀','😃','😄','😁','😆','😅','😂','🤣','😊','😇','🙂','🙃','😉','😌','😍','🥰','😘','😗','😙','😚','😋','😛','😝','😜','🤪','🤨','🧐','🤓','😎','🤩','🥳','😏','😒','😞','😔','😟','😕','🙁','😣','😖','😫','😩','🥺','😢','😭','😤','😠','😡','🤬','🤯','😳','🥵','🥶','😱','😨','😰','😥','😓','🤗','🤔','🤭','🤫','🤥','😶','😐','😑','😬','🙄','😯','😦','😧','😮','😲'],
  animals: ['🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐨','🐯','🦁','🐮','🐷','🐽','🐸','🐵','🙈','🙉','🙊','🐒','🐔','🐧','🐦','🐤','🐣','🐥','🦆','🦅','🦉','🦇','🐺','🐗','🐴','🦄','🐝','🐛','🦋','🐌','🐞','🐜','🦟','🦗','🕷️','🕸️','🦂','🐢','🐍','🦎','🦖','🦕','🐙','🦑','🦐','🦞','🦀','🐡','🐠','🐟','🐬','🐳','🐋','🦈','🐊','🐅','🐆','🦓','🦍','🦧','🐘','🦛','🦏','🐪','🐫','🦒','🦘','🐃','🐂','🐄','🐎','🐖','🐏','🐑','🦙','🐐','🦌','🐕','🐩','🦮','🐕‍🦺','🐈','🐓','🦃','🦚','🦜','🦢','🦩','🕊️','🐇','🦝','🦨','🦡','🦦','🦥','🐁','🐀','🐿️','🦔'],
  food: ['🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🫐','🍈','🍒','🍑','🥭','🍍','🥥','🥝','🍅','🍆','🥑','🥦','🥬','🥒','🌶️','🫑','🌽','🥕','🫒','🧄','🧅','🥔','🍠','🥐','🥯','🍞','🥖','🥨','🧀','🥚','🍳','🧈','🥞','🧇','🥓','🥩','🍗','🍖','🦴','🌭','🍔','🍟','🍕','🫓','🥙','🌮','🌯','🫔','🥗','🥘','🫕','🥫','🍝','🍜','🍲','🍛','🍣','🍱','🥟','🦪','🍤','🍙','🍚','🍘','🍥','🥠','🥮','🍢','🍡','🍧','🍨','🍦','🥧','🧁','🍰','🎂','🍮','🍭','🍬','🍫','🍿','🍩','🍪','🌰','🥜','🍯'],
  activities: ['⚽','🏀','🏈','⚾','🥎','🎾','🏐','🏉','🥏','🎱','🪀','🏓','🏸','🏒','🏑','🥍','🏏','🪃','🥅','⛳','🪁','🏹','🎣','🤿','🥊','🥋','🎽','🛹','🛷','⛸️','🥌','🎿','⛷️','🏂','🪂','🏋️‍♀️','🏋️','🤼‍♀️','🤼','🤸‍♀️','🤸','⛹️‍♀️','⛹️','🤺','🤾‍♀️','🤾','🏌️‍♀️','🏌️','🏇','🧘‍♀️','🧘','🏄‍♀️','🏄','🏊‍♀️','🏊','🤽‍♀️','🤽','🚣‍♀️','🚣','🧗‍♀️','🧗','🚵‍♀️','🚵','🚴‍♀️','🚴','🏆','🥇','🥈','🥉','🏅','🎖️','🏵️','🎗️'],
  travel: ['🚗','🚕','🚙','🚌','🚎','🏎️','🚓','🚑','🚒','🚐','🛻','🚚','🚛','🚜','🏍️','🛵','🚲','🛴','🛹','🛼','🚁','🛸','🚀','✈️','🛩️','🛫','🛬','🪂','💺','🚢','⛵','🚤','🛥️','🛳️','⛴️','🚟','🚠','🚡','🚂','🚃','🚄','🚅','🚆','🚇','🚈','🚉','🚊','🚝','🚞','🚋','🚌','🚍','🎡','🎢','🎠','🏗️','🌁','🗼','🏭','⛲','🎑','⛰️','🏔️','🗻','🌋','🏕️','🏞️','🏜️','🏖️','⛱️','🏝️','🌊'],
  objects: ['💡','🔦','🕯️','🪔','🧯','🛢️','💸','💵','💴','💶','💷','💰','💳','💎','⚖️','🔧','🔨','⚒️','🛠️','⛏️','🔩','⚙️','🧱','⛓️','🧲','🔫','💣','🧨','🔪','🗡️','⚔️','🛡️','🚬','⚰️','⚱️','🏺','🔮','📿','💈','⚗️','🔭','🔬','🕳️','💊','💉','🩸','🧬','🦠','🧫','🧪','🌡️','🧹','🧺','🧻','🚽','🚰','🚿','🛁','🛀','🧼','🪒','🧽','🧴','🛎️','🔑','🗝️','🚪','🛏️','🛋️','🪑','🚂','🧸','🖼️','🛍️','🛒','🎁','🎈','🎏','🎀','🎊','🎉','🪅','🪆','🎎','🏮','🎐','🧧'],
  symbols: ['❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','❣️','💕','💞','💓','💗','💖','💘','💝','💟','☮️','✝️','☪️','🕉️','☸️','✡️','🔯','🕎','☯️','☦️','🛐','⛎','♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓','🆔','⚛️','🉑','☢️','☣️','📴','📳','🈶','🈚','🈸','🈺','🈷️','✴️','🆚','💮','🉐','㊙️','㊗️','🈴','🈵','🈹','🈲','🅰️','🅱️','🆎','🆑','🅾️','🆘','❌','⭕','🛑','⛔','📛','🚫','💯','💢','♨️','🚷','🚯','🚳','🚱','🔞','📵','🚭']
};

// Empty states configuration
const emptyStates = {
  noChats: "No conversations yet",
  noChatSelected: "Select a chat to start messaging",
  noContacts: "No contacts available"
};

// DOM Elements
let chatListElement, quickContactsListElement, messagesListElement;
let currentContactAvatar, currentContactName, onlineStatus, onlineIndicator;
let messageInput, sendButton, searchInput, themeToggle;
let emptyChatsState, emptyChatState;
let attachmentButton, fileInput, emojiButton, emojiPicker;
let filePreview, fileRemove;

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
  initializeElements();
  initializeTheme();
  initializeEmptyStates();
  initializeEmojiPicker();
  setupEventListeners();
  
  // Show empty states initially
  showEmptyChatsState();
  showEmptyChatState();
});

function initializeElements() {
  chatListElement = document.getElementById('chatList');
  quickContactsListElement = document.getElementById('quickContactsList');
  messagesListElement = document.getElementById('messagesList');
  currentContactAvatar = document.getElementById('currentContactAvatar');
  currentContactName = document.getElementById('currentContactName');
  onlineStatus = document.getElementById('onlineStatus');
  onlineIndicator = document.getElementById('onlineIndicator');
  messageInput = document.getElementById('messageInput');
  sendButton = document.getElementById('sendButton');
  searchInput = document.getElementById('searchInput');
  themeToggle = document.getElementById('themeToggle');
  emptyChatsState = document.getElementById('emptyChatsState');
  emptyChatState = document.getElementById('emptyChatState');
  attachmentButton = document.getElementById('attachmentButton');
  fileInput = document.getElementById('fileInput');
  emojiButton = document.getElementById('emojiButton');
  emojiPicker = document.getElementById('emojiPicker');
  filePreview = document.getElementById('filePreview');
  fileRemove = document.getElementById('fileRemove');
}

function initializeTheme() {
  // Check for saved theme preference or default to 'dark'
  const savedTheme = localStorage.getItem('chat-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
}

function initializeEmptyStates() {
  // Update empty state text from configuration
  const chatEmptyTitle = emptyChatState?.querySelector('h3');
  const chatEmptyDesc = emptyChatState?.querySelector('p');
  
  if (chatEmptyTitle) chatEmptyTitle.textContent = emptyStates.noChatSelected;
  if (chatEmptyDesc) chatEmptyDesc.textContent = "Choose a conversation from the sidebar to view messages";
}

function initializeEmojiPicker() {
  const emojiPickerContent = document.getElementById('emojiPickerContent');
  if (!emojiPickerContent) return;
  
  // Load default category (smileys)
  loadEmojiCategory('smileys');
  
  // Setup category buttons
  const categoryButtons = document.querySelectorAll('.emoji-category');
  categoryButtons.forEach(button => {
    button.addEventListener('click', () => {
      categoryButtons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      loadEmojiCategory(button.dataset.category);
    });
  });
}

function loadEmojiCategory(category) {
  const emojiPickerContent = document.getElementById('emojiPickerContent');
  if (!emojiPickerContent) return;
  
  emojiPickerContent.innerHTML = '';
  const emojis = emojiData[category] || emojiData.smileys;
  
  emojis.forEach(emoji => {
    const emojiElement = document.createElement('div');
    emojiElement.className = 'emoji';
    emojiElement.textContent = emoji;
    emojiElement.addEventListener('click', () => insertEmoji(emoji));
    emojiPickerContent.appendChild(emojiElement);
  });
}

function insertEmoji(emoji) {
  if (!messageInput) return;
  
  const cursorPos = messageInput.selectionStart;
  const textBefore = messageInput.value.substring(0, cursorPos);
  const textAfter = messageInput.value.substring(messageInput.selectionEnd);
  
  messageInput.value = textBefore + emoji + textAfter;
  messageInput.focus();
  messageInput.setSelectionRange(cursorPos + emoji.length, cursorPos + emoji.length);
  
  // Hide emoji picker
  hideEmojiPicker();
}

function showEmojiPicker() {
  if (emojiPicker) {
    emojiPicker.style.display = 'block';
  }
}

function hideEmojiPicker() {
  if (emojiPicker) {
    emojiPicker.style.display = 'none';
  }
}

function setupEventListeners() {
  // Theme toggle
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }
  
  // Send message
  if (sendButton) {
    sendButton.addEventListener('click', handleSendMessage);
  }
  
  // Enter key to send message
  if (messageInput) {
    messageInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    });
  }
  
  // Search functionality
  if (searchInput) {
    searchInput.addEventListener('input', handleSearch);
  }
  
  // File attachment
  if (attachmentButton && fileInput) {
    attachmentButton.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
  }
  
  // File remove
  if (fileRemove) {
    fileRemove.addEventListener('click', removeSelectedFile);
  }
  
  // Emoji picker
  if (emojiButton) {
    emojiButton.addEventListener('click', (e) => {
      e.stopPropagation();
      const isVisible = emojiPicker.style.display === 'block';
      if (isVisible) {
        hideEmojiPicker();
      } else {
        showEmojiPicker();
      }
    });
  }
  
  // Close emoji picker when clicking outside
  document.addEventListener('click', (e) => {
    if (emojiPicker && !emojiPicker.contains(e.target) && e.target !== emojiButton) {
      hideEmojiPicker();
    }
  });
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('chat-theme', newTheme);
  
  // Add a subtle animation effect
  if (themeToggle) {
    themeToggle.style.transform = 'scale(0.8)';
    setTimeout(() => {
      themeToggle.style.transform = 'scale(1)';
    }, 150);
  }
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  selectedFile = file;
  showFilePreview(file);
}

function showFilePreview(file) {
  if (!filePreview) return;
  
  const fileName = filePreview.querySelector('.file-name');
  const fileSize = filePreview.querySelector('.file-size');
  const fileIcon = filePreview.querySelector('.file-icon');
  
  if (fileName) fileName.textContent = file.name;
  if (fileSize) fileSize.textContent = formatFileSize(file.size);
  
  // Set appropriate icon based on file type
  if (fileIcon) {
    if (file.type.startsWith('image/')) {
      fileIcon.className = 'file-icon fas fa-image';
    } else if (file.type.startsWith('video/')) {
      fileIcon.className = 'file-icon fas fa-video';
    } else if (file.type.startsWith('audio/')) {
      fileIcon.className = 'file-icon fas fa-music';
    } else if (file.type.includes('pdf')) {
      fileIcon.className = 'file-icon fas fa-file-pdf';
    } else if (file.type.includes('document') || file.type.includes('word')) {
      fileIcon.className = 'file-icon fas fa-file-word';
    } else {
      fileIcon.className = 'file-icon fas fa-file';
    }
  }
  
  filePreview.style.display = 'block';
}

function removeSelectedFile() {
  selectedFile = null;
  if (fileInput) fileInput.value = '';
  if (filePreview) filePreview.style.display = 'none';
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function handleSendMessage() {
  const messageText = messageInput?.value.trim();
  
  if ((!messageText && !selectedFile) || !currentChatId) return;
  
  const newMessage = {
    id: Date.now(),
    senderId: "me",
    text: messageText || '',
    timestamp: new Date().toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    }),
    type: "sent",
    file: selectedFile ? {
      name: selectedFile.name,
      size: selectedFile.size,
      type: selectedFile.type,
      url: URL.createObjectURL(selectedFile) // For preview only
    } : null
  };
  
  // Add message to history
  if (!messageHistory[currentChatId]) {
    messageHistory[currentChatId] = [];
  }
  messageHistory[currentChatId].push(newMessage);
  
  // Clear input and file
  if (messageInput) messageInput.value = '';
  removeSelectedFile();
  
  // Update UI
  displayMessages();
  
  // Here you would typically send the message to your backend
  console.log('Message sent:', newMessage);
}

function showEmptyChatsState() {
  if (emptyChatsState && chatListElement) {
    if (contacts.length === 0) {
      emptyChatsState.style.display = 'flex';
      chatListElement.style.display = 'none';
    } else {
      emptyChatsState.style.display = 'none';
      chatListElement.style.display = 'flex';
    }
  }
}

function showEmptyChatState() {
  if (emptyChatState && messagesListElement) {
    if (currentChatId === null) {
      emptyChatState.style.display = 'flex';
      messagesListElement.style.display = 'none';
    } else {
      emptyChatState.style.display = 'none';
      messagesListElement.style.display = 'flex';
    }
  }
}

function handleSearch() {
  const searchTerm = searchInput?.value.toLowerCase() || '';
  const chatItems = document.querySelectorAll('.chat-item');
  
  chatItems.forEach(item => {
    const name = item.querySelector('.chat-name')?.textContent.toLowerCase() || '';
    const message = item.querySelector('.chat-message')?.textContent.toLowerCase() || '';
    
    if (name.includes(searchTerm) || message.includes(searchTerm)) {
      item.style.display = 'flex';
    } else {
      item.style.display = 'none';
    }
  });
}

// Backend Integration Functions (Ready to be implemented)

function loadContactsFromBackend(contactsData) {
  contacts = contactsData;
  renderContactsList();
  showEmptyChatsState();
}

function loadQuickContactsFromBackend(quickContactsData) {
  quickContacts = quickContactsData;
  renderQuickContacts();
}

function addNewContact(contactData) {
  contacts.push(contactData);
  renderContactsList();
  showEmptyChatsState();
}

function updateMessageHistory(chatId, messages) {
  messageHistory[chatId] = messages;
  if (chatId === currentChatId) {
    displayMessages();
  }
}

function setCurrentChat(contactId) {
  currentChatId = contactId;
  const contact = contacts.find(c => c.id === contactId);
  
  if (contact) {
    updateChatHeader(contact);
    displayMessages();
    showEmptyChatState();
    
    // Mark chat as active in sidebar
    document.querySelectorAll('.chat-item').forEach(item => {
      item.classList.remove('active');
      if (item.dataset.contactId == contactId) {
        item.classList.add('active');
      }
    });
  }
}

function addNewMessage(chatId, messageData) {
  if (!messageHistory[chatId]) {
    messageHistory[chatId] = [];
  }
  messageHistory[chatId].push(messageData);
  
  if (chatId === currentChatId) {
    displayMessages();
  }
  
  // Update last message in contacts list
  const contact = contacts.find(c => c.id === chatId);
  if (contact) {
    contact.lastMessage = messageData.text || 'File';
    contact.timestamp = messageData.timestamp;
    renderContactsList();
  }
}

function renderContactsList() {
  if (!chatListElement) return;
  
  chatListElement.innerHTML = '';
  
  contacts.forEach(contact => {
    const chatItem = document.createElement('div');
    chatItem.className = 'chat-item';
    chatItem.dataset.contactId = contact.id;
    
    chatItem.innerHTML = `
      <div class="chat-avatar">
        <img src="${contact.avatar}" alt="${contact.name}">
        ${contact.isOnline ? '<div class="online-indicator"></div>' : ''}
      </div>
      <div class="chat-info">
        <div class="chat-name">${contact.name}</div>
        <div class="chat-message">${contact.lastMessage}</div>
      </div>
      <div class="chat-meta">
        <div class="chat-time">${contact.timestamp}</div>
        ${contact.unreadCount > 0 ? `<div class="chat-unread">${contact.unreadCount}</div>` : ''}
      </div>
    `;
    
    chatItem.addEventListener('click', () => setCurrentChat(contact.id));
    chatListElement.appendChild(chatItem);
  });
}

function renderQuickContacts() {
  if (!quickContactsListElement) return;
  
  quickContactsListElement.innerHTML = '';
  
  quickContacts.forEach(contact => {
    const quickContact = document.createElement('div');
    quickContact.className = 'quick-contact';
    
    quickContact.innerHTML = `
      <div class="quick-contact-avatar">
        <img src="${contact.avatar}" alt="${contact.name}">
      </div>
      <div class="quick-contact-name">${contact.name}</div>
    `;
    
    if (contact.contactId) {
      quickContact.addEventListener('click', () => setCurrentChat(contact.contactId));
    }
    
    quickContactsListElement.appendChild(quickContact);
  });
}

function updateChatHeader(contact) {
  if (currentContactName) currentContactName.textContent = contact.name;
  if (onlineStatus) onlineStatus.textContent = contact.isOnline ? 'Online' : 'Last seen recently';
  
  if (currentContactAvatar) {
    currentContactAvatar.src = contact.avatar;
    currentContactAvatar.alt = contact.name;
    currentContactAvatar.style.display = 'block';
  }
  
  if (onlineIndicator) {
    onlineIndicator.style.display = contact.isOnline ? 'block' : 'none';
  }
}

function displayMessages() {
  if (!messagesListElement || !currentChatId) return;
  
  messagesListElement.innerHTML = '';
  const messages = messageHistory[currentChatId] || [];
  
  messages.forEach(message => {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.type}`;
    
    let messageContent = `<div class="message-bubble">${message.text}</div>`;
    
    // Add file attachment if exists
    if (message.file) {
      const fileIcon = getFileIcon(message.file.type);
      messageContent += `
        <div class="message-file">
          <i class="message-file-icon ${fileIcon}"></i>
          <div class="message-file-info">
            <div class="message-file-name">${message.file.name}</div>
            <div class="message-file-size">${formatFileSize(message.file.size)}</div>
          </div>
          <button class="message-file-download" onclick="downloadFile('${message.file.url}', '${message.file.name}')">
            <i class="fas fa-download"></i>
          </button>
        </div>
      `;
    }
    
    messageDiv.innerHTML = `
      ${messageContent}
      <div class="message-time">${message.timestamp}</div>
    `;
    
    messagesListElement.appendChild(messageDiv);
  });
  
  // Scroll to bottom
  messagesListElement.scrollTop = messagesListElement.scrollHeight;
}

function getFileIcon(fileType) {
  if (fileType.startsWith('image/')) return 'fas fa-image';
  if (fileType.startsWith('video/')) return 'fas fa-video';
  if (fileType.startsWith('audio/')) return 'fas fa-music';
  if (fileType.includes('pdf')) return 'fas fa-file-pdf';
  if (fileType.includes('document') || fileType.includes('word')) return 'fas fa-file-word';
  return 'fas fa-file';
}

function downloadFile(url, filename) {
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// Export functions for backend integration
window.ChatApp = {
  loadContactsFromBackend,
  loadQuickContactsFromBackend,
  addNewContact,
  updateMessageHistory,
  setCurrentChat,
  addNewMessage
};
