from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from nbterm.nbterm import main

app = typer.Typer()
app.command()(main)

runner = CliRunner()


def get_value(key, text):
    for line in text.splitlines():
        if line.startswith(f"{key}="):
            return line[line.find("=") + 1 :]  # noqa


def test_untitled():
    for untitled in Path(".").glob("Untitled*.ipynb"):
        untitled.unlink()
    result = runner.invoke(app, ["--test", "0"])
    assert result.exit_code == 0
    assert get_value("notebook_path", result.stdout) == "Untitled.ipynb"
    assert get_value("kernel_cwd", result.stdout) == "."


@pytest.mark.parametrize(
    "notebook_name", ["Untitled.ipynb", "Untitled1.ipynb", "Untitled2.ipynb"]
)
def test_untitled_in_directory(notebook_name, tmp_dir):
    result = runner.invoke(app, [str(tmp_dir), "--test", "0"])
    assert result.exit_code == 0
    assert get_value("notebook_path", result.stdout) == str(tmp_dir / notebook_name)
    assert get_value("kernel_cwd", result.stdout) == str(tmp_dir)
    # write empty file for next test
    open(str(tmp_dir / notebook_name), "wt").close()


def test_notebook_path(tmp_dir):
    path = str(tmp_dir / "foo.ipynb")
    result = runner.invoke(app, [path, "--test", "0"])
    assert result.exit_code == 0
    assert get_value("notebook_path", result.stdout) == path
    assert get_value("kernel_cwd", result.stdout) == str(tmp_dir)


def test_kernel_cwd(tmp_dir):
    result = runner.invoke(app, ["--kernel-cwd", str(tmp_dir), "--test", "0"])
    assert result.exit_code == 0
    assert get_value("kernel_cwd", result.stdout) == str(tmp_dir)
