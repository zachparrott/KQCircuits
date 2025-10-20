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
from kqcircuits.junctions.overlap_junction import Overlap
from kqcircuits.junctions.overlap_array import OverlapArray
from kqcircuits.test_structures.junction_test_pads.junction_test_pads_simple import JunctionTestPadsSimple

@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200)),
                    marker_types=['','','',''],
                    chip_dicing_width=50,
                    chip_dicing_in_base_metal=True,
                    )
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200))],
                     frames_dice_width=[150,150], name_brand='QCCD', name_chip='QCCD', 
                     name_mask='', name_copy='')

class ChipQCCD(Chip):
    """C ."""
    # parameters to pass to junctions
    # small junctions
    Q_finger_width = Param(pdt.TypeDouble, "Width of the finger.", 0.100, unit="μm")
    Q_bridge_gap = Param(pdt.TypeDouble, "Gap between finger and hook.", 0.10, unit="μm")
    Q_hook_thickness = Param(pdt.TypeDouble, "Thickness of hook on catch.", 0.196, unit="μm")

    # SQUID junctions
    S_finger_width = Param(pdt.TypeDouble, "Width of the finger.", 1.496, unit="μm")
    S_bridge_gap = Param(pdt.TypeDouble, "Gap between finger and hook.", 0.15, unit="μm")
    S_hook_thickness = Param(pdt.TypeDouble, "Thickness of hook on catch.", 0.200, unit="μm")    

    # Array junctions
    A_bridge_gap = Param(pdt.TypeDouble, "Bridge width.", 0.158, unit="μm")
    A_gap_spacing = Param(pdt.TypeDouble, "Spacing between gaps.", 0.644+0.158, unit="μm")
    A_bridge_length = Param(pdt.TypeDouble, "Bridge length.", 1.75, unit="μm")
    A_junction_number = Param(pdt.TypeInt, "Number of junctions.", 105)

    # junction positions from Ansys
    jA_pos_A = (77, 158.6035) 
    jA_pos_B = (-77, 158.6035)
    
    jj_pos_C = (0, -45.0)
    jj_pos_SL = (-5, 225)
    jj_pos_SR = (35, 225)
    small_jj_gap = 20
    
    jj_pos_Qtest = (640, 4260)
    jj_pos_Stest = (4220, 4260)
    jj_pos_Atest = (680, 1320)

    def produce_junctions(self, **kwargs):
        junction_cell = self.add_element(Overlap, pad_to_pad_separation = self.small_jj_gap, **kwargs)
        # test_cell = self.add_element(Overlap, junction_height=40, pad_to_pad_separation=5, **kwargs)
        self.insert_cell(junction_cell, pya.DTrans(0, False, 2600 + self.jj_pos_C[0], 2600 + self.jj_pos_C[1]), "jj_C")

        # self.insert_cell(test_cell, pya.DTrans(0, False, self.jj_pos_Qtest[0], self.jj_pos_Qtest[1]), "jj_T")
        # self.insert_cell(test_cell, pya.DTrans(0, False, self.jj_pos_Qtest[0] + 240, self.jj_pos_Qtest[1]), "jj_T")

        self.insert_cell(junction_cell, pya.DTrans(0, False, self.jj_pos_Qtest[0], self.jj_pos_Qtest[1]), "jj_T")
        self.insert_cell(junction_cell, pya.DTrans(0, False, self.jj_pos_Qtest[0] + 240, self.jj_pos_Qtest[1]), "jj_T")

    def produce_array(self, **kwargs):
        array_cell = self.add_element(OverlapArray, pad_to_pad_separation = 82.793, **kwargs)
        test_cell = self.add_element(OverlapArray, pad_to_pad_separation = 80, **kwargs)

        self.insert_cell(array_cell, pya.DTrans(0, False, 2600 + self.jA_pos_A[0] - 3, 2600 + self.jA_pos_A[1]), "array_A1")
        self.insert_cell(array_cell, pya.DTrans(0, False, 2600 + self.jA_pos_A[0], 2600 + self.jA_pos_A[1]), "array_A2")

        self.insert_cell(array_cell, pya.DTrans(0, False, 2600 + self.jA_pos_B[0], 2600 + self.jA_pos_B[1]), "array_B1")
        self.insert_cell(array_cell, pya.DTrans(0, False, 2600 + self.jA_pos_B[0] + 3, 2600 + self.jA_pos_B[1]), "array_B2")

        self.insert_cell(test_cell, pya.DTrans(0, False, self.jj_pos_Atest[0], self.jj_pos_Atest[1]), "array_T") 
        self.insert_cell(test_cell, pya.DTrans(0, False, self.jj_pos_Atest[0] + 280, self.jj_pos_Atest[1]), "array_T")

    def produce_squid(self, **kwargs):
        junction_cell = self.add_element(Overlap, pad_to_pad_separation = 10.0, hook_width = 3, **kwargs)

        self.insert_cell(junction_cell, pya.DTrans(0, False, 2600 + self.jj_pos_SL[0], 2600 + self.jj_pos_SL[1]), "jj_SL")
        self.insert_cell(junction_cell, pya.DTrans(0, False, 2600 + self.jj_pos_SR[0], 2600 + self.jj_pos_SR[1]), "jj_SR")

        test_cell = self.add_element(Overlap, junction_height=40,
                                         pad_to_pad_separation = 10.0, hook_width = 3, **kwargs)

        self.insert_cell(test_cell, pya.DTrans(0, False, self.jj_pos_Stest[0], self.jj_pos_Stest[1]), "jj_ST")
        self.insert_cell(test_cell, pya.DTrans(0, False, self.jj_pos_Stest[0] + 240, self.jj_pos_Stest[1]), "jj_ST")

    def produce_jj_labels(self, pos1, pos2, pos3):
        # attempt at labelling test pads
        label1 = f"{self.Q_finger_width*1e3:.0f} x {self.Q_hook_thickness*1e3:.0f} nm"
        label2 = f"{self.S_finger_width*1e3:.0f} x {self.S_hook_thickness*1e3:.0f} nm"
        label3 = f"N={self.A_junction_number} {self.A_bridge_length*1e3:.0f} x {self.A_gap_spacing*1e3:.0f} nm"

        produce_label(self.cell, label1, pya.DPoint(pos1[0], pos1[1] - 50), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
        produce_label(self.cell, "Qubit JJ", pya.DPoint(pos1[0], pos1[1] - 125), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
        
        produce_label(self.cell, label2, pya.DPoint(pos2[0], pos2[1] - 50), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
        produce_label(self.cell, "SQUID JJ", pya.DPoint(pos2[0], pos2[1] - 125), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
        
        produce_label(self.cell, label3, pya.DPoint(pos3[0], pos3[1] - 50), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
        produce_label(self.cell, "JJ Array", pya.DPoint(pos3[0], pos3[1] - 125), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)

    def build(self):
        squid_params = {
            "finger_width": self.S_finger_width,
            "bridge_gap": self.S_bridge_gap,
            "hook_thickness": self.S_hook_thickness,
            "hook_undercut": 0.5
        }

        small_params = {
            "finger_width": self.Q_finger_width,
            "bridge_gap": self.Q_bridge_gap,
            "hook_thickness": self.Q_hook_thickness,
            "hook_undercut": 0.5
        }
        
        array_params = {
            "bridge_gap": self.A_bridge_gap,
            "gap_spacing": self.A_gap_spacing,
            "bridge_length": self.A_bridge_length,
            "junction_number": self.A_junction_number,
        }

        # load OAS
        qubit_cell = self.layout.create_cell("QCC_v10_7_2", Qubit.LIBRARY_NAME)
        self.insert_cell(qubit_cell, pya.DTrans(0, False, 2600, 2600), "QCC")

        testpad1 = self.add_element(JunctionTestPadsSimple, pad_width=200, area_height=520, area_width=520, pad_spacing=40, only_pads=True)
        self.insert_cell(testpad1, pya.DTrans(0, False, 500, 4000), "JJ_test")
        self.insert_cell(testpad1, pya.DTrans(0, False, 4080, 4000), "S_test")

        testpad3 = self.add_element(JunctionTestPadsSimple, pad_width=200, area_height=640, area_width=640, pad_spacing=80, only_pads=True)
        self.insert_cell(testpad3, pya.DTrans(0, False, 500, 1000), "A_test")

        self.produce_squid(**squid_params)
        self.produce_junctions(**small_params)

        self.produce_array(**array_params)

        self.produce_jj_labels((500, 4000), (4080, 4000), (500, 1000))
