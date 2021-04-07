import click

from .notebook import Notebook


@click.command()
@click.argument("notebook_path", default="")
@click.argument("kernel_spec_path", default="")
def cli(notebook_path, kernel_spec_path):
    Notebook(notebook_path, kernel_spec_path)


if __name__ == "__main__":
    cli()
