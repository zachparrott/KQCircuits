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

import math
from kqcircuits.pya_resolver import pya
from kqcircuits.util.parameters import Param, pdt
from kqcircuits.elements.element import Element

from kqcircuits.elements.markers.marker import Marker

class MarkerDummy(Marker):
    """The PCell declaration for the Dummy Marker.

    Necessary for replace_junction logic
    """
    def produce_geometry(self):
            
        layer_gap = self.get_layer("base_metal_gap_wo_grid")
        layer_gap_for_ebl = self.get_layer("base_metal_gap_for_EBL")
        layer_protection = self.get_layer("ground_grid_avoidance")
        
        def insert_to_main_layers(shape):
            self.cell.shapes(layer_gap).insert(shape)
            self.cell.shapes(layer_gap_for_ebl).insert(shape)
            
        # protection for the box
        protection_box = pya.DBox(pya.DPoint(50, 50), pya.DPoint(-50, -50))
        self.cell.shapes(layer_protection).insert(protection_box)          
        
        # center box
        sqr_uni = pya.DBox(
            pya.DPoint(10, 10),
            pya.DPoint(-10, -10),
        )
        insert_to_main_layers(sqr_uni)                     
    
    def build(self):
        self.produce_geometry()
