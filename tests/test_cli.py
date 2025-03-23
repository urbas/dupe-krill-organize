from click.testing import CliRunner

from dko.cli import main


def test_help():
    """Test that --help prints usage information."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
