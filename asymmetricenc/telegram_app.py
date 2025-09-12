from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Button, TextArea, Input
from textual.message import Message
from textual.events import Key
from textual.reactive import reactive

EMOJIS = [
    "😀\uFE0F", "😃\uFE0F", "😄\uFE0F", "😁\uFE0F", "😆\uFE0F", "😅\uFE0F", "😂\uFE0F", "🤣\uFE0F", "😊\uFE0F", "😇\uFE0F",
    "🙂\uFE0F", "🙃\uFE0F", "😉\uFE0F", "😌\uFE0F", "😍\uFE0F", "🥰\uFE0F", "😘\uFE0F", "😗\uFE0F", "😙\uFE0F", "😚\uFE0F",
    "😋\uFE0F", "😛\uFE0F", "😝\uFE0F", "😜\uFE0F", "🤪\uFE0F", "🤨\uFE0F", "🧐\uFE0F", "🤓\uFE0F", "😎\uFE0F", "🤩\uFE0F",
    "🥳\uFE0F", "😏\uFE0F", "😒\uFE0F", "😞\uFE0F", "😔\uFE0F", "😟\uFE0F", "😕\uFE0F", "🙁\uFE0F", "☹️\uFE0F", "😣\uFE0F",
    "😖\uFE0F", "😫\uFE0F", "😩\uFE0F", "🥺\uFE0F", "😢\uFE0F", "😭\uFE0F", "😤\uFE0F", "😠\uFE0F", "😡\uFE0F", "🤬\uFE0F",
]

class MessageSent(Message):
    """Custom message to indicate that a message should be sent."""
    pass

class CustomTextArea(TextArea):
    """A custom TextArea that sends a message on Enter."""
    def on_key(self, event: Key) -> None:
        if event.key == "enter":
            event.prevent_default()
            self.post_message(MessageSent())

class TelegramApp(App):
    """A Textual chat app inspired by Telegram."""

    CSS_PATH = "telegram_style.tcss"
    BINDINGS = [("ctrl+c", "quit", "Quit")]

    contacts = reactive(["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi"])
    selected_contact = reactive("Bob")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Horizontal(id="main-container"):
            with Vertical(id="sidebar"):
                yield Input(placeholder="Search contacts", id="search-contacts")
                with VerticalScroll(id="contact-list"):
                    pass  # Populated in on_mount

            with Container(id="chat-container"):
                yield Static(f"[b]{self.selected_contact}[/b]", id="chat-header")
                with VerticalScroll(id="chat-log"):
                    yield Static("[#888]Yesterday[/]")
                    yield Static("Hey! Are you there?", classes="message received")
                    yield Static("Yeah, what's up?", classes="message sent")
                    yield Static("I was wondering if you had time for a call tomorrow.", classes="message received")
                    yield Static("Sure, what time works for you?", classes="message sent")

                with Vertical(id="emoji-picker"):
                    for emoji in EMOJIS:
                        yield Button(emoji, classes="emoji-btn")

                with Horizontal(id="input-bar"):
                    yield CustomTextArea(placeholder="Message", id="message-input")
                    yield Button("😀", id="toggle-emoji-btn")
                    yield Button("📎", id="file-btn")
                    yield Button("Send", variant="primary", id="send-btn")
        yield Footer()

    def on_mount(self) -> None:
        """Focus the input on startup and setup contacts."""
        self.update_contact_list()
        self.query_one("#message-input", CustomTextArea).focus()

    def update_contact_list(self, search_term: str = "") -> None:
        """Update the contact list based on the search term."""
        contact_list = self.query_one("#contact-list")
        contact_list.remove_children()
        
        filtered_contacts = [c for c in self.contacts if search_term.lower() in c.lower()]
        
        for contact_name in filtered_contacts:
            contact_widget = Button(contact_name, classes="contact")
            if contact_name == self.selected_contact:
                contact_widget.add_class("active")
            contact_list.mount(contact_widget)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-contacts":
            self.update_contact_list(event.value)

    def action_send_message(self) -> None:
        """Send a message and clear the input."""
        textarea = self.query_one("#message-input", CustomTextArea)
        chat_log = self.query_one("#chat-log")
        text = textarea.text.strip()
        if text:
            chat_log.mount(Static(text, classes="message sent"))
            chat_log.scroll_end(animate=True)
            textarea.text = ""
        textarea.focus()

    def on_message_sent(self, event: MessageSent) -> None:
        """Handle the custom message to send content."""
        self.action_send_message()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.has_class("contact"):
            try:
                self.query_one(".contact.active").remove_class("active")
            except:
                pass
            event.button.add_class("active")
            self.selected_contact = str(event.button.label)
            self.query_one("#chat-header").update(f"[b]{self.selected_contact}[/b]")
            chat_log = self.query_one("#chat-log")
            chat_log.remove_children()
            chat_log.mount(Static(f"Chat history with {self.selected_contact} would be loaded here."))
            self.query_one("#message-input").focus()

        elif event.button.id == "send-btn":
            self.action_send_message()
        elif event.button.id == "toggle-emoji-btn":
            picker = self.query_one("#emoji-picker")
            if picker.styles.display == "none":
                picker.styles.display = "block"
            else:
                picker.styles.display = "none"
        elif event.button.id == "file-btn":
            pass
        elif event.button.has_class("emoji-btn"):
            textarea = self.query_one("#message-input", CustomTextArea)
            textarea.insert(str(event.button.label))
            textarea.focus()

if __name__ == "__main__":
    app = TelegramApp()
    app.run()