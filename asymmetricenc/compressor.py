from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Button, Digits, Label 
 

class shadowtalk(App):
    def compose(self) -> None:
        with Container(id="shadowalk"):

            yield Button("SEND")
            yield Button("message")
            yield Label("Commands")
            yield LAbel("Chats")
            yield Button("")
            yield Button("➣")






if __name__ == "__main__":
    shadowtalk().run()    