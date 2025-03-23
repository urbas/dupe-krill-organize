from pathlib import Path

import click
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Footer, Header, LoadingIndicator, Static

from dko.analysis import DirEntry, list_dirs, run_dupe_krill_report


class OrganizeDirs(App):
    """A Textual app to organize and view directories."""

    CSS = """
    DataTable {
        width: 100%;
        height: 100%;
    }

    LoadingIndicator {
        height: auto;
    }

    #directory-container {
        width: 100%;
        height: 100%;
    }

    #loading-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    .loading-text {
        text-align: center;
    }

    .hidden {
        display: none;
    }
    """

    paths: list[Path]
    dupe_krill_report: bytes | None = None
    dir_entries: list[DirEntry] | None = None

    def __init__(self, paths: list[Path]):
        super().__init__()
        self.paths = paths

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="loading-container"):
            yield LoadingIndicator()
            yield Static("Loading dupe-krill report...", classes="loading-text")

        with Container(id="directory-container", classes="hidden"):
            table = DataTable()
            table.add_column("Dupes", key="dupes")
            table.add_column("Related Dirs", key="related_dirs")
            table.add_column("Directory Path", key="dir_path")
            yield table

        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self.process_report_worker(), exclusive=True)

    async def process_report_worker(self) -> None:
        """Process the dupe-krill report in the background."""
        self.dupe_krill_report = await run_dupe_krill_report(self.paths)
        if self.dupe_krill_report is not None:
            self.dir_entries = await list_dirs(self.dupe_krill_report)
        self._update_ui()

    def _update_ui(self) -> None:
        self.query_one("#loading-container").add_class("hidden")
        directory_container = self.query_one("#directory-container")
        directory_container.remove_class("hidden")

        table = self.query_one(DataTable)
        if self.dir_entries:
            for dir_entry in self.dir_entries:
                table.add_row(
                    dir_entry.dupe_count,
                    dir_entry.related_dirs,
                    dir_entry.dir_path,
                )
            table.sort("dupes", "related_dirs", "dir_path", reverse=True)

    def on_key(self, event) -> None:
        pass


@click.command(name="dirs")
@click.argument("paths", type=Path, nargs=-1, required=True)
def cmd(paths: tuple[Path, ...]) -> None:
    app = OrganizeDirs([path for path in paths if path.is_dir()])
    app.run()
