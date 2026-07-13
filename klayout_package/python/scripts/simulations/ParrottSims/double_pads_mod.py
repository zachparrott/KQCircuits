# This code is part of KQCircuits
# Copyright (C) 2022 IQM Finland Oy
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see
# https://www.gnu.org/licenses/gpl-3.0.html.
#
# The software distribution should follow IQM trademark policy for open-source software
# (meetiqm.com/iqm-open-source-trademark-policy). IQM welcomes contributions to the code.
# Please see our contribution agreements for individuals (meetiqm.com/iqm-individual-contributor-license-agreement)
# and organizations (meetiqm.com/iqm-organization-contributor-license-agreement).

import logging
import sys
from pathlib import Path

import numpy as np

from kqcircuits.qubits.double_pads import DoublePads
from kqcircuits.simulations.post_process import PostProcess
from kqcircuits.simulations.single_element_simulation import (
    get_single_element_sim_class,
)
from kqcircuits.pya_resolver import pya
from kqcircuits.simulations.export.ansys.ansys_export import export_ansys
from kqcircuits.simulations.export.simulation_export import export_simulation_oas
from kqcircuits.util.export_helper import (
    create_or_empty_tmp_directory,
    get_active_or_new_layout,
    open_with_klayout_or_default_application,
)


# Simulation parameters
SimClass = get_single_element_sim_class(DoublePads)
sim_parameters = {
    "name": "double_pads",
    "use_internal_ports": True,
    "use_ports": True,
    "face_stack": ["1t1"],
    "box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(2000, 2000)),
    # sets the extent of the cpw coupler
    "waveguide_length": 200,
}

dir_path = create_or_empty_tmp_directory(Path(__file__).stem + "_output_q3d")

# Add eigenmode and Q3D specific settings
# fmt: off
export_parameters_ansys = {
    'percent_error': 1,
    'maximum_passes': 18,
    'minimum_passes': 2,
    'minimum_converged_passes': 2,
} 

export_parameters_ansys = {
    "ansys_tool": "q3d",
    "path": dir_path,
    "exit_after_run": True,
    "post_process": PostProcess("produce_cmatrix_table.py"),
    **export_parameters_ansys,
}

    
# Get layout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
layout = get_active_or_new_layout()

    # Sweep simulations
    # Here, we sweep coupler width with two different island-island gap widths:
    #   70 µm = 15.25 * 2 + 39.5
    #   150µm = 55.25 * 2 + 29.5
    # SIM junction set to 39.5 so that the gap between junction islands is same as that gap in Manhattan junction
    # Adapt taper widths to have 15 degree tapering angle from y-axis. Widths are different for each island
    # according to the Manhattan junction

simulations = []

pad_length = np.linspace(300, 500, 3, dtype=float).tolist()
island_extent = [[p, 100] for p in pad_length]

for extent in island_extent:
    name = sim_parameters["name"]
    name = f"{name}_pad_length_{int(extent[0])}"
    simulations += [
        SimClass(
            layout,
            **{
                **sim_parameters,
                "ground_gap": [900, 900],
                "a": 5,
                "b": 20,
                "coupler_a": 5,
                "coupler_extent": [150, 30],
                "island1_extent": extent,
                "island2_extent": extent,
                "coupler_offset": 100,
                "junction_type": "Manhattan",
                "junction_total_length": 30,
                "name": name,
            },
        )
    ]

# Create simulation
oas = export_simulation_oas(simulations, dir_path)

export_ansys(simulations, **export_parameters_ansys)

logging.info(f"Total simulations: {len(simulations)}")
open_with_klayout_or_default_application(oas)
