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

from kqcircuits.test_structures.test_structure import TestStructure
from kqcircuits.test_structures.profilometer import Profilometer

from kqcircuits.util.label import produce_label, LabelOrigin
from kqcircuits.junctions.overlap_junction2 import Overlap2
from kqcircuits.junctions.overlap_array import OverlapArray
from kqcircuits.util.library_helper import load_libraries

@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200)),
                      marker_types=["Marker Dummy"]*4,
                      chip_dicing_width=50,
                      chip_dicing_in_base_metal=True,
                      )
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200))],
                     frames_dice_width=[200,200], name_brand='', name_chip='JJ', 
                     frames_marker_dist = [250,250],
                     name_mask='', name_copy='')

class JunctionTestQCC(Chip):
  """Chip with grid of test junctions."""

  fwid = [120 for _ in range(24)]
 
  array_widths  = [1000, 1000, 1000, 1000, 1200, 1200, 1200, 1200,
                   1300, 1300, 1300, 1300, 1400, 1400, 1400, 1400,
                   1500, 1500, 1500, 1500, 1300, 1300, 1300, 1300]
  jj_numbers = [57,55,53,51, 57,55,53,51, 57,55,53,51, 57,55,53,51, 57,55,53,51, 57,55,53,51]

  Q_finger_widths = Param(pdt.TypeList, "Width of the finger, list.", fwid, unit="[μm]")
  Q_bridge_gap = Param(pdt.TypeDouble, "Gap between finger and hook.", 0.15, unit="μm")
  Q_hook_thickness = Param(pdt.TypeDouble, "Thickness of hook on catch.", 0.100, unit="μm")

  A_bridge_gap = Param(pdt.TypeDouble, "Bridge width.", 0.15, unit="μm")
  A_gap_spacing = Param(pdt.TypeDouble, "Spacing between gaps.", 0.8, unit="μm")
  A_array_widths = Param(pdt.TypeList, "Array JJ bridge widths.", array_widths, unit="[μm]")
  A_junction_number = Param(pdt.TypeList, "Number of JJs in each array.", jj_numbers)

  def build(self):

    # junction positions from Ansys
    jj_pos_A = pya.DTrans(0, False, -75, 158.6035 + 6)
    jj_pos_B = pya.DTrans(0, False, 75, 158.6035 + 6)
    jj_pos_C = pya.DTrans(0, False, 0, -45.0)
    
    small_jj_gap = 10

    jj_trans = [jj_pos_C, jj_pos_A, jj_pos_B]

    small_params = {"bridge_gap": self.Q_bridge_gap,
                    "hook_thickness": self.Q_hook_thickness,
                    "hook_undercut": 0.5,
                    "pad_to_pad_separation": small_jj_gap,
                    "hook_lead_thickness": 0.2,
                    "noSQUID": True}
    array_params = {
                    "bridge_gap": self.A_bridge_gap,
                    "gap_spacing": self.A_gap_spacing,
                    # "junction_number": self.A_junction_number,
                    "pad_to_pad_separation": 70.792,
    }

    small_short_params = {"bridge_gap": 0,
                    "hook_thickness": self.Q_hook_thickness,
                    "hook_undercut": 0.5,
                    "pad_to_pad_separation": small_jj_gap,
                    "hook_lead_thickness": 0.2,
                    "noSQUID": True}
    array_short_params = {
                    "bridge_gap": 0,
                    "gap_spacing": self.A_gap_spacing,
                    # "junction_number": self.A_junction_number,
                    "pad_to_pad_separation": 70.792,
    }
    
    load_libraries(path=TestStructure.LIBRARY_PATH)
    penguin = self.layout.create_cell("QCCv2", TestStructure.LIBRARY_NAME)

    translations = [[pya.DTrans(0, False, 900 + i*650, 3800 - j*850) for i in range(6)] for j in range(4)]

    i = 0
    j = 0
    for ti, trow in enumerate(translations):
      # for t, jt in zip(trow, small_jj_trans):
      for ri, t in enumerate(trow):
        self.insert_cell(penguin, t, "p1")

        if i < len(min(self.Q_finger_widths, self.A_array_widths)):
          qWidth = self.Q_finger_widths[i]
          aWidth = self.A_array_widths[i]
          jjN = self.A_junction_number[i]
          i += 1
        else:
          qWidth = self.Q_finger_widths[j]
          aWidth = self.A_array_widths[j]
          jjN = self.A_junction_number[j]
          j += 2  

        produce_label(self.cell, f"{qWidth}", t * pya.DPoint(-100, 550), LabelOrigin.TOPLEFT, 0, 0, 
                          [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)
        if ti < 3:
          produce_label(self.cell, f"{aWidth}_{jjN}", t * pya.DPoint(-200, 450),  LabelOrigin.TOPLEFT, 0, 0, 
                            [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)
        else:
          produce_label(self.cell, f"{aWidth}_S", t * pya.DPoint(-200, 450),  LabelOrigin.TOPLEFT, 0, 0, 
                            [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)
        
        junction_cell = self.add_element(Overlap2, finger_width=qWidth*1e-3,  **small_params)
        array_cell = self.add_element(OverlapArray, bridge_length=aWidth*1e-3, junction_number=jjN, **array_params)

        junction_short = self.add_element(Overlap2, finger_width=qWidth*1e-3,  **small_short_params)
        array_short = self.add_element(OverlapArray, bridge_length=aWidth*1e-3, junction_number=jjN, **array_short_params)

        for k, jt in enumerate(jj_trans):
          if k < 1:
            if ti < 3:
              self.insert_cell(junction_cell, t * jt, f"{ti}{ri}{k}")
            else:
              self.insert_cell(junction_short, t * jt, f"{ti}{ri}{k}")
          else:
            if ti < 3:
              self.insert_cell(array_cell, t * jt, f"{ti}{ri}{k}")
            else:
              self.insert_cell(array_short,t * jt, f"{ti}{ri}{k}")
            
            

    resolution = self.layout.create_cell("ResolutionTestStructure_NB", TestStructure.LIBRARY_NAME)
    self.insert_cell(resolution, pya.DTrans(0, False, 3700, 500), "res")
    # self.insert_cell(resolution, pya.DTrans(1, False, 4750, 1200), "res")
    # self.insert_cell(Profilometer, pya.DTrans(0, False, 3000, 500), "pro")
