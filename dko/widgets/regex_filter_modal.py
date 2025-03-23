from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import (
    Input,
    Label,
)


class RegexFilterModal(ModalScreen[str | None]):
    """A modal dialog for entering a filter pattern."""

    initial_filer: str | None

    def __init__(self, initial_filter: str | None = None):
        super().__init__()
        self.initial_filter = initial_filter

    CSS = """
    #dialog {
        width: 100%;
        height: auto;
        border: thick $background 80%;
        background: $surface;
    }

    #title {
        height: 1;
        width: 100%;
        content-align: center middle;
        background: $accent;
        color: $text;
    }

    #filter-input {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label(
                "Enter filter pattern (regex) or press ESC to clear", id="title"
            )
            yield Input(
                value=self.initial_filter or "",
                placeholder="Enter regex pattern...",
                id="filter-input",
            )

    def on_key(self, event: events.Key):
        if event.name == "escape":
            self.dismiss(None)
        elif event.name == "enter":
            filter_text = self.query_one("#filter-input", Input).value
            self.dismiss(filter_text)
