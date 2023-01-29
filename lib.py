import os
import math

import numpy as np

import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
from PySpice.Unit import *
from PySpice.Spice.Netlist import Circuit, SubCircuitFactory
from PySpice.Probe.WaveForm import OperatingPoint
from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Physics.SemiConductor import ShockleyDiode


logger = Logging.setup_logging()
libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)


__all__ = [
    'circuit1',
    'what_is_unit',
    'parallel_resistor_circuit',
    'raw_spice_circuit',
    'rectifier_circuit',
]


class ParallelResistors(SubCircuitFactory):
    NAME = "ParallelResistors"
    NODES = ('n1', 'n2',)

    def __init__(self, name:str=NAME, *r_units, **kwargs):
        # Add name
        self.NAME = name
        super().__init__(*[], **kwargs)
        for i, r_unit in enumerate(r_units):
            if isinstance(r_unit, type(1@u_Ohm)):
                self.R(i, self.NODES[0], self.NODES[1], r_unit)
            else:
                raise TypeError("r_unit {} is not a circuit value.".format(r_unit))

class Rectifier(SubCircuitFactory):

    NAME = 'Rectifier'
    NODES = (
        'input_1', 'input_2',
        'output_1', 'output_2',
    )

    def __init__(self, diode_model):
        super().__init__()

        self.X('D1', diode_model, 'input_1', 'output_1')
        self.X('D2', diode_model, 'output_2', 'input_2')
        self.X('D3', diode_model, 'output_2', 'input_1')
        self.X('D4', diode_model, 'input_2', 'output_1')


def what_is_unit():
    option = 1
    # Unit
    if option==1:
        print(type(u_kOhm))
    # Unit with scalar
    elif option==2:
        print(type(2@u_kOhm))
    # Analysis
    elif option==3:
        circuit = Circuit("Meh")
        circuit.V(1, 'top', circuit.gnd, 1@u_V)
        circuit.R(1, 'top', circuit.gnd, 1@u_kOhm)
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.operating_point()
        print(type(analysis))

def print_nodes(analysis:OperatingPoint):
    if isinstance(analysis, OperatingPoint):
        for node in analysis.nodes.values():
            print('Node {}: {:4.1f}'.format(str(node), float(node)))
    else:
        raise TypeError("{} is not of the correct type: {}".format(analysis, OperatingPoint))



def circuit1():
    """ 
    Run the 1st designed circuit. 
    Voltage Divider.
    """

    # Circuit netlist
    circuit = Circuit('Voltage Divider')

    circuit.V('input', 1, circuit.gnd, 4@u_V)
    circuit.R(1, 1, 'output', 3@u_kOhm)
    circuit.R(2, 'output', circuit.gnd, 1@u_kOhm)

    # DC operating point analysis
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()

    print(circuit)

    # Print Voltages at nodes
    print_nodes(analysis)

def parallel_resistor_circuit():
    circuit = Circuit("ParallelResistors")

    parallel_resistors = ParallelResistors(2@u_kOhm, 4@u_kOhm, 500@u_Ohm)
    circuit.subcircuit(parallel_resistors)
    circuit.X('1', parallel_resistors.NAME, 1, circuit.gnd)
    circuit.V(1, 1, circuit.gnd, 5@u_V)
    print(circuit)

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()

    print_nodes(analysis)

def raw_spice_circuit():
    """ 
    Use raw spice text to create circuit.
    Reads 'Netlist' text file under 'assets'.
      """
    text = "".join(open(os.path.join(os.getcwd(),"assets/raw_spice.txt")).readlines())
    # print(text)

    circuit = Circuit("Raw Spice")
    circuit.raw_spice = text
    # circuit.R(2, 'out', 0, raw_spice='1k')

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    print_nodes(analysis)

    print(circuit)


def rectifier_circuit():
    circuit = Circuit("Rectifier")

    diode = spice_library['1N4148']
    print("These are the components in the spice library.")
    for k,v in spice_library.items():
        print("{}|{}".format(k,v))
    # circuit.include(diode)