import asyncio
import re
from pathlib import Path
from typing import ClassVar

import click
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Static,
)

from dko.analysis import DirEntry, get_related_dirs, list_dirs, run_dupe_krill_report
from dko.widgets.dirs import Dirs
from dko.widgets.regex_filter_modal import RegexFilterModal


class OrganizeDirs(App):
    """A Textual app to organize and view directories."""

    CSS = """
    #dirs {
        height: 100%;
        width: 100%;
    }

    #main-container {
        layout: grid;
        width: 100%;
        height: 100%;
        grid-size: 1;
        grid-rows: 3fr 1fr;
    }

    #related-dirs-container {
        height: 100%;
    }
    """

    BINDINGS: ClassVar = [
        ("r", "rerun_dupe_krill", "Re-run dupe-krill"),
        ("q", "quit", "Quit"),
        ("f", "filter", "Filter"),
    ]

    dir_entries: list[DirEntry] | None = None
    dupe_krill_report: bytes | None = None
    regex_filter: str | None = None
    paths: list[Path]

    def __init__(self, paths: list[Path]):
        super().__init__()
        self.paths = paths

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            yield Dirs(id="dirs")
            with Vertical(id="related-dirs-container"):
                yield Static("Related directories:")
                yield ListView(id="related-dirs")
        yield Footer()

    def action_filter(self) -> None:
        self.push_screen(RegexFilterModal(self.regex_filter), self.set_filter)

    def set_filter(self, regex_filter: str | None) -> None:
        self.regex_filter = regex_filter
        self.refresh_dir_entries()

    def on_mount(self) -> None:
        self.rerun_dupe_krill()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self.refresh_related_dirs(event.row_key.value)

    def action_rerun_dupe_krill(self) -> None:
        self.rerun_dupe_krill()

    def rerun_dupe_krill(self) -> None:
        table = self.query_one(Dirs)
        table.loading = True
        self.rerun_dupe_krill_worker(table)

    def refresh_related_dirs(self, target_dir: str | None) -> None:
        list_view = self.query_one(ListView)
        list_view.loading = True
        self.refresh_related_dirs_worker(target_dir, list_view)

    def refresh_dir_entries(self) -> None:
        table = self.query_one(Dirs)
        dir_entries = self.dir_entries
        if self.regex_filter and self.dir_entries:
            try:
                pattern = re.compile(self.regex_filter)
                dir_entries = [
                    entry
                    for entry in self.dir_entries
                    if pattern.search(entry.dir_path)
                ]
            except re.error:
                self.notify(
                    f"Could not filter. '{self.regex_filter} is not valid regex.",
                    severity="error",
                )
        table.update_dir_entries(dir_entries)
        table.focus()

    @work(exclusive=True)
    async def rerun_dupe_krill_worker(self, table: Dirs) -> None:
        self.dupe_krill_report = await run_dupe_krill_report(self.paths)
        if self.dupe_krill_report is not None:
            self.dir_entries = await list_dirs(self.dupe_krill_report)
            self.refresh_dir_entries()
        table.loading = False

    @work(exclusive=True)
    async def refresh_related_dirs_worker(
        self, target_dir: str | None, list_view: ListView
    ) -> None:
        if target_dir and self.dupe_krill_report:
            await asyncio.sleep(0.3)
            related_dirs = await get_related_dirs(self.dupe_krill_report, target_dir)
            list_view.clear()
            if related_dirs is not None:
                for related_dir in related_dirs:
                    list_view.append(ListItem(Label(related_dir)))
        list_view.loading = False


@click.command(name="dirs")
@click.argument("paths", type=Path, nargs=-1, required=True)
def cmd(paths: tuple[Path, ...]) -> None:
    app = OrganizeDirs([path for path in paths if path.is_dir()])
    app.run()
