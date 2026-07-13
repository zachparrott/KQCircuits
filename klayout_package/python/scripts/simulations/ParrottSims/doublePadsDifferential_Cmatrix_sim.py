# This code is part of KQCircuits
# Copyright (C) 2026 Zachary Parrott
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

import logging
import sys
from pathlib import Path

import numpy as np

from kqcircuits.pya_resolver import pya

from kqcircuits.qubits.double_pads_diff import DoublePadsDifferential
from kqcircuits.simulations.post_process import PostProcess

from kqcircuits.simulations.single_element_simulation import (
    get_single_element_sim_class,
)
from kqcircuits.simulations.export.ansys.ansys_export import export_ansys
from kqcircuits.simulations.export.simulation_export import export_simulation_oas
from kqcircuits.util.export_helper import (
    create_or_empty_tmp_directory,
    get_active_or_new_layout,
    open_with_klayout_or_default_application,
)
from decimal import getcontext

# Prepare output directory
dir_path = create_or_empty_tmp_directory(Path(__file__).stem + "_output")

sim_class = get_single_element_sim_class(DoublePadsDifferential)  # pylint: disable=invalid-name

# Simulation parameters
sim_parameters = {
    "name": "pads_cmatrix",
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
    "coupler_offset": 30,
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

# Here our simulation is in Q3D and running the matrix table post process script
export_parameters = {
    "path": dir_path,
    "ansys_tool": "q3d",
    "post_process": [
        PostProcess(script)
        for script in ["produce_cmatrix_table.py", "effective_grounded_transmon.py"]
    ],
    "exit_after_run": True,
    "percent_error": 0.1,
    "minimum_converged_passes": 2,
    "frequency": 4,  # GHz
    "frequency_units": "GHz",
    "maximum_passes": 20,
    # may fix ground on pad issue. Setting to true will float the other side of the junction. Instead set floating=True in JunctionSimPort
    # "use_floating_islands": False,
}

# Get layout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
layout = get_active_or_new_layout()

# Cross sweep number of fingers and finger length
simulations = []

getcontext().prec = 6  # Set precision


island2_widths = np.linspace(700, 900, 3, dtype=float).tolist()

# second group
# pad_width = np.arange(1000 + pad_width[1] - pad_width[0], 1500, pad_width[1] - pad_width[0])

# coupler_heights = np.linspace(400, 1180, 5, dtype=float).tolist()
coupler_heights = [900, 1000]

# coupler_widths = np.arange(300 + coupler_widths[1] - coupler_widths[0], 700, coupler_widths[1] - coupler_widths[0])

# for extent in island_extent:
# 2x sweep
# for island2_width in island2_widths:
#     name = sim_parameters["name"]
#     name = f"{name}_pad_width_{int(island2_width)}"
#     simulations += [
#         sim_class(
#             layout,
#             **{
#                 **sim_parameters,
#                 "island1_extent": [
#                     max(
#                         island2_width - 400,
#                         80  # coupler width
#                         + 2 * sim_parameters["coupler_offset"]
#                         + 4 * sim_parameters["island1_r"],
#                     ),
#                     300,
#                 ],
#                 "island2_extent": [round(island2_width), 300],
#                 "ground_gap": [
#                     round(island2_width) + 100,
#                     2 * (300 + 1 / 2 * sim_parameters["island_island_gap"] + 50),
#                 ],
#                 "ground_coupler_extend": coupler_height + sim_parameters["coupler_offset"] + 100,
#                 "coupler_extent": [80, coupler_height],
#                 "box": pya.DBox(
#                     pya.DPoint(0, 0),
#                     pya.DPoint(
#                         round(island2_width) + 100 + 2000,
#                     2 * (300 + 1 / 2 * sim_parameters["island_island_gap"] + 50 + coupler_height) + 2000,
#                     ),
#                 ),
#                 "name": f"{name}_coupler_height_{round(coupler_height)}",
#             },
#         )
#         for coupler_height in coupler_heights
#     ]
# verification of pairs , og dimension
# coupler_heights = [506.0, 603.9, 720.3, 856.4]
# island2_widths = [734.9, 755.0, 769.8, 787.3]

# after 34 fF average cap to ground of resonator correction
coupler_heights = [522.0, 630.0, 758.4, 913.7]
island2_widths = [735.5, 750.4, 765.8, 784.0]

for island2_width, coupler_height in zip(island2_widths, coupler_heights):
    name = sim_parameters["name"]
    name = f"{name}_pw_{int(island2_width)}"
    simulations += [
        sim_class(
            layout,
            **{
                **sim_parameters,
                "island1_extent": [
                    max(
                        island2_width - 400,
                        80  # coupler width
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
                "ground_coupler_extend": coupler_height
                + sim_parameters["coupler_offset"]
                + 100,
                "coupler_extent": [80, coupler_height],
                "box": pya.DBox(
                    pya.DPoint(0, 0),
                    pya.DPoint(
                        round(island2_width) + 100 + 2000,
                        2
                        * (
                            300
                            + 1 / 2 * sim_parameters["island_island_gap"]
                            + 50
                            + coupler_height
                        )
                        + 2000,
                    ),
                ),
                "name": f"{name}_ch_{round(coupler_height)}",
            },
        )
    ]

# Export Ansys files
export_ansys(simulations, **export_parameters)

# Write and open oas file
open_with_klayout_or_default_application(export_simulation_oas(simulations, dir_path))
