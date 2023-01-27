import PySpice
from PySpice.Spice.Netlist import Circuit, SubCircuitFactory
from PySpice.Probe.WaveForm import OperatingPoint
from PySpice.Unit import *
import PySpice.Logging.Logging as Logging

logger = Logging.setup_logging()

__all__ = [
    'circuit1',
    'what_is_unit',
    'parallel_resistor_circuit',
]

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


class ParallelResistors(SubCircuitFactory):
    __name__ = "ParallelResistors"
    __nodes__ = ('n1', 'n2')

    def __init__(self, *r_units):
        super().__init__()
        for i, r_unit in enumerate(r_units):
            if isinstance(r_unit, type(1@u_Ohm)):
            # if isinstance(r_unit, type(u_Ohm)):
                self.R(i, __nodes__[0], __nodes__[1], r_unit)


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
    circuit = Circuit("Parallel Resistors")

    parallel_resistors = ParallelResistors(2@u_kOhm, 4@u_kOhm, 500@u_Ohm)
    circuit.subcircuit(parallel_resistors)
    circuit.V(1, 1, circuit.gnd, 5@u_V)
    circuit.X('1', 'parallel_resistors', 1, circuit.gnd)