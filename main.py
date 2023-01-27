import click

from lib import *


@click.command()
def cli():
    click.echo("Hi!")
    # what_is_unit()
    # circuit1()
    parallel_resistor_circuit()
    pass

if __name__ == "__main__":
    cli()
