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

from kqcircuits.elements.meander import Meander
from kqcircuits.elements.meander_cavity import MeanderCavity

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

box_size_x = 2200
box_y = 1700

sim_class = get_single_element_sim_class(
    MeanderCavity,
    # transformation_from_center=lambda cell: pya.DTrans(0, False, -box_size_x / 2.0, -box_y / 2.0),
)

sim_parameters = {
    "name": "meander_eigenmode_sim",
    # "use_internal_ports": True,
        # "box": pya.DBox(
        #     pya.DPoint(-box_size_x / 2.0, box_y),
        #     pya.DPoint(box_size_x / 2.0, box_y),
        # ),
    "box": pya.DBox(pya.DPoint(0, 0), pya.DPoint(box_size_x, box_y)),
    "face_stack": [
        "1t1",
    ],  # chip distance default at 8um
    "substrate_material": ["sapphire"],
    "material_dict": "{'sapphire': {'permittivity': 10.5}}",
    "airbridge_height": 50,
    # "a": 8, 
    # "b": 4,
    # "r": 100,  
    "length": 8000,
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
    {"length": [9000, 8800, 8600, 8400, 8200, 8000, 7800, 7600, 7400, 7200, 7000, 6800, 6600, 6400, 6200, 6000]},
)
# Export Ansys files
export_ansys(simulations, **export_parameters)

# Write and open oas file
open_with_klayout_or_default_application(export_simulation_oas(simulations, dir_path))
