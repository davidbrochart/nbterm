from pathlib import Path

import pytest

from nbterm.nbterm import default_save_path


@pytest.mark.parametrize(
    "notebook_name, save_name",
    [
        ("foo", "foo_run"),
        ("foo.ipynb", "foo_run.ipynb"),
        ("foo_.ipynb", "foo__run.ipynb"),
        ("foo_run.ipynb", "foo_run_run.ipynb"),
    ],
)
def test_default_save_path(notebook_name: str, save_name: str, tmp_path: Path) -> None:
    assert default_save_path(tmp_path / notebook_name) == tmp_path / save_name
