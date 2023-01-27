import click

from lib import *


@click.command()
def cli():
    # what_is_unit()
    # circuit1()
    parallel_resistor_circuit()

if __name__ == "__main__":
    cli()
