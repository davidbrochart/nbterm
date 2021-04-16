import typer

from .notebook import Notebook  # type: ignore


def main(
    notebook_path: str = typer.Argument("", help="Path to the notebook"),
    run: bool = typer.Option(False, help="Run the Notebook"),
):
    nb = Notebook(notebook_path)
    if run:
        nb.run()
    else:
        nb.show()


def cli():
    typer.run(main)


if __name__ == "__main__":
    cli()
