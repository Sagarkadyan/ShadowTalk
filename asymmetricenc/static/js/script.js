// Chat Application JavaScript
class ChatApp {
    constructor() {
        this.currentTheme = localStorage.getItem('chat-theme') || 'light';

        this.currentConversation = null;
        this.messages = {};
        this.conversationData = {};
        
        // Backend configuration - Set your backend URL and endpoints here
        this.backendConfig = {
            baseUrl: '', // Set your backend URL here (e.g., 'https://api.yourapp.com')
            endpoints: {
                conversations: '/api/conversations',
                messages: '/api/messages',
                sendMessage: '/api/messages/send',
                uploadFile: '/api/files/upload',
                user: '/api/user'
            },
            headers: {
                'Content-Type': 'application/json'
                // Add authentication headers here (e.g., 'Authorization': 'Bearer ' + token)
            }
        };

        this.selectedFiles = [];
        this.emojis = {
            smileys: ['😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', '😋', '😎', '😍', '😘', '🥰', '😗', '😙', '😚', '🙂', '🤗', '🤩', '🤔', '🤨', '😐', '😑', '😶', '🙄', '😏', '😣', '😥', '😮', '🤐', '😯', '😪', '😫', '🥱', '😴', '😌', '😛', '😜', '😝'],
            people: ['👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👋', '🤚', '🖐️', '✋', '🖖', '👏', '🙌', '🤲', '🤝', '🙏', '✍️', '💅', '🤳', '💪', '🦾', '🦿', '🦵', '🦶', '👂', '🦻', '👃', '🧠', '🫀', '🫁', '🦷', '🦴', '👀', '👁️', '👅'],
            animals: ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐻‍❄️', '🐨', '🐯', '🦁', '🐮', '🐷', '🐽', '🐸', '🐵', '🙈', '🙉', '🙊', '🐒', '🐔', '🐧', '🐦', '🐤', '🐣', '🐥', '🦆', '🦅', '🦉', '🦇', '🐺', '🐗', '🐴', '🦄', '🐝', '🪱', '🐛', '🦋', '🐌', '🐞'],
            food: ['🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🍆', '🥑', '🥦', '🥬', '🥒', '🌶️', '🫑', '🌽', '🥕', '🫒', '🧄', '🧅', '🥔', '🍠', '🥐', '🥯', '🍞', '🥖', '🥨', '🧀', '🥚', '🍳', '🧈', '🥞'],
            activities: ['⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱', '🪀', '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🪃', '🥅', '⛳', '🪁', '🏹', '🎣', '🤿', '🥊', '🥋', '🎽', '🛹', '🛷', '⛸️', '🥌', '🎿', '⛷️', '🏂', '🪂', '🏋️', '🤸', '🤺', '🤾', '🏌️', '🏇'],
            travel: ['🚗', '🚕', '🚙', '🚌', '🚎', '🏎️', '🚓', '🚑', '🚒', '🚐', '🛻', '🚚', '🚛', '🚜', '🏍️', '🛵', '🚲', '🛴', '🛹', '🛼', '🚁', '🛸', '✈️', '🛩️', '🛫', '🛬', '🪂', '💺', '🚀', '🛰️', '🚢', '⛵', '🚤', '🛥️', '🛳️', '⛴️', '🚂', '🚃', '🚄', '🚅', '🚆'],
            objects: ['💡', '🔦', '🕯️', '🪔', '🧯', '🛢️', '💸', '💵', '💴', '💶', '💷', '🪙', '💰', '💳', '💎', '⚖️', '🪜', '🧰', '🔧', '🔨', '⚒️', '🛠️', '⛏️', '🪚', '🔩', '⚙️', '🪤', '🧱', '⛓️', '🧲', '🔫', '💣', '🧨', '🪓', '🔪', '🗡️', '⚔️', '🛡️', '🚬', '⚰️', '🪦'],
            symbols: ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️', '✝️', '☪️', '🕉️', '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑']
        };
        
        this.init();
    }

    async init() {
        this.setTheme(this.currentTheme);
        this.bindEvents();
        
        // Load data from backend if configured
        if (this.backendConfig.baseUrl) {
            await this.loadConversations();
            if (this.currentConversation) {
                this.updateChatHeader();
                await this.loadMessages(this.currentConversation);
            }
        } else {
            // Show empty state when no backend is configured
            this.updateConversationsList([]);
        }
    }

    bindEvents() {
        // Theme toggle
        const themeToggle = document.querySelector('.theme-toggle');
        themeToggle.addEventListener('click', () => this.toggleTheme());



        // Conversation switching
        const conversations = document.querySelectorAll('.conversation');
        conversations.forEach(conv => {
            conv.addEventListener('click', (e) => {
                const conversationId = parseInt(e.currentTarget.dataset.conversation);
                this.switchConversation(conversationId);
            });
        });

        // Message input
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', () => this.sendMessage());

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => this.searchConversations(e.target.value));

        // Mobile sidebar toggle (for future mobile menu implementation)
        this.setupMobileHandlers();

        // Emoji and attachment buttons
        const emojiBtn = document.querySelector('.emoji-btn');
        const attachmentBtn = document.querySelector('.attachment-btn');
        
        emojiBtn.addEventListener('click', () => this.showEmojiPicker());
        attachmentBtn.addEventListener('click', () => this.showFileUpload());

        // Emoji picker event listeners
        this.initializeEmojiPicker();
        this.initializeFileUpload();

        // Chat action buttons
        const actionBtns = document.querySelectorAll('.action-btn');
        actionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const icon = e.currentTarget.querySelector('i');
                if (icon.classList.contains('fa-ellipsis-v')) {
                    this.showMoreOptions();
                }
            });
        });
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const themeIcon = document.querySelector('.theme-toggle i');
        
        if (theme === 'dark') {
            themeIcon.className = 'fas fa-sun';
        } else {
            themeIcon.className = 'fas fa-moon';
        }
        
        localStorage.setItem('chat-theme', theme);
        this.currentTheme = theme;
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }



    async switchConversation(conversationId) {
        // Update active conversation
        document.querySelectorAll('.conversation').forEach(conv => {
            conv.classList.remove('active');
        });
        
        const selectedConv = document.querySelector(`[data-conversation="${conversationId}"]`);
        if (selectedConv) {
            selectedConv.classList.add('active');
        }
        
        // Remove unread count
        const unreadCount = selectedConv?.querySelector('.unread-count');
        if (unreadCount) {
            unreadCount.remove();
        }
        
        this.currentConversation = conversationId;
        this.updateChatHeader();
        
        // Load messages from backend or display cached messages
        if (this.backendConfig.baseUrl && !this.messages[conversationId]) {
            await this.loadMessages(conversationId);
        } else {
            this.displayMessages();
        }
        
        // Close mobile sidebar if open
        this.closeMobileSidebar();
    }

    updateChatHeader() {
        const chatHeader = document.querySelector('.current-user');
        if (!chatHeader || !this.currentConversation) return;
        
        const data = this.conversationData[this.currentConversation];
        if (!data) return;
        
        chatHeader.innerHTML = `
            <div class="avatar">
                <img src="https://ui-avatars.com/api/?name=${data.avatar}&background=${data.color}&color=fff&size=50" alt="${data.name}">
                <div class="status-indicator ${this.getStatusClass(data.status)}"></div>
            </div>
            <div class="user-details">
                <h3>${data.name}</h3>
                <span class="status">${data.status}</span>
            </div>
        `;
    }

    getStatusClass(status) {
        if (status.includes('Online')) return 'online';
        if (status.includes('Away')) return 'away';
        if (status.includes('Offline')) return 'offline';
        return '';
    }

    displayMessages() {
        const messagesContainer = document.getElementById('messagesContainer');
        const placeholder = document.getElementById('emptyChatPlaceholder');
        const messages = this.messages[this.currentConversation] || [];
        
        // Clear only messages, keep placeholder
        const messageElements = messagesContainer.querySelectorAll('.message, .loading');
        messageElements.forEach(el => el.remove());
        
        if (messages.length > 0) {
            // Hide placeholder when messages exist
            if (placeholder) placeholder.style.display = 'none';
            
            messages.forEach(message => {
                this.addMessageToDOM(message, false);
            });
        } else {
            // Show placeholder when no messages
            if (placeholder) placeholder.style.display = 'flex';
        }
        
        this.scrollToBottom();
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const content = messageInput.value.trim();
        
        if (!content || !this.currentConversation) return;
        
        // Show loading state
        this.showSendingAnimation();
        
        const now = new Date();
        const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        // Create and show loading message
        const loadingMessageId = this.addLoadingMessage();
        
        // Clear input immediately for better UX
        messageInput.value = '';
        
        try {
            if (this.backendConfig.baseUrl) {
                // Send to backend
                const response = await this.sendMessageToBackend(content);
                
                // Remove loading message
                this.removeLoadingMessage(loadingMessageId);
                
                if (response && response.success) {
                    // Add the sent message if backend confirms success
                    const message = response.message || {
                        type: 'sent',
                        content: content,
                        timestamp: timestamp
                    };
                    
                    if (!this.messages[this.currentConversation]) {
                        this.messages[this.currentConversation] = [];
                    }
                    this.messages[this.currentConversation].push(message);
                    this.addMessageToDOM(message, true);
                    this.updateConversationPreview(content, timestamp);
                } else {
                    // Handle backend error
                    console.error('Failed to send message:', response);
                    // Re-add content to input
                    messageInput.value = content;
                }
            } else {
                // No backend configured - work offline
                setTimeout(() => {
                    this.removeLoadingMessage(loadingMessageId);
                    
                    const message = {
                        type: 'sent',
                        content: content,
                        timestamp: timestamp
                    };
                    
                    if (!this.messages[this.currentConversation]) {
                        this.messages[this.currentConversation] = [];
                    }
                    this.messages[this.currentConversation].push(message);
                    this.addMessageToDOM(message, true);
                    this.updateConversationPreview(content, timestamp);
                    this.scrollToBottom();
                }, 500);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeLoadingMessage(loadingMessageId);
            messageInput.value = content; // Restore content on error
        } finally {
            this.hideSendingAnimation();
            this.scrollToBottom();
        }
    }

    addMessageToDOM(message, animate = false) {
        const messagesContainer = document.getElementById('messagesContainer');
        const placeholder = document.getElementById('emptyChatPlaceholder');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.type}`;
        
        // Hide placeholder when first message is added
        if (placeholder) {
            placeholder.style.display = 'none';
        }
        
        if (animate) {
            messageElement.style.opacity = '0';
            messageElement.style.transform = 'translateY(20px)';
        }
        
        let messageContent;
        if (message.file) {
            // File message
            messageContent = `
                <div class="message-content">
                    <div class="message-file">
                        <div class="message-file-icon">
                            <i class="${message.file.icon}"></i>
                        </div>
                        <div class="message-file-info">
                            <div class="message-file-name">${this.escapeHtml(message.file.name)}</div>
                            <div class="message-file-size">${message.file.size}</div>
                        </div>
                        <button class="message-file-download" title="Download file">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                    <span class="timestamp">${message.timestamp}</span>
                </div>
            `;
        } else {
            // Regular text message
            messageContent = `
                <div class="message-content">
                    <p>${this.escapeHtml(message.content)}</p>
                    <span class="timestamp">${message.timestamp}</span>
                </div>
            `;
        }
        
        messageElement.innerHTML = messageContent;
        messagesContainer.appendChild(messageElement);
        
        if (animate) {
            requestAnimationFrame(() => {
                messageElement.style.transition = 'all 0.3s ease-out';
                messageElement.style.opacity = '1';
                messageElement.style.transform = 'translateY(0)';
            });
        }
    }

    simulateResponse() {
        const responses = [
            "That sounds great!",
            "Thanks for letting me know.",
            "I'll get back to you on that.",
            "Perfect timing!",
            "Absolutely!",
            "Let me check and get back to you.",
            "Sounds good to me.",
            "I appreciate the update."
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        const now = new Date();
        const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        const message = {
            type: 'received',
            content: randomResponse,
            timestamp: timestamp
        };
        
        this.messages[this.currentConversation].push(message);
        this.addMessageToDOM(message, true);
        this.updateConversationPreview(randomResponse, timestamp);
        this.scrollToBottom();
    }

    updateConversationPreview(content, timestamp) {
        const conversation = document.querySelector(`[data-conversation="${this.currentConversation}"]`);
        const lastMessageElement = conversation.querySelector('.last-message');
        const timeElement = conversation.querySelector('.time');
        
        lastMessageElement.textContent = content;
        timeElement.textContent = timestamp;
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showSendingAnimation() {
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.classList.add('loading');
        sendBtn.disabled = true;
    }

    hideSendingAnimation() {
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.classList.remove('loading');
        sendBtn.disabled = false;
    }

    addLoadingMessage() {
        const messagesContainer = document.getElementById('messagesContainer');
        const loadingMessageId = 'loading-' + Date.now();
        const messageElement = document.createElement('div');
        messageElement.className = 'message sent loading';
        messageElement.id = loadingMessageId;
        
        messageElement.innerHTML = `
            <div class="message-content">
                <div class="loading-dots">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
        
        return loadingMessageId;
    }

    removeLoadingMessage(loadingMessageId) {
        const loadingMessage = document.getElementById(loadingMessageId);
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }

    searchConversations(query) {
        const conversations = document.querySelectorAll('.conversation');
        
        conversations.forEach(conv => {
            const name = conv.querySelector('h4').textContent.toLowerCase();
            const lastMessage = conv.querySelector('.last-message').textContent.toLowerCase();
            
            if (name.includes(query.toLowerCase()) || lastMessage.includes(query.toLowerCase())) {
                conv.style.display = 'flex';
            } else {
                conv.style.display = query ? 'none' : 'flex';
            }
        });
    }

    setupMobileHandlers() {
        // Add mobile menu toggle functionality
        const chatHeader = document.querySelector('.chat-header');
        
        // Add mobile menu button if screen is mobile
        if (window.innerWidth <= 768) {
            this.addMobileMenuButton();
        }
        
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768) {
                this.addMobileMenuButton();
            } else {
                this.removeMobileMenuButton();
                this.closeMobileSidebar();
            }
        });
    }

    addMobileMenuButton() {
        const chatHeader = document.querySelector('.chat-header');
        let mobileMenuBtn = chatHeader.querySelector('.mobile-menu-btn');
        
        if (!mobileMenuBtn) {
            mobileMenuBtn = document.createElement('button');
            mobileMenuBtn.className = 'mobile-menu-btn action-btn';
            mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
            mobileMenuBtn.setAttribute('aria-label', 'Open menu');
            
            mobileMenuBtn.addEventListener('click', () => this.toggleMobileSidebar());
            
            chatHeader.insertBefore(mobileMenuBtn, chatHeader.firstChild);
        }
    }

    removeMobileMenuButton() {
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        if (mobileMenuBtn) {
            mobileMenuBtn.remove();
        }
    }

    toggleMobileSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        sidebar.classList.toggle('mobile-open');
        overlay.classList.toggle('active');
        
        if (overlay.classList.contains('active')) {
            overlay.addEventListener('click', () => this.closeMobileSidebar());
        }
    }

    closeMobileSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        sidebar.classList.remove('mobile-open');
        overlay.classList.remove('active');
    }

    initializeEmojiPicker() {
        const emojiPickerModal = document.getElementById('emojiPickerModal');
        const closeEmojiPicker = document.getElementById('closeEmojiPicker');
        const emojiCategories = document.querySelectorAll('.emoji-category');
        const emojiGrid = document.getElementById('emojiGrid');

        // Close emoji picker
        closeEmojiPicker.addEventListener('click', () => this.hideEmojiPicker());
        
        // Close on overlay click
        emojiPickerModal.addEventListener('click', (e) => {
            if (e.target === emojiPickerModal) {
                this.hideEmojiPicker();
            }
        });

        // Category switching
        emojiCategories.forEach(category => {
            category.addEventListener('click', () => {
                emojiCategories.forEach(c => c.classList.remove('active'));
                category.classList.add('active');
                this.showEmojiCategory(category.dataset.category);
            });
        });

        // Initialize with smileys
        this.showEmojiCategory('smileys');
    }

    initializeFileUpload() {
        const fileUploadModal = document.getElementById('fileUploadModal');
        const closeFileUpload = document.getElementById('closeFileUpload');
        const fileUploadArea = document.getElementById('fileUploadArea');
        const fileInput = document.getElementById('fileInput');
        const browseButton = document.getElementById('browseButton');
        const cancelUpload = document.getElementById('cancelUpload');
        const sendFiles = document.getElementById('sendFiles');

        // Close file upload
        closeFileUpload.addEventListener('click', () => this.hideFileUpload());
        cancelUpload.addEventListener('click', () => this.hideFileUpload());
        
        // Close on overlay click
        fileUploadModal.addEventListener('click', (e) => {
            if (e.target === fileUploadModal) {
                this.hideFileUpload();
            }
        });

        // Browse button
        browseButton.addEventListener('click', () => fileInput.click());
        fileUploadArea.addEventListener('click', () => fileInput.click());

        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelection(Array.from(e.target.files));
        });

        // Drag and drop
        fileUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUploadArea.classList.add('drag-over');
        });

        fileUploadArea.addEventListener('dragleave', () => {
            fileUploadArea.classList.remove('drag-over');
        });

        fileUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUploadArea.classList.remove('drag-over');
            this.handleFileSelection(Array.from(e.dataTransfer.files));
        });

        // Send files
        sendFiles.addEventListener('click', () => this.sendSelectedFiles());
    }

    showEmojiPicker() {
        const emojiPickerModal = document.getElementById('emojiPickerModal');
        emojiPickerModal.classList.add('active');
    }

    hideEmojiPicker() {
        const emojiPickerModal = document.getElementById('emojiPickerModal');
        emojiPickerModal.classList.remove('active');
    }

    showEmojiCategory(category) {
        const emojiGrid = document.getElementById('emojiGrid');
        const emojis = this.emojis[category] || [];
        
        emojiGrid.innerHTML = '';
        emojis.forEach(emoji => {
            const emojiButton = document.createElement('button');
            emojiButton.className = 'emoji-item';
            emojiButton.textContent = emoji;
            emojiButton.addEventListener('click', () => this.insertEmoji(emoji));
            emojiGrid.appendChild(emojiButton);
        });
    }

    insertEmoji(emoji) {
        const messageInput = document.getElementById('messageInput');
        const currentValue = messageInput.value;
        const cursorPosition = messageInput.selectionStart;
        
        const newValue = currentValue.slice(0, cursorPosition) + emoji + currentValue.slice(cursorPosition);
        messageInput.value = newValue;
        messageInput.focus();
        messageInput.setSelectionRange(cursorPosition + emoji.length, cursorPosition + emoji.length);
        
        this.hideEmojiPicker();
    }

    showFileUpload() {
        const fileUploadModal = document.getElementById('fileUploadModal');
        this.selectedFiles = [];
        this.updateFilePreview();
        fileUploadModal.classList.add('active');
    }

    hideFileUpload() {
        const fileUploadModal = document.getElementById('fileUploadModal');
        fileUploadModal.classList.remove('active');
        this.selectedFiles = [];
        this.updateFilePreview();
        document.getElementById('fileInput').value = '';
    }

    handleFileSelection(files) {
        files.forEach(file => {
            if (!this.selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
                this.selectedFiles.push(file);
            }
        });
        this.updateFilePreview();
    }

    updateFilePreview() {
        const filePreview = document.getElementById('filePreview');
        const sendFiles = document.getElementById('sendFiles');
        
        filePreview.innerHTML = '';
        
        if (this.selectedFiles.length === 0) {
            sendFiles.disabled = true;
            return;
        }
        
        sendFiles.disabled = false;
        
        this.selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-preview-item';
            
            const icon = this.getFileIcon(file.type);
            const size = this.formatFileSize(file.size);
            
            fileItem.innerHTML = `
                <div class="file-preview-icon">
                    <i class="${icon}"></i>
                </div>
                <div class="file-preview-info">
                    <div class="file-preview-name">${file.name}</div>
                    <div class="file-preview-size">${size}</div>
                </div>
                <button class="remove-file" data-index="${index}">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            fileItem.querySelector('.remove-file').addEventListener('click', () => {
                this.selectedFiles.splice(index, 1);
                this.updateFilePreview();
            });
            
            filePreview.appendChild(fileItem);
        });
    }

    getFileIcon(fileType) {
        if (fileType.startsWith('image/')) return 'fas fa-image';
        if (fileType.startsWith('video/')) return 'fas fa-video';
        if (fileType.startsWith('audio/')) return 'fas fa-music';
        if (fileType.includes('pdf')) return 'fas fa-file-pdf';
        if (fileType.includes('word') || fileType.includes('document')) return 'fas fa-file-word';
        if (fileType.includes('text')) return 'fas fa-file-alt';
        return 'fas fa-file';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async sendSelectedFiles() {
        if (this.selectedFiles.length === 0) return;
        
        const now = new Date();
        const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        try {
            if (this.backendConfig.baseUrl) {
                // Send files to backend
                const response = await this.sendMessageToBackend('', { files: this.selectedFiles });
                
                if (response && response.success) {
                    // Files sent successfully - they should appear via real-time updates
                    console.log('Files sent successfully');
                } else {
                    console.error('Failed to send files:', response);
                }
            } else {
                // No backend - display locally
                this.selectedFiles.forEach(file => {
                    const message = {
                        type: 'sent',
                        content: '',
                        timestamp: timestamp,
                        file: {
                            name: file.name,
                            size: this.formatFileSize(file.size),
                            type: file.type,
                            icon: this.getFileIcon(file.type)
                        }
                    };
                    
                    if (!this.messages[this.currentConversation]) {
                        this.messages[this.currentConversation] = [];
                    }
                    this.messages[this.currentConversation].push(message);
                    this.addMessageToDOM(message, true);
                });
                
                this.updateConversationPreview(`${this.selectedFiles.length} file(s) shared`, timestamp);
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Error sending files:', error);
        } finally {
            this.hideFileUpload();
        }
    }

    // Backend Integration Methods
    async makeRequest(endpoint, method = 'GET', data = null) {
        if (!this.backendConfig.baseUrl) {
            console.warn('Backend URL not configured. Please set backendConfig.baseUrl');
            return null;
        }

        const url = this.backendConfig.baseUrl + endpoint;
        const options = {
            method,
            headers: { ...this.backendConfig.headers }
        };

        if (data && method !== 'GET') {
            if (data instanceof FormData) {
                // Remove Content-Type header for FormData
                delete options.headers['Content-Type'];
                options.body = data;
            } else {
                options.body = JSON.stringify(data);
            }
        }

        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Backend request failed:', error);
            return null;
        }
    }

    async loadConversations() {
        const conversations = await this.makeRequest(this.backendConfig.endpoints.conversations);
        
        if (conversations && conversations.length > 0) {
            // Update conversation data
            conversations.forEach(conv => {
                this.conversationData[conv.id] = {
                    name: conv.name,
                    status: conv.status,
                    avatar: conv.avatar,
                    color: conv.color || 'f093fb'
                };
            });
            
            // Set first conversation as current
            this.currentConversation = conversations[0].id;
            
            // Update sidebar with real conversations
            this.updateConversationsList(conversations);
        }
    }

    async loadMessages(conversationId) {
        const messages = await this.makeRequest(
            `${this.backendConfig.endpoints.messages}?conversation_id=${conversationId}`
        );
        
        if (messages) {
            this.messages[conversationId] = messages;
            this.displayMessages();
        }
    }

    async sendMessageToBackend(content, fileData = null) {
        const messageData = {
            conversation_id: this.currentConversation,
            content: content,
            type: 'sent'
        };

        if (fileData) {
            const formData = new FormData();
            formData.append('conversation_id', this.currentConversation);
            formData.append('content', content);
            formData.append('type', 'sent');
            
            if (fileData.files) {
                fileData.files.forEach(file => {
                    formData.append('files', file);
                });
            }
            
            return await this.makeRequest(this.backendConfig.endpoints.sendMessage, 'POST', formData);
        } else {
            return await this.makeRequest(this.backendConfig.endpoints.sendMessage, 'POST', messageData);
        }
    }

    updateConversationsList(conversations) {
        const conversationsList = document.getElementById('conversationsList');
        const emptyState = document.getElementById('emptyConversations');
        
        if (!conversationsList) return;

        // Clear existing conversations (except empty state)
        const existingConvs = conversationsList.querySelectorAll('.conversation');
        existingConvs.forEach(conv => conv.remove());
        
        if (conversations && conversations.length > 0) {
            // Hide empty state
            if (emptyState) emptyState.style.display = 'none';
            
            conversations.forEach(conv => {
                const conversationElement = document.createElement('div');
                conversationElement.className = 'conversation';
                conversationElement.dataset.conversation = conv.id;
                
                conversationElement.innerHTML = `
                    <div class="avatar">
                        <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(conv.name)}&background=${conv.color || 'f093fb'}&color=fff&size=50" alt="${conv.name}">
                        <div class="status-indicator ${conv.online ? 'online' : 'offline'}"></div>
                    </div>
                    <div class="conversation-info">
                        <div class="conversation-header">
                            <h4>${conv.name}</h4>
                            <span class="time">${conv.lastMessageTime || ''}</span>
                        </div>
                        <p class="last-message">${conv.lastMessage || 'No messages yet'}</p>
                        ${conv.unreadCount ? `<div class="unread-count">${conv.unreadCount}</div>` : ''}
                    </div>
                `;
                
                conversationElement.addEventListener('click', () => {
                    this.switchConversation(conv.id);
                });
                
                conversationsList.appendChild(conversationElement);
            });
        } else {
            // Show empty state
            if (emptyState) emptyState.style.display = 'flex';
        }
    }

    showMoreOptions() {
        console.log('More options menu would open here');
        // Future: Implement context menu with more options
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the chat application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

// Add smooth scrolling behavior for better UX
document.addEventListener('scroll', function(e) {
    if (e.target.classList.contains('messages-container')) {
        e.target.style.scrollBehavior = 'smooth';
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    console.log('Connection restored');
    // Future: Update UI to show connection status
});

window.addEventListener('offline', () => {
    console.log('Connection lost');
    // Future: Update UI to show offline status
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }
    
    // Escape to close mobile sidebar
    if (e.key === 'Escape') {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar.classList.contains('mobile-open')) {
            sidebar.classList.remove('mobile-open');
            document.getElementById('sidebarOverlay').classList.remove('active');
        }
    }
});
