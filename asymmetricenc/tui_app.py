from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Input, Button
from textual.containers import ScrollableContainer


class ChatApp(App):
    CSS_PATH = "myapp.tcss"
    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        # Header
        yield Container(Static("ShadowTalk", id="title"), id="header")

        # Main split: sidebar + chat
        with Horizontal(id="main"):
            with Container(id="sidebar"):
                yield Static("[b]Commands[/b]", id="sidebar-title")
                yield Static(
                    "Type /friends to see list\nType /connect <name> to connect",
                    id="sidebar-help",
                )
            with Container(id="chat"):
                yield Static("[b]Chat[/b]", id="chat-title")
                yield ScrollableContainer(id="messages")

        # Bottom input bar
        with Horizontal(id="input-bar"):
            yield Input(placeholder="Type your message…", id="chat-input")
            yield Button("🙂", id="emoji-btn", classes="chat-btn")
            yield Button("⌂", id="upload-btn", classes="chat-btn")
            yield Button("Send", id="send-btn", classes="chat-btn")

    def on_mount(self) -> None:
        """Focus the input when the app starts."""
        self.query_one("#chat-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle send button press."""
        if event.button.id == "send-btn":
            self.process_message()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key press in input."""
        self.process_message()

    def process_message(self) -> None:
        """Get text from input, post it to the log, and clear the input."""
        input_box = self.query_one("#chat-input", Input)
        text = input_box.value.strip()
        if text:
            log = self.query_one("#messages", ScrollableContainer)
            log.mount(Static(f"[b]You:[/b] {text}", classes="msg self"))
            input_box.value = ""
            log.scroll_end(animate=False)
        input_box.focus()


if __name__ == "__main__":
    ChatApp().run()
