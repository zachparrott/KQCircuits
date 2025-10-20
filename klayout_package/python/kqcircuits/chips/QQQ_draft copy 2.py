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

from kqcircuits.qubits.qubit import Qubit
from kqcircuits.junctions.junction import Junction
from kqcircuits.junctions.overlap_junction import Overlap

@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(5100, 5100)))
# no flip chip alignment markers
@add_parameters_from(ChipFrame, marker_types=['','','',''])
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(5100, 5100))],
                     frames_dice_width=[50,50], name_brand='NIST', name_chip='QQQ', 
                     name_mask='', name_copy='')

# @add_parameters_from(Junction, "junction_type")
# @add_parameters_from(Junction, "junction_type")
@add_parameters_from(Overlap)

class ChipQQQOld(Chip):
    """C ."""
    
    # junction positions from Ansys
    jj_pos_A = (98.023702, -22.519238)
    jj_pos_B = (-93.971143, -7.8589838)
    jj_pos_C = (0, -45.0)
    jj_pos_SL = (-5, 225)
    jj_pos_SR = (35, 225)
    small_jj_gap = 35
    
    def produce_junctions(self):
        junction_cell = self.add_element(Overlap, pad_to_pad_separation = self.small_jj_gap)
        # junction_cell = self.add_element(Junction, junction_type="Overlap", pad_to_pad_separation=50)
        
        self.insert_cell(junction_cell, pya.DTrans(0, False, 2550 + self.jj_pos_A[0], 2550 + self.jj_pos_A[1]), "jj_A")
        self.insert_cell(junction_cell, pya.DTrans(0, False, 2550 + self.jj_pos_B[0], 2550 + self.jj_pos_B[1]), "jj_B")
        self.insert_cell(junction_cell, pya.DTrans(0, False, 2550 + self.jj_pos_C[0], 2550 + self.jj_pos_C[1]), "jj_C")


    def produce_squid(self):
        junction_cell = self.add_element(Overlap, 
                                         pad_to_pad_separation = 10.0, finger_width = 1,
                                         hook_thickness = 0.265, hook_width = 3,
                                         )

        self.insert_cell(junction_cell, pya.DTrans(0, False, 2550 + self.jj_pos_SL[0], 2550 + self.jj_pos_SL[1]), "jj_SL")
        self.insert_cell(junction_cell, pya.DTrans(0, False, 2550 + self.jj_pos_SR[0], 2550 + self.jj_pos_SR[1]), "jj_SL")


    def build(self):
        # self.produce_two_launchers(self.a_launcher, self.b_launcher, self.launcher_width, self.taper_length, self.launcher_frame_gap)

        # load OAS
        qubit_cell = self.layout.create_cell("QQQ_v5_5_2", Qubit.LIBRARY_NAME)
        self.insert_cell(qubit_cell, pya.DTrans(0, False, 2550, 2550), "QQQ")

        self.produce_squid()
        self.produce_junctions()
