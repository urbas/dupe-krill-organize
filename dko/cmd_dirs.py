import asyncio
from pathlib import Path
from typing import ClassVar

import click
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import DataTable, Footer, Header, Label, ListItem, ListView, Static

from dko.analysis import get_related_dirs, list_dirs, run_dupe_krill_report
from dko.widgets.dirs import Dirs


class OrganizeDirs(App):
    """A Textual app to organize and view directories."""

    CSS = """
    #dirs {
        height: 100%;
    }

    #main-container {
        layout: grid;
        width: 100%;
        height: 100%;
        grid-size: 1 2;
        grid-rows: 3fr 1fr;
    }

    #related-dirs-container {
        height: 100%;
    }

    #related-dirs {
    }
    """

    BINDINGS: ClassVar = [
        ("r", "rerun_dupe_krill", "Re-run dupe-krill"),
        ("q", "quit", "Quit"),
    ]

    paths: list[Path]
    dupe_krill_report: bytes | None = None

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

    @work(exclusive=True)
    async def rerun_dupe_krill_worker(self, table: Dirs) -> None:
        self.dupe_krill_report = await run_dupe_krill_report(self.paths)
        if self.dupe_krill_report is not None:
            dir_entries = await list_dirs(self.dupe_krill_report)
            table.update_dir_entries(dir_entries)
            table.focus()
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
