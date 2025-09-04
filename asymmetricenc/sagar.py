
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Input


class ChatApp(App):
    CSS = """
    Horizontal {
        height: 100%;
    }

    #commands {
        width: 30%;
        border: round;
        padding: 1;
    }

    #chat {
        width: 70%;
        border: round;
        padding: 1;
    }

    #input {
        dock: bottom;
        border: round;
    }
    """

    def compose(self) -> ComposeResult:
        # Left panel (commands/friends), right panel (chat), bottom input
        with Horizontal():
            self.commands = Static("Commands/Users:\n/friends\n/connect <name>\n/quit", id="commands")
            self.chat = Static("Chat:\n", id="chat")
            yield self.commands
            yield self.chat
        yield Input(placeholder="Type message or /command", id="input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return

        if text.lower() in ("/quit", "q"):
            self.exit()  # quit cleanly
        elif text.startswith("/"):
            self.commands.update(self.commands.renderable + f"\nCMD: {text}")
        else:
            self.chat.update(self.chat.renderable + f"\nYOU: {text}")

        event.input.value = ""  # clear input


if __name__ == "__main__":
    ChatApp().run()
