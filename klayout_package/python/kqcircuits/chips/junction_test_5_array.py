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

from kqcircuits.test_structures.junction_test_pads.junction_test_pads_simple import JunctionTestPadsSimple
from kqcircuits.junctions.overlap_junction import Overlap
from kqcircuits.junctions.overlap_array import OverlapArray
from kqcircuits.util.label import produce_label, LabelOrigin

@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200)),
                      marker_types=['','','',''],
                      chip_dicing_width=50,
                      chip_dicing_in_base_metal=True,
                      )
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200))],
                     frames_dice_width=[150,150], name_brand='NIST', name_chip='JJ', 
                     name_mask='', name_copy='')

class JunctionTestArray5(Chip):
  """Chip with grid of test junctions."""

  qubit_widths = Param(pdt.TypeList, "Qubit finger widths.", [50, 100], unit="[nm]")
  squid_widths = Param(pdt.TypeList, "SQUID finger widths.", [550, 1100], unit="[nm]")
  array_widths = Param(pdt.TypeList, "Array bridge lengths.", [1000,1200,1300,1400,1500], unit="[nm]")
  bridge_width = Param(pdt.TypeDouble, "Junction bridge width.", 0.15, unit="μm")
  
  qubit_hook = Param(pdt.TypeDouble, "Thickness of hook on qubit catch.", 0.100, unit="μm")
  squid_hook = Param(pdt.TypeDouble, "Thickness of hook on SQUID catch.", 0.200, unit="μm")

  # Array junctions
  A_bridge_gap = Param(pdt.TypeDouble, "Bridge width.", 0.15, unit="μm")
  A_gap_spacing = Param(pdt.TypeDouble, "Spacing between gaps.", 0.8, unit="μm")
  A_junction_number = Param(pdt.TypeInt, "Number of junctions.", 81)

  def build(self):
    testpad1 = self.add_element(JunctionTestPadsSimple, pad_width=250, area_height=1850, area_width=1500, pad_spacing=100, only_pads=True)
    self.insert_cell(testpad1, pya.DTrans(1, True, 625, 750), "SQUID_test")
    self.insert_cell(testpad1, pya.DTrans(1, True, 625, 2750), "JJ_test")
    
    testpad2 = self.add_element(JunctionTestPadsSimple, pad_width=250, area_height=1500, area_width=3600, pad_spacing=100, only_pads=True)
    self.insert_cell(testpad2, pya.DTrans(1, True, 2900, 700), "array_test")
    
    small_params = {
      "bridge_gap": self.bridge_width,
      "hook_thickness": self.qubit_hook,
      "junction_height": 100, 
      "pad_to_pad_separation": 12,
      "hook_undercut": 0.5
    }
    big_params = {
      "bridge_gap": self.bridge_width,
      "hook_thickness": self.squid_hook,
      "junction_height": 100, 
      "pad_to_pad_separation": 12,
      "hook_width": 3,
      "hook_undercut": 0.5
    }

    array_params = {
      "bridge_gap": self.A_bridge_gap,
      "gap_spacing": self.A_gap_spacing,
      "junction_number": self.A_junction_number,
      "pad_to_pad_separation": 100,
    }

    # Qubit junctions
    for i in range(len(self.qubit_widths)):
      if i < 11:
        small_width = self.qubit_widths[i]
        
        # small junctions
        test_cell = self.add_element(Overlap, finger_width=float(small_width)*1e-3, **small_params)
        self.insert_cell(test_cell, pya.DTrans(0, False, 850 + i *350, 1850))
        self.insert_cell(test_cell, pya.DTrans(0, False, 850 + i *350, 1150))

        label = f"{small_width}"
        produce_label(self.cell, label, pya.DPoint(725 + i * 350, 2525), LabelOrigin.TOPLEFT, 0, 0, 
                        [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)
    
    # SQUID junctions
    for i in range(len(self.squid_widths)):
      if i < 11:    
        # squid junctions
        squid_finger = int(float(self.squid_widths[i]))
        
        squid_cell = self.add_element(Overlap, finger_width=squid_finger*1e-3, **big_params)
        self.insert_cell(squid_cell, pya.DTrans(0, False, 850 + i *350, 3150))
        self.insert_cell(squid_cell, pya.DTrans(0, False, 850 + i *350, 3850))

        label2 = f"{squid_finger}"
        produce_label(self.cell, label2, pya.DPoint(725 + i * 350, 4500), LabelOrigin.TOPLEFT, 0, 0, 
                        [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)    

    # Array junctions
    for i in range(len(self.array_widths)):
      if i < 5:
        
        array_width = int(float(self.array_widths[i]))

        test_cell = self.add_element(OverlapArray, bridge_length=array_width*1e-3, **array_params)
        for j in range(4):
          self.insert_cell(test_cell, pya.DTrans(0, False, 3125 + j * 350, 3900 - i*700))

        label = f"{array_width}"
        produce_label(self.cell, label, pya.DPoint(4475 , 3950 - i * 700), LabelOrigin.TOPLEFT, 0, 0, 
                        [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)    


    produce_label(self.cell, "SQUID", pya.DPoint(1400, 4650), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 100)
      
    produce_label(self.cell, "QUBIT", pya.DPoint(1400, 2675), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 100)
    
    produce_label(self.cell, "ARRAY", pya.DPoint(3350, 4650), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 100)
