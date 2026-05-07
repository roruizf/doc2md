import os
import stat
from pathlib import Path

from typer.testing import CliRunner

from doc2md.cli import app


def test_install_wsl_script_is_executable_and_uses_bash() -> None:
    script = Path("scripts/install_wsl.sh")

    assert script.exists()
    assert script.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash")
    assert os.stat(script).st_mode & stat.S_IXUSR


def test_cli_version_returns_package_version() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == "0.1.0"
