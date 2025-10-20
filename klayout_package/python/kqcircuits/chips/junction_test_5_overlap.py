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
from kqcircuits.test_structures.test_structure import TestStructure
from kqcircuits.test_structures.profilometer import Profilometer

from kqcircuits.test_structures.junction_test_pads.junction_test_pads_simple import JunctionTestPadsSimple
from kqcircuits.test_structures.junction_test_pads_asym import JunctionTestPadsAsym

from kqcircuits.junctions.overlap_junction2 import Overlap2
from kqcircuits.junctions.overlap_junction2array import OverlapSeries

from kqcircuits.junctions.overlap_junction_simple_array import OverlapSimpleSeries
from kqcircuits.junctions.overlap_junction_simple import OverlapSimple

@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200)),
                      marker_types=["Marker Dummy"]*4,
                      chip_dicing_width=50,
                      chip_dicing_in_base_metal=True,
                      )
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200))],
                     frames_dice_width=[200,200], name_brand='NIST', name_chip='JJ', frames_marker_dist = [250,250],
                     name_mask='t', name_copy='')

class JunctionTest5Overlap(Chip):
  """Chip with grid of test junctions."""

  qubit_widths = Param(pdt.TypeList, "Qubit finger widths.", [50, 100], unit="[nm]")
  bridge_width = Param(pdt.TypeDouble, "Junction bridge width.", 0.15, unit="μm")
  SQUID_widths = Param(pdt.TypeList, "Squid finger widths.", [1000, 2000], unit="[nm]")
  qubit_hook = Param(pdt.TypeDouble, "Thickness of hook on qubit catch.", 0.100, unit="μm")
  squid_taper = Param(pdt.TypeDouble, "SQUID taper (catch side).", 2.0, unit="μm")

  def build(self):
    # labelling
    self.makeFixedLabels()

    # pads for SQUID jjs
    testpad1 = self.add_element(JunctionTestPadsSimple, pad_width=200, area_height=1550, area_width=2050, pad_spacing=50, only_pads=True)   
    self.insert_cell(testpad1, pya.DTrans(1, True, 400, 2475), "SQUID_test")

    # small qubit jjs
    testpad2 = self.add_element(JunctionTestPadsSimple, pad_width=200, area_height=1550, area_width=1550, pad_spacing=50, only_pads=True)
    self.insert_cell(testpad2, pya.DTrans(1, True, 400, 660), "JJ_test")

    # pads for series array
    seriespad = self.add_element(JunctionTestPadsAsym, pad_width=200, pad_spacing_y=50, pad_spacing_x=150, area_height=2300, area_width=1550+300, only_pads=True)
    self.insert_cell(seriespad, pya.DTrans(1, True, 2500, 2750-75), "SQUID_series")
    self.insert_cell(seriespad, pya.DTrans(1, True, 2500, 660-75), "qubit_series2")    

    small_params = {
      "bridge_gap": self.bridge_width,
      "hook_thickness": self.qubit_hook,
      "junction_height": 50, 
      "pad_to_pad_separation": 10,
      "hook_undercut": 0.5,
      "hook_lead_thickness": 0.2,
      "noSQUID": True,
    }
    small_short_params = {
      "bridge_gap": 0,
      "hook_thickness": self.qubit_hook,
      "junction_height": 50, 
      "pad_to_pad_separation": 10,
      "hook_undercut": 0.5,
      "hook_lead_thickness": 0.2,
      "noSQUID": True,
    }
    small_series_params = {
      "bridge_gap": self.bridge_width,
      "hook_thickness": self.qubit_hook,
      "hook_undercut": 0.5,
      "hook_lead_thickness": 0.2,
      "noSQUID": True,
    }
    small_series_short_params = {
      "bridge_gap": 0,
      "hook_thickness": self.qubit_hook,
      "hook_undercut": 0.5,
      "hook_lead_thickness": 0.2,
      "noSQUID": True,
    }
    big_params = {
      "bridge_gap": self.bridge_width,
      "junction_height": 50, 
      "pad_to_pad_separation": 10,
      "taper_width": self.squid_taper,
    }
    big_short_params = {
      "bridge_gap": 0,
      "junction_height": 50, 
      "pad_to_pad_separation": 10,
      "taper_width": self.squid_taper,
    }
    big_series_params = {
      "taper_width": self.squid_taper,
    }

    finger_widths = self.qubit_widths

    # self.squidSeries(2700)

    # for i, small_width in enumerate(finger_widths):
    for i in range(len(self.qubit_widths)):
      for j in range(2):
        if i < 6:
          small_width = self.qubit_widths[i]
          
          # small junctions
          test_cell = self.add_element(Overlap2, finger_width=float(small_width)*1e-3, **small_params)
          self.insert_cell(test_cell, pya.DTrans(0, False, 550 + 2*i *250, 1935), f"{i}{j}_0")
          self.insert_cell(test_cell, pya.DTrans(0, False, 550 + 2*i *250, 1435), f"{i}{j}_2")
          self.insert_cell(test_cell, pya.DTrans(0, False, 550 + (2*i + 1) *250, 1935), f"{i}{j}_3")
          self.insert_cell(test_cell, pya.DTrans(0, False, 550 + (2*i + 1) *250, 1435), f"{i}{j}_4")

          test_short = self.add_element(Overlap2, finger_width=float(small_width)*1e-3, **small_short_params)
          self.insert_cell(test_short, pya.DTrans(0, False, 550 + i *500, 935), f"{i}{j}_1")
          self.insert_cell(test_short, pya.DTrans(0, False, 800 + i *500, 935), f"{i}{j}_5")

          self.qubitSeries(2650+750*i, small_width*1e-3, small_series_short_params, f"{i}{j}", **small_series_params)

          label = f"{small_width}"
          produce_label(self.cell, label, pya.DPoint(500 + i * 500, 2325), LabelOrigin.TOPLEFT, 0, 0, 
                          [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)
          
          # squid junctions
          squid_finger = self.SQUID_widths[i]
          
          label2 = f"{squid_finger}"
          produce_label(self.cell, label2, pya.DPoint(500 + i * 500, 4620), LabelOrigin.TOPLEFT, 0, 0, 
                          [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)    

          squid_cell = self.add_element(OverlapSimple, finger_width=squid_finger*1e-3, **big_params)
          squid_short = self.add_element(OverlapSimple, finger_width=squid_finger*1e-3, **big_short_params)

          self.insert_cell(squid_cell, pya.DTrans(0, False, 550 + i * 500 + j * 250, 4250), f"{i}{j}_06")
          
          self.insert_cell(squid_cell, pya.DTrans(0, False, 550 +10 + i * 500 + j * 250, 3750), f"{i}{j}_07")
          self.insert_cell(squid_cell, pya.DTrans(0, False, 550 -10 + i * 500 + j * 250, 3750), f"{i}{j}_08")

          self.insert_cell(squid_cell, pya.DTrans(0, False, 550 +10 + i * 500 + j * 250, 3250), f"{i}{j}_09")
          self.insert_cell(squid_short, pya.DTrans(0, False, 550 -10 + i * 500 + j * 250, 3250), f"{i}{j}_10")

          self.insert_cell(squid_short, pya.DTrans(0, False, 550 + i * 500 + j * 250, 2750), f"{i}{j}_11")

          self.squidSeries(2650 + 750*i, squid_finger*1e-3, f"{i}{j}", **big_series_params)
    
    resolution = self.layout.create_cell("ResolutionTestStructure_NB", TestStructure.LIBRARY_NAME)
    self.insert_cell(resolution, pya.DTrans(0, False, 3700, 500), "res")
    

    # self.insert_cell(Profilometer, pya.DTrans(0, False, 3000, 500), "pro")
  
  def makeFixedLabels(self):
    produce_label(self.cell, "SQUID", pya.DPoint(2050, 4650), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 100)
    
    produce_label(self.cell, "short", pya.DPoint(2000, 2725), LabelOrigin.TOPLEFT, 0, 0, 
                    [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)   
    produce_label(self.cell, ".5loop", pya.DPoint(2000, 2725+500), LabelOrigin.TOPLEFT, 0, 0, 
                        [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75) 
    produce_label(self.cell, "loop", pya.DPoint(2000, 2725+2*500), LabelOrigin.TOPLEFT, 0, 0, 
                        [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)     
    
    produce_label(self.cell, "QUBIT", pya.DPoint(2050, 2475), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 100)
    
    produce_label(self.cell, "short", pya.DPoint(2000, 950), LabelOrigin.TOPLEFT, 0, 0, 
                        [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)  

  def qubitSeries(self, x_coord, finger, short_params, id, **params):
    padS = [10, 10, 5]
    jjCount = [5, 10, 20]
    endExtend = [178, 38, 29]

    produce_label(self.cell, f"{int(finger*1e3)}", pya.DPoint(x_coord , 2160+270+200), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)
    
    for j, (s, c, e) in enumerate(zip(padS, jjCount, endExtend)):

      produce_label(self.cell, f"{c}x", pya.DPoint(x_coord - 100 + 250*j, 2040+270+200), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
      
      jj_top = self.add_element(OverlapSeries, 
                                  includeTop = True, includeBot = False, pad_to_pad_separation=s, 
                                  finger_width = finger, **params)
      jj_bot = self.add_element(OverlapSeries, 
                                  includeTop = False, includeBot = True,  pad_to_pad_separation=s,
                                  finger_width = finger, junction_height=e, **params)    
      jj_mid = self.add_element(OverlapSeries, 
                                  includeTop = False, includeBot = False,  pad_to_pad_separation=s,
                                  finger_width = finger, **params)
      
      jj_topS = self.add_element(OverlapSeries, 
                                  includeTop = True, includeBot = False, pad_to_pad_separation=s, 
                                  finger_width = finger, **short_params)
      jj_botS = self.add_element(OverlapSeries, 
                                  includeTop = False, includeBot = True,  pad_to_pad_separation=s,
                                  finger_width = finger, junction_height=e, **short_params)    
      jj_midS = self.add_element(OverlapSeries, 
                                  includeTop = False, includeBot = False,  pad_to_pad_separation=s,
                                  finger_width = finger, **short_params)

      for yi, y in enumerate([3075-2090, 3675-2090, 4275-2090]):
        if yi == 0:
          # short in bottom row
          for i in range(c):
            if s > 5:
              if i == 0:
                self.insert_cell(jj_topS, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
              elif i==(c - 1):
                self.insert_cell(jj_botS, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
              else:
                self.insert_cell(jj_midS, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
            else:
              if i == 0:
                self.insert_cell(jj_topS, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (2 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
              elif i==(c - 1):
                self.insert_cell(jj_botS, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (2 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
              else:
                self.insert_cell(jj_midS, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (2 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
        else:
          for i in range(c):
            if s > 5:
              if i == 0:
                self.insert_cell(jj_top, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
              elif i==(c - 1):
                self.insert_cell(jj_bot, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
              else:
                self.insert_cell(jj_mid, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
            else:
              if i == 0:
                self.insert_cell(jj_top, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (2 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
              elif i==(c - 1):
                self.insert_cell(jj_bot, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (2 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
              else:
                self.insert_cell(jj_mid, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (2 + s)), f"{yi}{id}{c}{i}_{j}_{finger}_{x_coord}")
  
    
  def squidSeries(self, x_coord, squid_finger, id, **squid_test_params):
    padS = [10, 10, 3.7]
    jjCount = [5, 10, 20]
    endExtend = [178, 38, 10]

    produce_label(self.cell, f"{int(squid_finger*1e3)}", pya.DPoint(x_coord - 100, 4520+200), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 75)
    
    for j, (s, c, e) in enumerate(zip(padS, jjCount, endExtend)):

      produce_label(self.cell, f"{c}x", pya.DPoint(x_coord - 100 + 250*j, 4400+200), LabelOrigin.TOPLEFT, 0, 0, 
                      [self.face()["base_metal_gap_wo_grid"]], self.face()["ground_grid_avoidance"], 50)
      
      squid_top = self.add_element(OverlapSimpleSeries, 
                                  includeTop = True, includeBot = False, pad_to_pad_separation=s, 
                                  finger_width = squid_finger, **squid_test_params)
      squid_bot = self.add_element(OverlapSimpleSeries, 
                                  includeTop = False, includeBot = True,  pad_to_pad_separation=s,
                                  finger_width = squid_finger, junction_height=e, **squid_test_params)    
      squid_mid = self.add_element(OverlapSimpleSeries, 
                                  includeTop = False, includeBot = False,  pad_to_pad_separation=s,
                                  finger_width = squid_finger, **squid_test_params)
      
      squid_topS = self.add_element(OverlapSimpleSeries, 
                                  includeTop = True, includeBot = False, pad_to_pad_separation=s, bridge_gap = 0,
                                  finger_width = squid_finger, **squid_test_params)
      squid_botS = self.add_element(OverlapSimpleSeries, 
                                  includeTop = False, includeBot = True,  pad_to_pad_separation=s, bridge_gap = 0,
                                  finger_width = squid_finger, junction_height=e, **squid_test_params)    
      squid_midS = self.add_element(OverlapSimpleSeries, 
                                  includeTop = False, includeBot = False,  pad_to_pad_separation=s, bridge_gap = 0,
                                  finger_width = squid_finger, **squid_test_params)

      for yi, y in enumerate([3075, 3250+425, 3950+325]):
        if yi == 0:
          # short in bottom row
          for i in range(c):
            if i == 0:
              self.insert_cell(squid_topS, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"s{c}{yi}{id}{i}_{j}_{x_coord}_{squid_finger}")
            elif i==(c - 1):
              self.insert_cell(squid_botS, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"b{c}{yi}{id}{i}_{j}_{x_coord}_{squid_finger}")
            else:
              self.insert_cell(squid_midS, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"m{c}{yi}{id}{i}_{j}_{x_coord}_{squid_finger}")
        else:
          for i in range(c):
            if i == 0:
              self.insert_cell(squid_top, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"s{c}{yi}{id}{i}_{j}_{x_coord}_{squid_finger}")
            elif i==(c - 1):
              self.insert_cell(squid_bot, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"nn{c}{yi}{id}{i}_{j}_{x_coord}_{squid_finger}")
            else:
              self.insert_cell(squid_mid, pya.DTrans(0, False, x_coord + 250*j, y - s / 2 - i * (4 + s)), f"bb{c}{yi}{id}{i}_{j}_{x_coord}_{squid_finger}")
