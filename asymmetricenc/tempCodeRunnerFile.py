from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container
from textual.widgets import Static, Input, Button
from textual.containers import ScrollableContainer

class ChatApp(App):
    CSS_Path =  "myapp.tcss"   

    def compose(self) -> ComposeResult:
        with Horizontal(id="main"):
            with Container(id="sidebar"):
                yield Static("[b]Commands[/b]", id="sidebar-title")
                yield Static("Type /friends to see list\nType /connect <name> to connect")

            with Container(id="chat"):
                yield Static("[b]Chat[/b]", id="chat-title")
                yield ScrollableContainer(id="chat-messages")

        with Horizontal(id="bottom-bar"):
            yield Input(placeholder="Type your message...", id="chat-input")
            yield Button("😀", id="emoji-btn", classes="chat-btn")
            yield Button("📎", id="upload-btn", classes="chat-btn")
            yield Button("➤", id="send-btn")
            

if __name__ == "__main__":
    ChatApp().run()
