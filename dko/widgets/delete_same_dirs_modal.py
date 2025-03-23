import asyncio
import logging
import subprocess

from textual import events, work
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView

from dko.analysis import get_related_dirs

logger = logging.getLogger(__name__)


def delete_dirs(dirs: list[str]) -> None:
    for dir_path in dirs:
        subprocess.run(["rm", "-rf", dir_path], check=True)


async def is_same_content(dir1: str, dir2: str) -> bool:
    cmd = ["diff", "-r", dir1, dir2]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _stdout, _stderr = await process.communicate()
    return process.returncode == 0


class DeleteSameDirsModal(ModalScreen):
    """Delete directories below and keep the selected directory."""

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
        color: $error;
        text-style: bold;
    }

    #identical-dirs-list {
        border: solid $error;
    }
    """

    same_dirs: list[str] | None = None

    def __init__(self, selected_dir: str, dupe_krill_report: bytes | None):
        super().__init__()
        self.selected_dir = selected_dir
        self.dupe_krill_report = dupe_krill_report

    def compose(self):
        with Container(id="dialog"):
            yield Label(
                f"Delete directories below and keep '{self.selected_dir}'?",
                id="title",
            )
            yield ListView(id="identical-dirs-list")
            yield Label("Press ENTER to confirm or ESC to cancel.")

    def on_mount(self) -> None:
        list_view = self.query_one(ListView)
        list_view.loading = True
        self.load_same_dirs_worker()

    def on_key(self, event: events.Key):
        if event.name == "escape":
            self.dismiss()
        elif event.name == "enter":
            if not self.same_dirs:
                self.notify("Nothing to delete. Still looking for same directories?")
                return
            delete_dirs(self.same_dirs)
            self.notify(f"Deleted directories: {self.same_dirs}")
            self.dismiss()

    @work(exclusive=True)
    async def load_same_dirs_worker(self) -> None:
        list_view = self.query_one(ListView)
        if self.selected_dir and self.dupe_krill_report:
            related_dirs = await get_related_dirs(
                self.dupe_krill_report, self.selected_dir
            )
            list_view.clear()
            if related_dirs is not None:
                self.same_dirs = [
                    related_dir
                    for related_dir in related_dirs
                    if related_dir != self.selected_dir
                    and await is_same_content(self.selected_dir, related_dir)
                ]
                list_view.extend(
                    [
                        ListItem(Label(related_dir), name=related_dir)
                        for related_dir in self.same_dirs
                    ]
                )
        list_view.loading = False
