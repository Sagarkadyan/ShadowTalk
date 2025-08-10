document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.querySelector(".sidebar");
    const toggleSidebar = document.getElementById("toggleSidebar");
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const attachBtn = document.getElementById("attachBtn");
    const sendBtn = document.getElementById("sendBtn");
    const messageInput = document.getElementById("messageInput");
    const messages = document.getElementById("messages");
    const emojiPicker = document.getElementById("emojiPicker");

    // Sidebar toggle
    toggleSidebar.addEventListener("click", () => {
        sidebar.style.width = sidebar.style.width === "0px" ? "280px" : "0px";
    });

    // Emoji picker setup
    const emojis = ["😀","😂","😍","👍","🎉","🔥","❤️","😎","🤔","😢"];
    emojis.forEach(e => {
        const span = document.createElement("span");
        span.textContent = e;
        span.addEventListener("click", () => {
            messageInput.value += e;
        });
        emojiPicker.appendChild(span);
    });

    // File attach button
    attachBtn.addEventListener("click", () => fileInput.click());

    // Send message
    sendBtn.addEventListener("click", () => {
        if (messageInput.value.trim() !== "") {
            appendMessage(messageInput.value, "sent");
            messageInput.value = "";
        }
    });

    function appendMessage(text, type) {
        const div = document.createElement("div");
        div.classList.add("message", type);
        div.textContent = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    // Drag and drop handling
    let dragCounter = 0;
    document.addEventListener("dragenter", (e) => {
        e.preventDefault();
        dragCounter++;
        dropZone.style.display = "flex";
    });

    document.addEventListener("dragleave", (e) => {
        e.preventDefault();
        dragCounter--;
        if (dragCounter === 0) dropZone.style.display = "none";
    });

    document.addEventListener("dragover", (e) => e.preventDefault());

    document.addEventListener("drop", (e) => {
        e.preventDefault();
        dragCounter = 0;
        dropZone.style.display = "none";
        console.log("Files dropped:", e.dataTransfer.files);
    });
});
