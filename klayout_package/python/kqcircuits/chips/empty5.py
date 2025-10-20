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
from kqcircuits.elements.launcher import Launcher
from kqcircuits.elements.waveguide_coplanar import WaveguideCoplanar

@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(5000, 5000)))
# no flip chip alignment markers
@add_parameters_from(ChipFrame, marker_types=['','','',''])
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(5000, 5000))])

class Test5(Chip):
    """Chip with almost all ground metal removed, used for EBL tests."""
    # Chip.shape.box_dwidth = 5000
    # Chip.shape.bod_dheight = 5000
    # Chip.face_boxes = [pya.DBox(pya.DPoint(0, 0), pya.DPoint(5000, 5000)), pya.DBox(pya.DPoint(0, 0), pya.DPoint(5000, 5000))]

    a_launcher = Param(pdt.TypeDouble, "Pad CPW trace center", 240, unit="μm")
    b_launcher = Param(pdt.TypeDouble, "Pad CPW trace gap", 100, unit="μm")
    launcher_width = Param(pdt.TypeDouble, "Pad extent", 300, unit="μm")
    taper_length = Param(pdt.TypeDouble, "Tapering length", 300, unit="μm")
    launcher_frame_gap = Param(pdt.TypeDouble, "Gap at chip frame", 200, unit="μm") 
    launcher_indent = Param(pdt.TypeDouble, "Chip edge to pad port", 900, unit="μm")   
  
    def produce_two_launchers(self, a_launcher, b_launcher, launcher_width, taper_length, launcher_frame_gap, 
                              launcher_indent, pad_pitch, launcher_assignments=None,  enabled=None, chip_box=None,
                            face_id=0):
        
        launcher_cell = self.add_element(Launcher, s=launcher_width, l=taper_length,
                                             a_launcher=a_launcher, b_launcher=b_launcher,
                                             launcher_frame_gap=launcher_frame_gap, face_ids=[self.face_ids[face_id]])

        pads_per_side = [0,1,0,1]

        dirs = (90, 0, -90, 180)
        trans = (pya.DTrans(3, 0, self.box.p1.x, self.box.p2.y),
                 pya.DTrans(2, 0, self.box.p2.x, self.box.p2.y),
                 pya.DTrans(1, 0, self.box.p2.x, self.box.p1.y),
                 pya.DTrans(0, 0, self.box.p1.x, self.box.p1.y))
        _w = self.box.p2.x - self.box.p1.x
        _h = self.box.p2.y - self.box.p1.y
        sides = [_w, _h, _w, _h]

        return self._insert_launchers(dirs, enabled, launcher_assignments, launcher_cell, launcher_indent,
                                      launcher_width, pad_pitch, pads_per_side, sides, trans)
    

    def build(self):
        # self.produce_two_launchers(self.launcher_width, self.b_launcher, self.launcher_width, 
        #                            self.taper_length, self.launcher_frame_gap, self.launcher_indent, 100)

        # self.insert_cell(
        #     WaveguideCoplanar, 
        #     path=pya.DPath([
        #       self.refpoints["1_port"],
        #       self.refpoints["1_port_corner"],
        #       self.refpoints["2_port_corner"],
        #       self.refpoints["2_port"],
        #     ], 0)
        # )
        return True
