import asyncio
import time
from pathlib import Path
from typing import Optional

import typer

from nbterm import __version__
from .notebook import Notebook


def version_callback(value: bool):
    if value:
        typer.echo(f"nbterm {__version__}")
        raise typer.Exit()


def main(
    notebook_path: Optional[Path] = typer.Argument(None, help="Path to the notebook."),
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
):
    nb = Notebook(notebook_path, no_kernel=no_kernel or False, save_path=save_path)
    if run:
        assert no_kernel is not True
        asyncio.run(nb.run_all())
        save_path = save_path or default_save_path(notebook_path)
        nb.save(save_path)
        typer.echo(f"Executed notebook has been saved to: {save_path}")
    else:
        nb.show()


def default_save_path(notebook_path: Optional[Path]) -> Path:
    if notebook_path:
        # TODO: on Python >=3.9, can use https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.with_stem
        return notebook_path.with_name(
            f"{notebook_path.stem}_run{notebook_path.suffix}"
        )
    else:
        return Path.cwd() / f"nbterm-{time.time()}.ipynb"


def cli():
    typer.run(main)


if __name__ == "__main__":
    cli()
