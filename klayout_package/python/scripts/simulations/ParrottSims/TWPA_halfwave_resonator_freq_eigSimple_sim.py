"""
Sweeep coupling length for half wave resonator without the band pass filtering
structure.

fcenter = 7.25 GHz -> lambda/2 = 1/2 vph / fc = 8762.9 um
fres1 = 7.137 GHz -> lambda/2 = 1/2 vph / fc = 8901.7 um

er = 5.5668
c / np.sqrt(er)
np.float64(127062645.60234061)
vph = c / np.sqrt(er)
fc = 7.25e9
0.5 * vph / fc
np.float64(0.008762941076023491)
fc = 7.137e9
0.5 * vph / fc
np.float64(0.008901684573514125)
"""

from scipy.constants import *

import logging
import sys
from pathlib import Path

from kqcircuits.pya_resolver import pya
from kqcircuits.simulations.export.ansys.ansys_export import export_ansys
from kqcircuits.simulations.export.simulation_export import (
    export_simulation_oas,
    sweep_simulation,
)
from kqcircuits.simulations.simulation import Simulation
from kqcircuits.util.parameters import Param, pdt
from kqcircuits.simulations.port import EdgePort, InternalPort
from kqcircuits.chips.BP_Purcell import PurcellQubits

from kqcircuits.elements.halfwave_resonator import HalfWaveResonator

from kqcircuits.elements.waveguide_coplanar import WaveguideCoplanar

from kqcircuits.simulations.export.simulation_export import cross_sweep_simulation
from kqcircuits.simulations.single_element_simulation import (
    get_single_element_sim_class,
)

from kqcircuits.util.export_helper import (
    create_or_empty_tmp_directory,
    get_active_or_new_layout,
    open_with_klayout_or_default_application,
)
from kqcircuits.util.parameters import add_parameters_from

# or should this be in sim_params?

# Prepare output directory
dir_path = create_or_empty_tmp_directory(Path(__file__).stem + "_output")

box_size_x = 2000
box_y2 = 2000
box_y1 = -500


# Simulation parameters
sim_class = get_single_element_sim_class(
    HalfWaveResonator,
    transformation_from_center=lambda cell: pya.DTrans(
        0, False, -3750, -(box_y1 + box_y2) / 2.0 - 3750
    ),
    ignore_ports=['HR_U0_port_a', 'HR_U0_port_b']
)

sim_parameters = {
    "name": "halfwave_linewidth_sim",
    # "use_internal_ports": True,
    "box": pya.DBox(
        pya.DPoint(-box_size_x / 2.0, box_y1),
        pya.DPoint(box_size_x / 2.0, box_y2),
    ),
    "launchers": False,
    "qubits": False,
    "removeFilter": True,
    # "use_ports": True,
    "face_stack": [
        "1t1",
    ],  # chip distance default at 8um
    "substrate_material": ["sapphire"],
    "material_dict": "{'sapphire': {'permittivity': 10.5}}",
    # "a": 3.5,  # readout structure a in flip chip
    # "b": 32,  # readout structure b in flip chip
    "airbridge_height": 50,
    "inputCapControl": 6.2,
    "outputCapControl": 9.8,
    "filter_length": 8762.9,
    # "resonator_lengths": [
    #     8901.7,
    # ],
    "resonator_couplings": [100],
    # "filter_positions": [0.5],
}

export_parameters = {
    "ansys_tool": "eigenmode",
    "path": dir_path,
    "maximum_passes": 8,
    "percent_refinement": 30,
    "n_modes": 1,
    "min_frequency": 2,
    "exit_after_run": True,
    "skip_errors": False,
    "mesh_size": {"1t1_gap": 8},
}

# Get layout
logging.basicConfig(level=logging.WARN, stream=sys.stdout)
layout = get_active_or_new_layout()

# # Sweep simulations for variable geometry
simulations = cross_sweep_simulation(
    layout,
    sim_class,
    sim_parameters,
    {
        # "resonator_couplings": [[50], [200]],
        "filter_positions": [[0.5], [0.3]],
        "resonator_lengths": [[8840.0], [8778.0], [8717.0], [8657.0], [8597.0], [8539.0]],
    },
)

# Fixed geometry simulation
# simulations = [sim_class(pya.Layout(), **sim_parameters)]

# Export Ansys files
export_ansys(simulations, **export_parameters)

# Write and open oas file
open_with_klayout_or_default_application(export_simulation_oas(simulations, dir_path))
