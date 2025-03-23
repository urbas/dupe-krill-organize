from typing import ClassVar

from textual.widgets import DataTable

from dko.analysis import DirEntry


class Dirs(DataTable):
    dir_entries: list[DirEntry] | None = None
    sort_order: list[str]
    sort_reverse: bool = True

    BINDINGS: ClassVar = [
        ("1", "sort_by_dupes", "Sort By Dupes"),
        ("2", "sort_by_related_dirs", "Sort By Related Dirs"),
        ("3", "sort_by_dir_path", "Sort By Dir Path"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sort_order = ["dupes", "related_dirs", "dir_path"]
        self.add_column("Dupes", key="dupes")
        self.add_column("Related Dirs", key="related_dirs")
        self.add_column("Directory Path", key="dir_path")
        self.cursor_type = "row"

    def update_dir_entries(self, dir_entries: list[DirEntry] | None) -> None:
        if self.dir_entries != dir_entries:
            self.dir_entries = dir_entries
            self._update_ui()

    def _update_sort_order(self, sort_type: str) -> None:
        """Update the sort order based on the selected column.

        If the column is already the primary sort, toggle the sort direction.
        Otherwise, make it the primary sort column with descending order.
        """
        if self.sort_order[0] == sort_type:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_order.remove(sort_type)
            self.sort_order.insert(0, sort_type)
            self.sort_reverse = True
        self._update_sorting()

    def _update_ui(self) -> None:
        self.clear()
        if self.dir_entries:
            for dir_entry in self.dir_entries:
                self.add_row(
                    dir_entry.dupe_count,
                    dir_entry.related_dirs,
                    dir_entry.dir_path,
                    key=dir_entry.dir_path,
                )
            self._update_sorting()

    def _update_sorting(self) -> None:
        self.sort(*self.sort_order, reverse=self.sort_reverse)

    def action_sort_by_dupes(self) -> None:
        self._update_sort_order("dupes")

    def action_sort_by_related_dirs(self) -> None:
        self._update_sort_order("related_dirs")

    def action_sort_by_dir_path(self) -> None:
        self._update_sort_order("dir_path")
