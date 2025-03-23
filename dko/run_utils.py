import asyncio
import logging


def handle_command_error(
    cmd: list[str],
    process: asyncio.subprocess.Process,
    stderr: bytes,
    log: logging.Logger,
) -> bool:
    if process.returncode != 0:
        log.error(
            "Command '%s' failed with return code %d", " ".join(cmd), process.returncode
        )
        log.error("Error output: %s", stderr.decode("utf-8"))
        return True
    return False
