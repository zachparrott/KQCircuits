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


class MaskMarkerNist(Element):
    """The PCell declaration for a MaskMarkerFc.

    optical alignment markers for e-beam litho
    """

    window = Param(pdt.TypeBoolean, "Window in airbridge flyover and UBM layer", False)
    arrow_number = Param(pdt.TypeInt, "Number of arrow pairs in the marker", 3)

    @staticmethod
    def create_cross(arm_length, arm_width):

        m = arm_length / 2
        n = arm_width / 2

        cross = pya.DPolygon([
            pya.DPoint(-n, -m),
            pya.DPoint(-n, -n),
            pya.DPoint(-m, -n),
            pya.DPoint(-m, n),
            pya.DPoint(-n, n),
            pya.DPoint(-n, m),
            pya.DPoint(n, m),
            pya.DPoint(n, n),
            pya.DPoint(m, n),
            pya.DPoint(m, -n),
            pya.DPoint(n, -n),
            pya.DPoint(n, -m)
        ])

        return cross

    def build(self):

        layer_gap = self.get_layer("base_metal_gap_wo_grid")
        layer_flyover = self.get_layer("chip_dicing")
        layer_protection = self.get_layer("ground_grid_avoidance")

        def insert_to_main_layers(shape):
            self.cell.shapes(layer_gap).insert(shape)
        def insert_to_airbridge(shape):
            self.cell.shapes(layer_flyover).insert(shape)

        # protection for the box
        # protection_box = pya.DBox(
        #     pya.DPoint(1000, 3500),
        #     pya.DPoint(-1000, -3500)
        # )
        # self.cell.shapes(layer_protection).insert(protection_box)
        # negative_layer = pya.Region([protection_box.to_itype(self.layout.dbu)])

        # crosses

        arm_widths = [3, 3]
        arm_lengths =   [1000, 1000]

        shift = pya.DPoint(0, -2000)
        shift2 = pya.DPoint(-1500, -2000)
        dislocation = 0
        for i in range(len(arm_widths)):
            if i != 0:
                shift += pya.DPoint(0, 4000)
                shift2 += pya.DPoint(0, 4000)

            inner_shapes = pya.DCplxTrans(1, 0, False, pya.DVector(shift)) * self.create_cross(
                arm_lengths[i], arm_widths[i]
            )
            insert_to_main_layers(inner_shapes)
            # if self.window:
            #     inner_shapes2 = pya.DCplxTrans(1, 0, False, pya.DVector(shift2)) * self.create_cross(
            #         arm_lengths[i], arm_widths[i]
            #     )
            #     insert_to_airbridge(inner_shapes2)

    @classmethod
    def get_marker_locations(cls, cell_marker, **kwargs):
        # set markers to the edge clearance
        wafer_center_x = kwargs.get('wafer_center_x', 0)
        wafer_center_y = kwargs.get('wafer_center_y', 0)
        wafer_rad = kwargs.get('wafer_rad', 75000)
        edge_clearance = kwargs.get('edge_clearance', 1000)
        margin = kwargs.get('box_margin', 1000)
        _h = cell_marker.dbbox().height()
        _w = cell_marker.dbbox().width()
        # coordinate = math.sqrt((wafer_rad - edge_clearance) ** 2 - (_h / 2 + margin) ** 2)
        coordinate = kwargs.get('x_shift', 32500)
        # return [
        #     pya.DTrans(wafer_center_x - coordinate + (margin + _w/2), wafer_center_y) * pya.DTrans.M90,
        #     pya.DTrans(wafer_center_x + coordinate - (margin + _w/2), wafer_center_y) * pya.DTrans.R0]
        return [
            pya.DTrans(wafer_center_x - coordinate - _w/2 + 500, wafer_center_y) * pya.DTrans.M90,
            pya.DTrans(wafer_center_x + coordinate + _w/2 - 500, wafer_center_y) * pya.DTrans.R0]

    @classmethod  # TODO: this is a direct copy from marker.py Will be fixed in future issue
    def get_marker_region(cls, inst, **kwargs):
        margin = kwargs.get('box_margin', 0)
        return pya.Region(inst.bbox()).extents(margin / inst.cell.layout().dbu)
