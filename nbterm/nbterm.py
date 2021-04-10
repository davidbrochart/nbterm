import typer

from .notebook import Notebook


def main(notebook_path: str = typer.Argument("")):
    Notebook(notebook_path)


def cli():
    typer.run(main)


if __name__ == "__main__":
    cli()
