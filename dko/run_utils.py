import asyncio
import logging


def handle_command_error(
    cmd: list[str],
    result: asyncio.subprocess.Process,
    stderr: bytes,
    log: logging.Logger,
) -> bool:
    if result.returncode != 0:
        log.error(
            "Command '%s' failed with return code %d", " ".join(cmd), result.returncode
        )
        log.error("Error output: %s", stderr.decode("utf-8"))
        return True
    return False
