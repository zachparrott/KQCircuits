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
from kqcircuits.simulations.export.simulation_export import (
    export_simulation_oas,
    sweep_simulation,
)
from kqcircuits.simulations.simulation import Simulation
from kqcircuits.util.parameters import Param, pdt
from kqcircuits.simulations.port import EdgePort

# from kqcircuits.chips.BP_Purcell import PurcellQubits
from kqcircuits.chips.BP_Purcelldiff import PurcellQubits2

from kqcircuits.elements.waveguide_coplanar import WaveguideCoplanar

from kqcircuits.simulations.export.simulation_export import cross_sweep_simulation

from kqcircuits.util.export_helper import (
    create_or_empty_tmp_directory,
    get_active_or_new_layout,
    open_with_klayout_or_default_application,
)
from kqcircuits.util.parameters import add_parameters_from


# or should this be in sim_params?
@add_parameters_from(
    Simulation,
    box=pya.DBox(pya.DPoint(0, 0), pya.DPoint(7500, 7500)),
    ground_grid_box=pya.DBox(pya.DPoint(0, 0), pya.DPoint(7500, 7500)),
)
class Bandpass(Simulation):
    launchers: bool
    launchers = Param(pdt.TypeBoolean, "True to include launchers in simulation", False)

    qubits = Param(pdt.TypeBoolean, "True to include qubits in simulation", True)

    # Ability to re-define PurcellQubits parameters from defaults
    inputCapControl = Param(
        pdt.TypeDouble, "Input smooth capacitor finger control.", 2.1
    )
    outputCapControl = Param(
        pdt.TypeDouble, "Output smooth capacitor finger control.", 2.1
    )
    filter_length = Param(
        pdt.TypeDouble,
        "CPW t-line half wavelength for filter resonator.",
        9076,
        unit="μm",
    )
    lengthIN = Param(
        pdt.TypeDouble, "Length compensation for input capacitance.", 751, unit="μm"
    )
    lengthOUT = Param(
        pdt.TypeDouble, "Length compensation for output capacitance.", 1472, unit="μm"
    )

    filter_positions = Param(
        pdt.TypeList,
        "Fractional position of resonators along the bandpass resonator length.",
        [0.3, 0.433, 0.566, 0.7],
    )
    resonator_lengths = Param(
        pdt.TypeList, "Readout resonators length in um.", [9000, 9000, 9000, 9000]
    )
    resonator_couplings = Param(
        pdt.TypeList, "Readout coupling length in um.", [100, 100, 100, 100]
    )
    balance_correction = Param(
        pdt.TypeList,
        "Balance correction factor for resonator coupling roll.",
        [1.0, 1.0, 1.0, 1.0],
    )

    def build(self):

        # The following will remove the chip framing and launchers to put wave ports right at the small CPW dimensions

        chip = self.add_element(
            # PurcellResonators,
            PurcellQubits2,
            **{
                "filter_only": False,
                "a": 8,
                "b": 4,
                "inputCapControl": self.inputCapControl,
                "outputCapControl": self.outputCapControl,
                "filter_length": self.filter_length,
                "filter_positions": self.filter_positions,
                "resonator_lengths": self.resonator_lengths,
                "resonator_couplings": self.resonator_couplings,
                "lengthIN": self.lengthIN,
                "lengthOUT": self.lengthOUT,
                "lockout_length": 4200,
                "center_length": 4700,
                "qubit_loading": [0, 0, 0, 0],
                "balance_correction": self.balance_correction,
            },
        )

        # Remove unneeded elements
        self.delete_instances(chip, "Chip Frame")
        self.delete_instances(chip, "Launcher")

        # Insert chip and get refpoints
        _, refpoints = self.insert_cell(chip, rec_levels=None)

        maximum_box = pya.DBox(pya.DPoint(1000, 4400), pya.DPoint(5700, 7400))

        if not self.qubits:
            # remove the qubits
            suffices = ["$2"]

            for suffix in suffices:
                self.delete_instances(chip, f"Double Pads Differential{suffix}")

            for i in range(14):
                self.delete_instances(chip, f"Waveguide Composite${i}")
                self.delete_instances(chip, f"Waveguide Coplanar$3{i}")
            self.delete_instances(chip, "Hanger Resonator")
            self.delete_instances(chip, "Smooth Capacitor")
            self.delete_instances(chip, "Smooth Capacitor$1")
            self.delete_instances(chip, "Waveguide Coplanar$31")
            self.delete_instances(chip, "Waveguide Coplanar$32")
            self.delete_instances(chip, "Waveguide Coplanar$30")

            self.delete_instances(chip, "Waveguide Composite")
            self.delete_instances(chip, "Waveguide Coplanar$3")
            self.delete_instances(chip, "Waveguide Composite$14")

        # Limit the size of the box to fit the ports
        self.box &= maximum_box


# Prepare output directory
dir_path = create_or_empty_tmp_directory(Path(__file__).stem + "_output")

# Simulation parameters
sim_class = Bandpass  # pylint: disable=invalid-name

sim_parameters = {
    "name": "resfilter_U0_D0_sim",
    "use_internal_ports": True,
    "launchers": False,
    "qubits": False,
    "use_ports": True,
    "face_stack": [
        "1t1",
    ],  # chip distance default at 8um
    "substrate_material": ["sapphire"],
    "material_dict": "{'sapphire': {'permittivity': 10.5}}",
    "airbridge_height": 50,
    "inputCapControl": 6.39,
    "outputCapControl": 12.29,
    "lengthIN": 785.68,
    "lengthOUT": 1770.43,
    "filter_length": 8655,
    "filter_positions": [0.35, 0.45, 0.55],
    "resonator_couplings": [340, 340, 340],
}

export_parameters = {
    "path": dir_path,
    "ansys_tool": "q3d",
    "percent_error": 0.1,
    "minimum_converged_passes": 2,
    "frequency": 4,  # GHz
    "frequency_units": "GHz",
    "maximum_passes": 20,
    "exit_after_run": True,
    "skip_errors": False,
    # "mesh_size": {"1t1_gap": 8},
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
        "resonator_lengths": [[8670, 8700, 8700]],  # , [8770]],
        # "filter_positions": [[0.35], [0.5], [0.65]],
        # "balance_correction": [[1.0], [0.95], [1.05], [0.9], [1.1]],
    },
)

# Fixed geometry simulation
# simulations = [sim_class(pya.Layout(), **sim_parameters)]

# Export Ansys files
export_ansys(simulations, **export_parameters)

# Write and open oas file
open_with_klayout_or_default_application(export_simulation_oas(simulations, dir_path))
