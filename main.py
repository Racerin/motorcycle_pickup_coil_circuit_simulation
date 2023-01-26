import click

from lib import *


@click.command()
def cli():
    click.echo("My project echo.")

if __name__ == "__main__":
    cli()
