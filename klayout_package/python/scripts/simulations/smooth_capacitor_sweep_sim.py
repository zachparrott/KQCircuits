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

import logging
import sys
from pathlib import Path

import numpy as np

from kqcircuits.pya_resolver import pya
from kqcircuits.elements.smooth_capacitor import SmoothCapacitor
from kqcircuits.simulations.post_process import PostProcess
from kqcircuits.simulations.single_element_simulation import get_single_element_sim_class
from kqcircuits.simulations.export.ansys.ansys_export import export_ansys
from kqcircuits.simulations.export.simulation_export import cross_sweep_simulation, export_simulation_oas
from kqcircuits.util.export_helper import (
    create_or_empty_tmp_directory,
    get_active_or_new_layout,
    open_with_klayout_or_default_application,
)

# Prepare output directory
dir_path = create_or_empty_tmp_directory(Path(__file__).stem + "_output")

sim_class = get_single_element_sim_class(SmoothCapacitor)  # pylint: disable=invalid-name

# Simulation parameters
sim_parameters = {
    "name": "smooth_capacitor",
    "use_internal_ports": True,
    "use_ports": True,
    "box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(1000, 1000)),
    "port_size": 200,
    "face_stack": ["1t1"],
    # "corner_r": 2,
    "chip_distance": 8,
    # "ground_gap": 20,
    # "fixed_length": 0,
    # "r_inner": 75,
    # "r_outer": 120,
    # "swept_angle": 180,
    # "outer_island_width": 40,
    "a": 10,
    "b": 4.6,
    "finger_width": 10,
    "finger_gap": 4.6,
    "finger_control": 2.1,
}

# Here our simulation is in Q3D and runnign the matrix table post process script
export_parameters = {
    "path": dir_path,
    "ansys_tool": "q3d",
    "post_process": PostProcess("produce_cmatrix_table.py"),
    "exit_after_run": True,
    "percent_error": 0.3,
    "minimum_converged_passes": 2,
    "maximum_passes": 20,
}

# Get layout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
layout = get_active_or_new_layout()

# Cross sweep number of fingers and finger length
simulations = []


# simulations for getting the ballpark
simulations += cross_sweep_simulation(layout, sim_class, sim_parameters, {
    'finger_control': np.linspace(1.0, 8.0, 12, dtype=float).tolist(),
})

# Export Ansys files
export_ansys(simulations, **export_parameters)

# Write and open oas file
open_with_klayout_or_default_application(export_simulation_oas(simulations, dir_path))
