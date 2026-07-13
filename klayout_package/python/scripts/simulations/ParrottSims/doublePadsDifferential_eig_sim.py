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

from kqcircuits.qubits.double_pads_diff import DoublePadsDifferential
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
SimClass = get_single_element_sim_class(DoublePadsDifferential)
sim_parameters = {
    "name": "double_pads_eigenmode",
    "use_internal_ports": True,
    "use_ports": True,
    "box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(3000, 2000)),
    "port_size": 200,
    "face_stack": ["1t1"],
    "chip_distance": 8,
    "substrate_material": ["sapphire"],
    "material_dict": "{'sapphire': {'permittivity': 10.5}}",
    "a": 8,
    "b": 4,
    "ground_gap_r": 10,
    "coupler_a": 8,
    "coupler_r": 10,
    "coupler_offset": 10,
    "island1_r": 10,
    "island2_r": 10,
    "island_island_gap": 70,
    "island1_taper_width": 50,
    "island1_taper_junction_width": 25,
    "island2_taper_width": 50,
    "island2_taper_junction_width": 25,
    # set the simulation junction to match intended junction height
    "junction_total_length": 12,
    "junction_upper_pad_length": 2,
    "junction_lower_pad_length": 2,
    "junction_upper_pad_width": 2,
    "junction_lower_pad_width": 2,
    # extend the CPW of the coupler
    "waveguide_length": 200,
}

dir_path = create_or_empty_tmp_directory(Path(__file__).stem + "_output")

# Add eigenmode and Q3D specific settings
# fmt: off
export_parameters_ansys = {
    'maximum_passes': 12,
    'minimum_passes': 2,
    'minimum_converged_passes': 2,
    'min_frequency': 2,
    "n_modes": 1,
    'max_delta_f': 0.1,
}

export_parameters_ansys = {
    "ansys_tool": "eigenmode",
    "path": dir_path,
    "exit_after_run": True,
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

pad_widths = [783.4, ] #805.9, 827.7, 849.9]
coupler_heights = [284.5, ] #333.7, 396.3, 465.9]

simulations = []
for island2_width, coupler_height in zip(
    pad_widths, coupler_heights
):
    name = sim_parameters["name"]
    name = f"{name}_pad_width_{int(island2_width)}"
    simulations += [
        SimClass(
            layout,
            **{
                **sim_parameters,
                "island1_extent": [
                    max(
                        island2_width - 400,
                        100  # coupler width
                        + 2 * sim_parameters["coupler_offset"]
                        + 4 * sim_parameters["island1_r"],
                    ),
                    300,
                ],
                "island2_extent": [round(island2_width), 300],
                "ground_gap": [
                    round(island2_width) + 100,
                    2 * (300 + 1 / 2 * sim_parameters["island_island_gap"] + 50),
                ],
                "ground_coupler_extend": coupler_height + sim_parameters["coupler_offset"] + 100,
                "coupler_extent": [100, coupler_height],
                "box": pya.DBox(
                    pya.DPoint(0, 0),
                    pya.DPoint(
                        round(island2_width) + 100 + 3000,
                    2 * (300 + 1 / 2 * sim_parameters["island_island_gap"] + 50) + 3000,
                    ),
                ),
                "name": f"{name}_coupler_width_{round(coupler_height)}",
            },
        )
    ]

# Create simulation
oas = export_simulation_oas(simulations, dir_path)

export_ansys(simulations, **export_parameters_ansys)

logging.info(f"Total simulations: {len(simulations)}")
open_with_klayout_or_default_application(oas)
