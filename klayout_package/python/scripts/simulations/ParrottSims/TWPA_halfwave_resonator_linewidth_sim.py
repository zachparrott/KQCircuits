# This code is part of KQCircuits
# Copyright (C) 2025 Zachary Parrott
# Copyright (C) 2023 IQM Finland Oy
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see https://www.gnu.org/licenses/gpl-3.0.html.
#
# Contributions are made under the IQM Individual Contributor License Agreement.
# For more information, see: https://meetiqm.com/iqm-individual-contributor-license-agreement

"""
Sweeep coupling length for half wave resonator without the band pass filtering
structure.

"resonator_lengths": [[8796.6], [8707.5], [8615.5], [8226.0]],

Using phase velocity from 0.1% eigenmode in halwwave_parse_results.ipynb
"""

from scipy.constants import *

import logging
import sys
from pathlib import Path

from kqcircuits.pya_resolver import pya
from kqcircuits.simulations.export.ansys.ansys_export import export_ansys
from kqcircuits.simulations.export.simulation_export import export_simulation_oas, sweep_simulation
from kqcircuits.simulations.simulation import Simulation
from kqcircuits.util.parameters import Param, pdt
from kqcircuits.simulations.port import EdgePort, InternalPort
from kqcircuits.chips.BP_Purcell import PurcellQubits

from kqcircuits.elements.halfwave_resonator import HalfWaveResonator

from kqcircuits.elements.waveguide_coplanar import WaveguideCoplanar

from kqcircuits.simulations.export.simulation_export import cross_sweep_simulation
from kqcircuits.simulations.single_element_simulation import get_single_element_sim_class

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
    transformation_from_center=lambda cell: pya.DTrans(0, False, -3750, -(box_y1 + box_y2) / 2.0 - 3750),
)

sim_parameters = {
    "name": "halfwave_linewidth_sim_try2",
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
    "inputCapControl": 6.2,
    "outputCapControl": 9.8,
    "filter_length": 8762.9,
    "resonator_lengths": [8901.7, ],
    "filter_positions": [0.5],
}

export_parameters = {
    "path": dir_path,
    "max_delta_s": 0.05,
    "maximum_passes": 8,
    "frequency": 7.25,
    "sweep_start": 7.0,
    "sweep_end": 7.5,
    "sweep_count": 501,
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
        "resonator_lengths": [[8796.6], [8707.5], [8615.5], [8527.7]], 
        "resonator_couplings": [[200], [300], [400], [500]]
        # "resonator_lengths": [[8796.6],], 
        # "resonator_couplings": [[25], [50]]
    },
)

# Fixed geometry simulation
# simulations = [sim_class(pya.Layout(), **sim_parameters)]

# Export Ansys files
export_ansys(simulations, **export_parameters)

# Write and open oas file
open_with_klayout_or_default_application(export_simulation_oas(simulations, dir_path))
