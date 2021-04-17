from typing import Optional

import typer

from nbterm import __version__
from .notebook import Notebook


def version_callback(value: bool):
    if value:
        typer.echo(f"nbterm {__version__}")
        raise typer.Exit()


def main(
    notebook_path: str = typer.Argument("", help="Path to the notebook."),
    run: Optional[bool] = typer.Option(None, "--run", help="Run the notebook."),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, help="Show the version and exit."
    ),
):
    nb = Notebook(notebook_path)
    if run:
        nb.run()
        typer.echo(f"Executed notebook has been saved to: {nb.run_notebook_path}")
    else:
        nb.show()


def cli():
    typer.run(main)


if __name__ == "__main__":
    cli()
