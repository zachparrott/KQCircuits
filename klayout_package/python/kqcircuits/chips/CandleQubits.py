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


from kqcircuits.chips.chip import Chip
from kqcircuits.pya_resolver import pya
from kqcircuits.elements.chip_frame import ChipFrame
from kqcircuits.util.parameters import Param, pdt, add_parameters_from, add_parameter

from kqcircuits.util.label import produce_label, LabelOrigin

from kqcircuits.qubits.qubit import Qubit
# from kqcircuits.junctions.junction import Junction
from kqcircuits.junctions.overlap_junction2 import Overlap2
from kqcircuits.junctions.overlap_junction_simple import OverlapSimple

from kqcircuits.test_structures.junction_test_pads.junction_test_pads_simple import JunctionTestPadsSimple

@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200)),
                    marker_types=['','','',''],
                    chip_dicing_width=50,
                    chip_dicing_in_base_metal=True,
                    )
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200))],
                     frames_dice_width=[150,150], name_brand='MIT', name_chip='Candle', 
                     name_mask='', name_copy='')

# @add_parameters_from(Junction, "junction_type")
# @add_parameters_from(Junction, "junction_type")


class CandleQubits(Chip):
    """C ."""
    # parameters to pass to junctions
    # small junctions
    Q_finger_width = Param(pdt.TypeDouble, "Width of the finger.", 0.136, unit="μm")
    Q_bridge_gap = Param(pdt.TypeDouble, "Gap between finger and hook.", 0.15, unit="μm")
    Q_hook_thickness = Param(pdt.TypeDouble, "Thickness of hook on catch.", 0.100, unit="μm")

    # junction positions from Ansys
    jj_pos_A = (-1762.5, 1800)
    jj_pos_B = (-1762.5+1450, 1800)
    jj_pos_C = (-1762.5+2*1450, 1800)
    top_pos = [pya.DPoint(-1762.5 + i*1450 + 2600, 1800 + 2600) for i in range(3)]
    bot_pos = [pya.DPoint(-1136.5 + i*1450 + 2600, -1800 + 2600) for i in range(3)]
    small_jj_gap = 30


    
    def produce_junctions(self, **kwargs):
        junction_cell = self.add_element(Overlap2, pad_to_pad_separation = self.small_jj_gap, **kwargs)
        # test_cell = self.add_element(Overlap, junction_height=40, pad_to_pad_separation=5, **kwargs)
        
        for i in range(3):
            self.insert_cell(junction_cell, pya.DTrans(0, False, self.bot_pos[i]), f"jj_b{i}")
            self.insert_cell(junction_cell, pya.DTrans(0, False, self.top_pos[i]), f"jj_t{i}")
        

    def build(self):
        # self.produce_two_launchers(self.a_launcher, self.b_launcher, self.launcher_width, self.taper_length, self.launcher_frame_gap)
  
        small_params = {"finger_width": self.Q_finger_width,
                    "bridge_gap": self.Q_bridge_gap,
                    "hook_thickness": self.Q_hook_thickness,
                    "hook_undercut": 0.5,
                    "noSQUID": True}

        # load OAS
        qubit_cell = self.layout.create_cell("CANDLE_QBIT", Qubit.LIBRARY_NAME)
        self.insert_cell(qubit_cell, pya.DTrans(1, False, 2600, 2600), "Candles")

        
        self.produce_junctions(**small_params)
