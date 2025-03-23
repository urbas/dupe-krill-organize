import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

from dko.run_utils import handle_command_error

LOG = logging.getLogger(__name__)


@dataclass
class DirEntry:
    """Represents a directory with duplicate files."""

    dir_path: str
    dupe_count: int
    related_dirs: int


async def run_dupe_krill_report(paths: list[Path]) -> bytes | None:
    cmd = ["dupe-krill", "--dry-run", "--json"]
    cmd.extend(str(path) for path in paths)

    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout_bytes, stderr_bytes = await process.communicate()

    if handle_command_error(cmd, process, stderr_bytes, LOG):
        return None
    return stdout_bytes


async def list_dirs(dupe_krill_report: bytes) -> list[DirEntry] | None:
    cmd = ["dupe-krill-analyze", "list-dirs"]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_bytes, stderr_bytes = await process.communicate(input=dupe_krill_report)

    if handle_command_error(cmd, process, stderr_bytes, LOG):
        return None

    entries = []
    for line in stdout_bytes.decode("utf-8").strip().splitlines():
        if not line:
            continue
        parts = line.split(maxsplit=2)
        if len(parts) == 3:
            dupe_count = int(parts[0])
            related_dirs = int(parts[1])
            dir_path = parts[2]
            entries.append(
                DirEntry(
                    dir_path=dir_path, dupe_count=dupe_count, related_dirs=related_dirs
                )
            )

    return entries


async def get_related_dirs(
    dupe_krill_report: bytes, target_dir: str
) -> list[str] | None:
    cmd = ["dupe-krill-analyze", "related-dirs", target_dir]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_bytes, stderr_bytes = await process.communicate(input=dupe_krill_report)

    if handle_command_error(cmd, process, stderr_bytes, LOG):
        return None
    return stdout_bytes.decode("utf-8").strip().splitlines()
