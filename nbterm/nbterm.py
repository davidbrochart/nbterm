import sys
from pathlib import Path
import asyncio
from typing import Optional

import typer

from nbterm import __version__
from .notebook import Notebook


def version_callback(value: bool):
    if value:
        typer.echo(f"nbterm {__version__}")
        raise typer.Exit()


def find_available_name(directory: Path, prefix: str):
    notebooks = list(directory.glob(f"{prefix}*.ipynb"))
    notebook_path = directory / f"{prefix}.ipynb"
    i = 0
    while True:
        if notebook_path not in notebooks:
            break
        i += 1
        notebook_path = directory / f"{prefix}{i}.ipynb"
    return notebook_path


def main(
    notebook_path: Optional[Path] = typer.Argument(None, help="Path to the notebook."),
    kernel_cwd: Optional[Path] = typer.Option(
        None, help="Working directory of the kernel."
    ),
    no_kernel: Optional[bool] = typer.Option(
        None, "--no-kernel", help="Don't launch a kernel."
    ),
    run: Optional[bool] = typer.Option(None, "--run", help="Run the notebook."),
    save_path: Optional[Path] = typer.Option(
        None, "--save-path", help="Path to save the notebook."
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, help="Show the version and exit."
    ),
    test: Optional[str] = typer.Option(None, "--test", help="N/A (for testing)."),
):
    prefix = "Untitled"
    if notebook_path is None:
        notebook_path = find_available_name(Path("."), prefix)
    elif notebook_path.is_dir():
        notebook_path = find_available_name(notebook_path, prefix)
    assert notebook_path is not None
    if not notebook_path.parent.is_dir():
        typer.echo(f"Not a directory: {notebook_path.parent}")
        sys.exit(1)
    if kernel_cwd is None:
        kernel_cwd = notebook_path.parent
    if not kernel_cwd.is_dir():
        typer.echo(f"kernel-cwd is not a directory: {kernel_cwd}")
        sys.exit(1)
    if test is not None:
        typer.echo(f"notebook_path={notebook_path}")
        typer.echo(f"kernel_cwd={kernel_cwd}")
        sys.exit(0)
    nb = Notebook(
        notebook_path,
        kernel_cwd=kernel_cwd,
        no_kernel=no_kernel or False,
        save_path=save_path,
    )
    if run:
        assert no_kernel is not True
        asyncio.run(nb.run_all())
        if save_path is None:
            directory = notebook_path.parent
            prefix = str(directory / f"{notebook_path.stem}_run")
            save_path = find_available_name(directory, prefix)
        nb.save(save_path)
        typer.echo(f"Executed notebook has been saved to: {save_path}")
    else:
        nb.show()


def cli():
    typer.run(main)


if __name__ == "__main__":
    cli()
