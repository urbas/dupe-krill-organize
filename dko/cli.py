import logging

import click

from dko import cmd_dirs


def setup_logging(verbosity_level: int) -> None:
    """Configure logging based on verbosity level."""
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")
    log_level = min(
        max(logging.DEBUG, logging.WARNING - (verbosity_level * 10)),
        logging.ERROR,
    )
    logging.getLogger().setLevel(log_level)


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase verbosity level.")
@click.option("-q", "--quiet", count=True, help="Decrease verbosity level.")
def main(verbose: int, quiet: int) -> None:
    """Simple CLI tool with various commands."""
    setup_logging(verbose - quiet)


main.add_command(cmd_dirs.cmd)
