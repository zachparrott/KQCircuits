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

from kqcircuits.pya_resolver import pya
from kqcircuits.simulations.export.ansys.ansys_export import export_ansys
from kqcircuits.simulations.export.simulation_export import export_simulation_oas, sweep_simulation
from kqcircuits.simulations.simulation import Simulation
from kqcircuits.util.parameters import Param, pdt
from kqcircuits.simulations.port import EdgePort, InternalPort
from kqcircuits.chips.BP_Purcell import PurcellQubits
from kqcircuits.simulations.export.simulation_export import cross_sweep_simulation

from kqcircuits.util.export_helper import (
    create_or_empty_tmp_directory,
    get_active_or_new_layout,
    open_with_klayout_or_default_application,
)
from kqcircuits.util.parameters import add_parameters_from

# or should this be in sim_params?
@add_parameters_from(Simulation,
                     box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(7500, 7500)), 
                     ground_grid_box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(7500, 7500)))

class Bandpass(Simulation):
    
    launchers: bool
    launchers = Param(pdt.TypeBoolean, "True to include launchers in simulation", False)
    
    # Ability to re-define PurcellQubits parameters from defaults
    inputCapControl = Param(pdt.TypeDouble, "Input smooth capacitor finger control.", 2.1)
    outputCapControl = Param(pdt.TypeDouble, "Output smooth capacitor finger control.", 2.1)
    filter_length = Param(pdt.TypeDouble, "CPW t-line half wavelength for filter resonator.", 9076, unit="μm")      
    lengthIN = Param(pdt.TypeDouble, "Length compensation for input capacitance.", 751, unit="μm")
    lengthOUT = Param(pdt.TypeDouble, "Length compensation for output capacitance.", 1472, unit="μm")
    
    def build(self):
        
        # The following will remove the chip framing and launchers to put wave ports right at the small CPW dimensions
        
        chip = self.add_element(
            PurcellQubits,
            **{
                "filter_only": True,
                "a": 8,
                "b": 4,
                "inputCapControl": self.inputCapControl,
                "outputCapControl": self.outputCapControl,
                "filter_length": self.filter_length,
                "lengthIN": self.lengthIN,
                "lengthOUT": self.lengthOUT,
                "lockout_length": 4000,
                "center_length": 4700,                
            }
        )
        
        # Remove unneeded elements
        self.delete_instances(chip, "Chip Frame")
        
        # Insert chip and get refpoints
        _, refpoints = self.insert_cell(chip, rec_levels=None)

        if not self.launchers:
            # Remove launchers
            self.delete_instances(chip, "Launcher")

            # maximum_box = pya.DBox(pya.DPoint(700, 700), pya.DPoint(6800, 6800))
            maximum_box = pya.DBox(pya.DPoint(700, 3000), pya.DPoint(6800, 4500))
            port_shift = 0
        else:
            maximum_box = pya.DBox(pya.DPoint(150, 150), pya.DPoint(7500-150, 7500-150))
            # maximum_box = pya.DBox(pya.DPoint(150, 3000), pya.DPoint(7500-150, 4500))
            port_shift = 550

        # Limit the size of the box to fit the ports
        self.box &= maximum_box
                
        # Define edge ports, shifted inward by port_shift w.r.t. launcher refpoints
        for i, (launcher, shift) in enumerate(
            zip(
                ["E", "W"],
                [
                    [-port_shift, 0],
                    [port_shift, 0],
                ],
            )
        ):
            self.ports.append(EdgePort(i + 1, refpoints[f"{launcher}_port"] + pya.DVector(*shift)))


# Prepare output directory
dir_path = create_or_empty_tmp_directory(Path(__file__).stem + "_output")

# Simulation parameters
sim_class = Bandpass  # pylint: disable=invalid-name

sim_parameters = {
    "name": "port_sim",
    # "use_internal_ports": True,
    "launchers": False,
    # "use_ports": True,
    "face_stack": ["1t1",],  # chip distance default at 8um
    "substrate_material": ["sapphire"],
    "material_dict": "{'sapphire': {'permittivity': 10.5}}",
    # "a": 3.5,  # readout structure a in flip chip
    # "b": 32,  # readout structure b in flip chip    
    "inputCapControl": 6.39,
    "outputCapControl": 12.29,
    "lengthIN": 785.68,
    "lengthOUT": 1770.43,
}

export_parameters = {
    "path": dir_path,
    "max_delta_s": 0.01,
    "maximum_passes": 12,
    "frequency": 7.25,
    "sweep_start": 6,
    "sweep_end": 8.5,
    "sweep_count": 501,
    "exit_after_run": True,
    "skip_errors": False,
    "mesh_size": {"1t1_gap": 8},
}

# Get layout
logging.basicConfig(level=logging.WARN, stream=sys.stdout)
layout = get_active_or_new_layout()

# # Sweep simulations for variable geometry
simulations = cross_sweep_simulation(layout, sim_class, sim_parameters, {
    'filter_length': [8655]
})

# Fixed geometry simulation
# simulations = [sim_class(pya.Layout(), **sim_parameters)]

# Export Ansys files
export_ansys(simulations, **export_parameters)

# Write and open oas file
open_with_klayout_or_default_application(export_simulation_oas(simulations, dir_path))
