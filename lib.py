import os
import math
import numbers
from collections.abc import Sequence

import numpy as np

import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
from PySpice.Unit import *
from PySpice.Probe.Plot import plot
from PySpice.Spice.NgSpice.Shared import NgSpiceShared
from PySpice.Spice.Netlist import Circuit, SubCircuitFactory
from PySpice.Probe.WaveForm import OperatingPoint
from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Physics.SemiConductor import ShockleyDiode


logger = Logging.setup_logging()

ASSET_PATH = os.path.join(os.getcwd(), 'assets')

libraries_path = os.path.join(ASSET_PATH, 'examples')
spice_library = SpiceLibrary(libraries_path)
# spice_library = SpiceLibrary('/lib/')


__all__ = [
    'circuit1',
    'what_is_unit',
    'parallel_resistor_circuit',
    'raw_spice_circuit',
    'read_num_from_text_file',
    'rectifier_circuit',
    'engine_pickup_sensor_circuit',
    'engine_pickup_sensor_circuit_2',
]




def read_num_from_text_file(filename:str="No load.txt") -> list[float]:
    """ Reads numbers per line from text file """
    numbers = []
    path = os.path.join(ASSET_PATH, filename)
    with open(path) as file:
        for line in file.readlines():
            try:
                num = float(line.strip())
                numbers.append(num)
            except ValueError:
                pass
    return numbers
    

class MyNgSpiceShared(NgSpiceShared):


    def __init__(
            self, voltages:Sequence=None, step_time=None, end_time:float=1.0,
            default_voltage=0, **kwargs):
        super().__init__(**kwargs)

        # Ternary Operators
        self.voltages = voltages if isinstance(voltages, Sequence) \
            else read_num_from_text_file()
        self.end_time = end_time
        self.step_time = step_time if isinstance(step_time, numbers.Number) \
            else self.end_time / len(self.voltages)
        self.default_voltage = default_voltage

        # Preping for callback function
        self.callback_voltages = self.voltages.copy()
        self.callback_voltages.reverse()

    
    def get_vsrc_data(self, voltage, time, node, ngspice_id):
        self._logger.debug('ngspice_id-{} get_vsrc_data @{} node {}'.format(ngspice_id, time, node))
        # voltage[0] = self.__voltages[0]
        # voltage[0] = 10@u_V * math.sin(50@u_Hz.pulsation * time)
        try:
            volt = self.callback_voltages.pop()
            voltage[0] = volt
        except IndexError:
            # If I used up the voltage inputs, use '0' by default.
            voltage[0] = self.default_voltage
        return 0

    def get_isrc_data(self, current, time, node, ngspice_id):
        print(current, time, node, ngspice_id)
        self._logger.debug('ngspice_id-{} get_isrc_data @{} node {}'.format(ngspice_id, time, node))
        current[0] = 1
        return 0

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

    def __init__(self, diode_model, name=NAME):
        self.NAME = name
        super().__init__()
        self.X('D1', diode_model, 'input_1', 'output_1')
        self.X('D2', diode_model, 'output_2', 'input_2')
        self.X('D3', diode_model, 'output_2', 'input_1')
        self.X('D4', diode_model, 'input_2', 'output_1')


def closest_input_for_output(dict1:dict, key)->'dict1[key]':
    """ Returns the value corresponding to the best matching key. """
    assert isinstance(dict1, dict), "dict1 is not of type 'dictionary'."
    # Checks
    if dict1 == dict():
        return None
    # Setting default values to compare with
    best_key = list(dict1.keys())[0]
    best_value, best_score = dict1[best_key], None
    if isinstance(key, numbers.Number):
        assert all((isinstance(k,numbers.Number) for k in dict1.keys()))
        if best_score is None:
            best_score = abs(best_key - key)
        for k,v in dict1.items():
            # The closer the key and value's key, the better the score
            if abs(k - key) < best_score:
                best_value = v
            # Best possible answer
            if best_score == 0: break
    else:
        raise TypeError("type '{}' is not supported for the function 'closest_input_for_output'.".format(type(key)))
    return best_value

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
    text = "".join(open(os.path.join(ASSET_PATH, "raw_spice.txt")).readlines())

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
    rectifier = Rectifier(diode_model=diode)
    circuit.V('input', 'input', circuit.gnd, 0.7@u_V)
    circuit.subcircuit(rectifier)
    # circuit.X('1', rectifier.NAME, 'input', circuit.gnd, , )

def engine_pickup_sensor_circuit():
    circuit = Circuit("Rectify External Voltage")

    diode = spice_library['1N4148']
    circuit.include(diode)

    # circuit.V('input', 'input', circuit.gnd, 'dc 0 external')
    circuit.V('input', 'input', circuit.gnd, 14.4@u_V)
    circuit.R(1, 'in', 'out', 700@u_Ohm)
    circuit.X('D1', '1N4148', 'out', circuit.gnd)
    print(circuit)

    simulator = circuit.simulator()
    voltages = read_num_from_text_file()

    # STOPPED HERE
    slice1 = slice(0, max(voltages), 1e-3)
    analysis = simulator.dc(Vinput=slice1)

    n_voltages = len(voltages)
    times = np.linspace(0, 10*0.05, num=n_voltages)
    if False:
        t_input_voltage_pair = dict()
        for i in range(n_voltages):
            t_input_voltage_pair.update({times[i]:voltages[i]})
        # output_voltages = [closest_input_for_output(dict1, analysis.out[t]) for t in times]
    
    figure, axis = plt.subplots(1,1)
    # axis.plot(t, voltages, t, analysis.Vinput)
    # axis.plot(times, voltages, times, output_voltages)
    
    analysis = simulator.transient(step_time=1@u_us, end_time=2@u_s)
    axis.plot(times, voltages, times, analysis.out)


    axis.set(xlabel='Time (s)', ylabel='Voltage (V)', title="Graph showing response of voltage.")
    axis.grid()

    # fig.savefig("meh.png")
    plt.show()

    # print(diode, 'diode')
    # circuit.include(diode)

def engine_pickup_sensor_circuit_2():
    """ 
        Use Transient method to simulate circuit.

        References:
        - most important: 
            https://pyspice.fabrice-salvaire.fr/releases/v1.4/examples/ngspice-shared/external-source.html#simulation-using-external-sources
        - others: 
            https://pyspice.fabrice-salvaire.fr/releases/v1.5/examples/diode/diode-characteristic-curve.html#simulation
            https://pyspice.fabrice-salvaire.fr/releases/v1.5/api/PySpice/Spice/Simulation.html#PySpice.Spice.Simulation.CircuitSimulation.transient
    """
    circuit = Circuit("Rectify External Voltage")

    diode = spice_library['1N4148']
    # The following line is the issue
    # circuit.include(diode)
    pathh = "assets\examples\libraries\diode\general-purpose\BAV21.lib"
    # circuit.include(pathh)

    circuit.V('input', 'input', circuit.gnd, 'dc 0 external')
    circuit.R(1, 'input', 'output', 700@u_Ohm)
    circuit.model('1N4148PH', 'D', IS=4.352@u_uA, RS=0.6458@u_Ohm, BV=110@u_V, IBV=0.0001@u_V, N=1.906)
    circuit.Diode(1, 'output', circuit.gnd, model="1N4148PH")
    # circuit.X('D1', '1N4148', 'output', circuit.gnd)
    # circuit.R(2, 'output', circuit.gnd, 700@u_Ohm)
    print(circuit)

    ngspice_shared = MyNgSpiceShared(step_time=1e-6, end_time=0.5)
    # ngspice_shared = MyNgSpiceShared(end_time=1)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25,
        simulator='ngspice-shared', ngspice_shared=ngspice_shared)

    analysis = simulator.transient(
        step_time=ngspice_shared.step_time, end_time=ngspice_shared.end_time
        )
    # analysis = simulator.transient(step_time=1@u_us, end_time=10*50@u_us)

    figure, axis = plt.subplots()
    axis.set(xlabel='Time (m??)', ylabel='Voltage (V)', title="Graph showing response of voltage.")
    axis.grid()
    axis.plot(analysis.input)
    axis.plot(analysis.output)
    axis.legend(('input', 'output'), loc=(0.05, 0.1))

    # fig.savefig("meh.png")
    plt.show()