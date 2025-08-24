document.addEventListener("DOMContentLoaded", () => {
            // DOM elements
            const loginForm = document.getElementById("loginForm");
            const registerForm = document.getElementById("registerForm");
            const sendBtn = document.getElementById("sendBtn");
            const messageInput = document.getElementById("messageInput");
            const messagesContainer = document.getElementById("messagesContainer");
            const conversationsList = document.getElementById("conversationsList");
            const fileInput = document.getElementById("fileInput");
            const sendFilesBtn = document.getElementById("sendFiles");
            const attachmentBtn = document.querySelector(".attachment-btn");
            const fileUploadModal = document.getElementById("fileUploadModal");
            const closeFileUpload = document.getElementById("closeFileUpload");

            let currentConversation = "default"; // fallback conversation id

            this.backendConfig = {
                baseUrl: 'http://localhost:5000/chat', // Your Flask server URL
                endpoints: {
                    conversations: '/conversations',
                    messages: '/messages',
                    sendMessage: '/messages/send',
                    uploadFile: '/files/upload',
                    user: '/user',
                    onlineuser: '/onlineusers'
                    
                },
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            this.selectedFiles = [];
            const emojis = {
                smileys: ['😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', '😋', '😎', '😍', '😘', '🥰', '😗', '😙', '😚', '🙂', '🤗', '🤩', '🤔', '🤨', '😐', '😑', '😶', '🙄', '😏', '😣', '😥', '😮', '🤐', '😯', '😪', '😫', '🥱', '😴', '😌', '😛', '😜', '😝'],
                people: ['👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👋', '🤚', '🖐️', '✋', '🖖', '👏', '🙌', '🤲', '🤝', '🙏', '✍️', '💅', '🤳', '💪', '🦾', '🦿', '🦵', '🦶', '👂', '🦻', '👃', '🧠', '🫀', '🫁', '🦷', '🦴', '👀', '👁️', '👅'],
                animals: ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐻‍❄️', '🐨', '🐯', '🦁', '🐮', '🐷', '🐽', '🐸', '🐵', '🙈', '🙉', '🙊', '🐒', '🐔', '🐧', '🐦', '🐤', '🐣', '🐥', '🦆', '🦅', '🦉', '🦇', '🐺', '🐗', '🐴', '🦄', '🐝', '🪱', '🐛', '🦋', '🐌', '🐞'],
                food: ['🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🍆', '🥑', '🥦', '🥬', '🥒', '🌶️', '🫑', '🌽', '🥕', '🫒', '🧄', '🧅', '🥔', '🍠', '🥐', '🥯', '🍞', '🥖', '🥨', '🧀', '🥚', '🍳', '🧈', '🥞'],
                activities: ['⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱', '🪀', '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🪃', '🥅', '⛳', '🪁', '🏹', '🎣', '🤿', '🥊', '🥋', '🎽', '🛹', '🛷', '⛸️', '🥌', '🎿', '⛷️', '🏂', '🪂', '🏋️', '🤸', '🤺', '🤾', '🏌️', '🏇'],
                travel: ['🚗', '🚕', '🚙', '🚌', '🚎', '🏎️', '🚓', '🚑', '🚒', '🚐', '🛻', '🚚', '🚛', '🚜', '🏍️', '🛵', '🚲', '🛴', '🛹', '🛼', '🚁', '🛸', '✈️', '🛩️', '🛫', '🛬', '🪂', '💺', '🚀', '🛰️', '🚢', '⛵', '🚤', '🛥️', '🛳️', '⛴️', '🚂', '🚃', '🚄', '🚅', '🚆'],
                objects: ['💡', '🔦', '🕯️', '🪔', '🧯', '🛢️', '💸', '💵', '💴', '💶', '💷', '🪙', '💰', '💳', '💎', '⚖️', '🪜', '🧰', '🔧', '🔨', '⚒️', '🛠️', '⛏️', '🪚', '🔩', '⚙️', '🪤', '🧱', '⛓️', '🧲', '🔫', '💣', '🧨', '🪓', '🔪', '🗡️', '⚔️', '🛡️', '🚬', '⚰️', '🪦'],
                symbols: ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️', '✝️', '☪️', '🕉️', '☸️', '✡️', '🔯', '🕎', '☯️', '☦️', '🛐', '⛎', '♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑']
            };
            const emojiBtn = document.querySelector(".emoji-btn");
            const emojiModal = document.getElementById("emojiPickerModal");
            const emojiGrid = document.getElementById("emojiGrid");
            const closeEmojiPicker = document.getElementById("closeEmojiPicker");

            if (emojiBtn && emojiModal && emojiGrid) {
            // Show picker
            emojiBtn.addEventListener("click", () => {
                emojiModal.style.display = "block";
                emojiGrid.innerHTML = "";
                Object.values(emojis).forEach(category => {
                category.forEach(symbol => {
                    const span = document.createElement("span");
                    span.textContent = symbol;
                    span.style.cursor = "pointer";
                    span.addEventListener("click", () => {
                    messageInput.value += symbol;
                    emojiModal.style.display = "none";
                    });
                    emojiGrid.appendChild(span);
                });
                });
            });
            // Close picker
            if (closeEmojiPicker) {
                closeEmojiPicker.addEventListener("click", () => {
                emojiModal.style.display = "none";
                });
            }
            }

            const themeToggle = document.querySelector('.theme-toggle');

            themeToggle.addEventListener('click', () => {
                document.body.dataset.theme =
                  document.body.dataset.theme === 'dark' ? 'light' : 'dark';
            });
            

            // ================= AUTH ==================
            async function login(username, password) {
                try {
                    const res = await fetch("/login", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ username1: username, password1: password })
                    });
                    const data = await res.json();
                    if (data.success) {
                        window.location.href = data.redirect;
                    } else {
                        alert(data.error || "Login failed");
                    }
                } catch (err) {
                    console.error("Login error:", err);
                }
            }
        
            async function register(username, email, password) {
                try {
                    const res = await fetch("/register", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ username, email, password })
                    });
                    const data = await res.json();
                    alert(data.message || "Registered");
                } catch (err) {
                    console.error("Register error:", err);
                }
            }
        
            if (loginForm) {
                loginForm.addEventListener("submit", (e) => {
                    e.preventDefault();
                    const username = loginForm.querySelector("#username").value;
                    const password = loginForm.querySelector("#password").value;
                    login(username, password);
                });
            }
        
            if (registerForm) {
                registerForm.addEventListener("submit", (e) => {
                    e.preventDefault();
                    const username = registerForm.querySelector("#username").value;
                    const email = registerForm.querySelector("#email").value;
                    const password = registerForm.querySelector("#password").value;
                    register(username, email, password);
                });
            }
        
            // ================= MESSAGES ==================
            async function loadMessages(conversationId) {
                try {
                    const res = await fetch(`/api/messages?conversation_id=${conversationId}`);
                    const data = await res.json();
                    messagesContainer.innerHTML = "";
                    data.forEach(msg => {
                        const div = document.createElement("div");
                        div.textContent = `${msg.sender || "Unknown"}: ${msg.text || ""}`;
                        messagesContainer.appendChild(div);
                    });
                } catch (err) {
                    console.error("Error loading messages:", err);
                }
            }
        
            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;
        
                try {
                    const res = await fetch("/api/messages/send", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            message,
                            conversation_id: currentConversation
                        })
                    });
                    const data = await res.json();
                    if (data.success) {
                        const msgDiv = document.createElement("div");
                        msgDiv.textContent = `You: ${message}`;
                        messagesContainer.appendChild(msgDiv);
                        messageInput.value = "";
                    } else {
                        alert("Message send failed");
                    }
                } catch (err) {
                    console.error("Error sending message:", err);
                }
            }
        
            if (sendBtn) {
                sendBtn.addEventListener("click", sendMessage);
                messageInput.addEventListener("keypress", (e) => {
                    if (e.key === "Enter") sendMessage();
                });
            }
       
            // ================= CONVERSATIONS ==================
            async function loadConversations() {
                try {
                    const res = await fetch("/api/conversations");
                    const data = await res.json();
                    conversationsList.innerHTML = "";
                    if (data.length === 0) {
                        conversationsList.innerHTML = `<p>No conversations</p>`;
                        return;
                    }
                    data.forEach(conv => {
                        const div = document.createElement("div");
                        div.textContent = conv.title || conv.id;
                        div.addEventListener("click", () => {
                            currentConversation = conv.id;
                            loadMessages(conv.id);
                        });
                        conversationsList.appendChild(div);
                    });
                } catch (err) {
                    console.error("Error loading conversations:", err);
                }
            }
        
            // ================= ONLINE USERS ==================
            async function getOnlineUsers() {
                try {
                    // Construct the full URL using the configured base and endpoint
                    const url = `${this.backendConfig.baseUrl}${this.backendConfig.endpoints.onlineuser}`;
                    const res = await fetch(url);
                    const data = await res.json();
            
                    // Get the sidebar element for online users
                    const sidebar = document.getElementById("online-users");
                    
                    // Clear previous user list to avoid duplication
                    sidebar.innerHTML = "";
            
                    // Check if there are users to display
                    if (data.users && data.users.length > 0) {
                        data.users.forEach(user => {
                            const div = document.createElement("div");
                            div.className = "user-item";
                            div.textContent = user;
                            sidebar.appendChild(div);
                        });
                    } else {
                        // Display a message if no users are online
                        const noUsersDiv = document.createElement("div");
                        noUsersDiv.textContent = "No users online.";
                        noUsersDiv.className = "no-users-message";
                        sidebar.appendChild(noUsersDiv);
                    }
            
                    console.log("Online users:", data.users);
                } catch (err) {
                    console.error("Error getting users:", err);
                }
            }
            }
            
            // ================= FILE UPLOAD ==================
            async function uploadFiles(files) {
                const formData = new FormData();
                for (let f of files) {
                    formData.append("file", f); // <-- key should be 'file', not 'files'
                }
                try {
                    const res = await fetch("/api/files/upload", {
                        method: "POST",
                        body: formData
                    });
                    const data = await res.json();
                    console.log("Files uploaded:", data);
                } catch (err) {
                    console.error("File upload error:", err);
                }
            }
        
            if (fileInput && sendFilesBtn) {
                sendFilesBtn.addEventListener("click", () => {
                    if (fileInput.files.length > 0) {
                        uploadFiles(fileInput.files);
                    }
                });
            }
            if (attachmentBtn && fileUploadModal) {
                attachmentBtn.addEventListener("click", () => {
                  fileUploadModal.style.display = "block";
                });
              }
              
              if (closeFileUpload) {
                closeFileUpload.addEventListener("click", () => {
                  fileUploadModal.style.display = "none";
                });
              }
              
              
            // ================= AUTO REFRESH ==================
            if (messagesContainer && conversationsList) {
                loadConversations();
                getOnlineUsers();
                // Refresh messages every 3s for current conversation
                setInterval(() => {
                    if (currentConversation) loadMessages(currentConversation);
                }, 3000);
            }
        });
        