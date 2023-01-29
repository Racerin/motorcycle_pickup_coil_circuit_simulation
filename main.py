import click

from lib import *


@click.command()
def cli():
    click.echo("Hi!")
    # what_is_unit()
    # circuit1()
    # raw_spice_circuit()
    # parallel_resistor_circuit()
    # read_num_from_text_file()
    # rectifier_circuit()
    engine_pickup_sensor_circuit()

if __name__ == "__main__":
    cli()
