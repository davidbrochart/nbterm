import click

from .notebook import Notebook


@click.command()
@click.argument("nb-path", default="")
def cli(nb_path):
    Notebook(nb_path)


if __name__ == "__main__":
    cli()
