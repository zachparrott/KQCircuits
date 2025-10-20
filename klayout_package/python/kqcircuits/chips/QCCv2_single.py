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
from kqcircuits.test_structures.profilometer import Profilometer
from kqcircuits.util.label import produce_label, LabelOrigin

from kqcircuits.qubits.qubit import Qubit
# from kqcircuits.junctions.junction import Junction
from kqcircuits.junctions.overlap_junction2 import Overlap2
from kqcircuits.junctions.overlap_array import OverlapArray
from kqcircuits.junctions.overlap_junction_simple import OverlapSimple

from kqcircuits.test_structures.junction_test_pads.junction_test_pads_simple import JunctionTestPadsSimple
from kqcircuits.test_structures.test_structure import TestStructure
from kqcircuits.elements.element import Element
from kqcircuits.util.library_helper import load_libraries

@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200)),
                    marker_types=["Marker Dummy"]*4,
                    chip_dicing_width=50,
                    chip_dicing_in_base_metal=True,
                    )
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200))],
                     frames_dice_width=[200,200], frames_marker_dist = [250,250],
                     name_brand='QCCS', name_chip='QCCS', 
                     name_mask='tt', name_copy='')

# @add_parameters_from(Junction, "junction_type")
# @add_parameters_from(Junction, "junction_type")


class ChipQCCv2Single(Chip):
    """C ."""
    # parameters to pass to junctions
    # small junctions
    Q_finger_width = Param(pdt.TypeDouble, "Width of the finger.", 0.136, unit="μm")
    Q_bridge_gap = Param(pdt.TypeDouble, "Gap between finger and hook.", 0.15, unit="μm")
    Q_hook_thickness = Param(pdt.TypeDouble, "Thickness of hook on catch.", 0.100, unit="μm")

    # SQUID junctions
    S_finger_width = Param(pdt.TypeDouble, "Width of the finger.", 1.496, unit="μm")
    S_bridge_gap = Param(pdt.TypeDouble, "Gap between finger and hook.", 0.15, unit="μm")
    S_hook_thickness = Param(pdt.TypeDouble, "Thickness of hook on catch.", 0.200, unit="μm")    

    # Array junctions
    A_bridge_gap = Param(pdt.TypeDouble, "Bridge width.", 0.158, unit="μm")
    A_gap_spacing = Param(pdt.TypeDouble, "Spacing between gaps.", 0.644+0.158, unit="μm")
    A_bridge_length = Param(pdt.TypeDouble, "Bridge length.", 3.5, unit="μm")
    A_junction_number = Param(pdt.TypeInt, "Number of junctions.", 53)

    # junction positions from Ansys
    jA_pos_A = (75, 158.6035 + 6) 
    jA_pos_B = (-75, 158.6035 + 6)
    
    jj_pos_C = (0, -45.0)
    jj_pos_SL = (-10, 230)
    jj_pos_SR = (10, 230)
    small_jj_gap = 10

        
    def produce_junctions(self, penguin, **kwargs):
        junction_cell = self.add_element(Overlap2, pad_to_pad_separation = self.small_jj_gap, **kwargs)
        
        short_params = kwargs
        short_params['bridge_gap'] = 0.0
        short_cell = self.add_element(Overlap2, pad_to_pad_separation = self.small_jj_gap, **short_params)

        self.insert_cell(junction_cell, pya.DTrans(0, False, 2600 + self.jj_pos_C[0], 2600 + self.jj_pos_C[1]), "jj_C")

        for i, trans in enumerate(penguin):
            if i == 0:
                self.insert_cell(junction_cell, trans * pya.DTrans(0, False, self.jj_pos_C[0], self.jj_pos_C[1]), "jj_Ct")
            # else:
            #     self.insert_cell(short_cell, trans * pya.DTrans(0, False, self.jj_pos_C[0], self.jj_pos_C[1]), "jj_C")


    def produce_array(self, penguin, **kwargs):
        array_cell = self.add_element(OverlapArray, pad_to_pad_separation = 70.792, **kwargs)
        
        short_params = kwargs
        short_params['bridge_gap'] = 0.0 
        short_cell = self.add_element(OverlapArray, pad_to_pad_separation = 70.792, **short_params)

        self.insert_cell(array_cell, pya.DTrans(0, False, 2600 + self.jA_pos_A[0], 2600 + self.jA_pos_A[1]), "array_A")
        self.insert_cell(array_cell, pya.DTrans(0, False, 2600 + self.jA_pos_B[0], 2600 + self.jA_pos_B[1]), "array_B")

        for i, trans in enumerate(penguin):
            if i == 0:
                self.insert_cell(array_cell, trans * pya.DTrans(0, False, self.jA_pos_A[0], self.jA_pos_A[1]), "array_At")
                self.insert_cell(array_cell, trans * pya.DTrans(0, False, self.jA_pos_B[0], self.jA_pos_B[1]), "array_Bt")
            # else:
            #     self.insert_cell(short_cell, trans * pya.DTrans(0, False, self.jA_pos_A[0], self.jA_pos_A[1]), "array_A")
            #     self.insert_cell(short_cell, trans * pya.DTrans(0, False, self.jA_pos_B[0], self.jA_pos_B[1]), "array_B")



    def produce_squid(self, penguin, **kwargs):
        junction_cell = self.add_element(OverlapSimple, pad_to_pad_separation = 8.0, hook_width = 3, **kwargs)

        self.insert_cell(junction_cell, pya.DTrans(0, False, 2600 + self.jj_pos_SL[0], 2600 + self.jj_pos_SL[1]), "jj_SL")
        self.insert_cell(junction_cell, pya.DTrans(0, False, 2600 + self.jj_pos_SR[0], 2600 + self.jj_pos_SR[1]), "jj_SR")


        

    def produce_jj_labels(self, pos1, pos2):
        # attempt at labelling test pads
        label1 = f"{self.Q_finger_width*1e3:.0f} x {self.Q_hook_thickness*1e3:.0f} nm"
        label2 = f"{self.A_bridge_length*1e3:.0f} nm x {self.A_junction_number}"

        produce_label(self.cell, label1, pya.DPoint(pos1[0] + 700, pos1[1] - 50), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
        
        produce_label(self.cell, label2, pya.DPoint(pos2[0] + 700, pos2[1] - 50), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
        
        # produce_label(self.cell, "short", pya.DPoint(pos1[0] + 700, pos1[1] - 50), LabelOrigin.TOPLEFT, 0, 0, 
        #               [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
        


    def build(self):
        # self.produce_two_launchers(self.a_launcher, self.b_launcher, self.launcher_width, self.taper_length, self.launcher_frame_gap)
        squid_params = {"finger_width": self.S_finger_width,
                    "bridge_gap": self.S_bridge_gap,
                    "hook_thickness": self.S_hook_thickness,
                    "hook_undercut": 0.5}

        small_params = {"finger_width": self.Q_finger_width,
                    "bridge_gap": self.Q_bridge_gap,
                    "hook_thickness": self.Q_hook_thickness,
                    "hook_lead_thickness": 0.2,
                    "hook_undercut": 0.5,
                    "noSQUID": True}
        
        array_params = {
            "bridge_gap": self.A_bridge_gap,
            "gap_spacing": self.A_gap_spacing,
            "bridge_length": self.A_bridge_length,
            "junction_number": self.A_junction_number,
        }

        # load OAS
        load_libraries(path=Qubit.LIBRARY_PATH)
        load_libraries(path=TestStructure.LIBRARY_PATH)
        load_libraries(path=Element.LIBRARY_PATH)

        qubit_cell = self.layout.create_cell("QCCv2", Qubit.LIBRARY_NAME)
        self.insert_cell(qubit_cell, pya.DTrans(0, False, 2600, 2600), "QCCv2")

        penguin = self.layout.create_cell("QCCv2", TestStructure.LIBRARY_NAME)
        penguin_translations = [pya.DTrans(0, False, 4400 - i*650, 4150) for i in range(2)]

        for i, trans in enumerate(penguin_translations):
            if i == 0:
                self.insert_cell(penguin, trans)

        # testpad1 = self.add_element(JunctionTestPadsSimple, pad_width=200, area_height=520, area_width=1000, pad_spacing=40, only_pads=True)
        # self.insert_cell(testpad1, pya.DTrans(0, False, 500, 4000), "JJ_test")
        # testpad2 = self.add_element(JunctionTestPadsSimple, pad_width=200, area_height=520, area_width=520, pad_spacing=40, only_pads=True)
        # self.insert_cell(testpad2, pya.DTrans(0, False, 4080, 4000), "S_test")

        self.produce_squid(penguin_translations, **squid_params)
        self.produce_junctions(penguin_translations, **small_params)
        self.produce_array(penguin_translations, **array_params)

        self.produce_jj_labels((3575, 3975), (3575, 3900))

        resolution = self.layout.create_cell("ResolutionTestStructure_NB", TestStructure.LIBRARY_NAME)
        self.insert_cell(resolution, pya.DTrans(0, False, 670, 4200-100), "res")
        
        # self.insert_cell(Profilometer, pya.DTrans(0, False, 670-112.5, 4075-100), "pro")

        NISTlogo = self.layout.create_cell("NISTlogo", Element.LIBRARY_NAME)
        
        # measured from crap GDS logo file
        scaleFactor = 40 / 158.016
        self.insert_cell(NISTlogo, pya.DCplxTrans(scaleFactor, 0, False, 650, 4400), "logo")

        produce_label(self.cell, "Z.Parrott", pya.DPoint(325, 4275), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
