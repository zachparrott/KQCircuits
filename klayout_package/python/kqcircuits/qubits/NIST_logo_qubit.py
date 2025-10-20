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

from kqcircuits.elements.element import Element

from kqcircuits.junctions.manhattan import Manhattan

from kqcircuits.util.parameters import Param, pdt, add_parameters_from
from kqcircuits.qubits.qubit import Qubit
from kqcircuits.pya_resolver import pya
from kqcircuits.util.refpoints import WaveguideToSimPort, JunctionSimPort
from kqcircuits.junctions.overlap_junction2 import Overlap2


class NISTLogo(Qubit):
    """A two-island qubit, consisting of two rounded rectangles shunted by a junction, with one capacitive coupler.

    Contains a coupler on the north edge and two separate qubit islands in the center
    joined by a junction or SQUID loaded from another library.
    Refpoint for a readout line at the opening to the coupler and a modifiable refpoint for
    a driveline.
    """

    ground_gap = Param(pdt.TypeList, "Width, height of the ground gap (µm, µm)", [600, 400])
    ground_gap_r = Param(pdt.TypeDouble, "Ground gap rounding radius", 0, unit="μm")
    coupler_extent = Param(pdt.TypeList, "Width, height of the coupler (µm, µm)", [150, 20])
    coupler_r = Param(pdt.TypeDouble, "Coupler rounding radius", 0, unit="μm")
    coupler_a = Param(pdt.TypeDouble, "Width of the coupler waveguide center conductor", Element.a, unit="μm")
    coupler_offset = Param(pdt.TypeDouble, "Distance from first qubit island to coupler", 20, unit="μm")    
    
    drive_position = Param(pdt.TypeList, "Coordinate for the drive port (µm, µm)", [-450, 0])
    pads_height = Param(pdt.TypeDouble,  "Total height of the pads", 200, unit="µm")
    pads_width = Param(pdt.TypeDouble,  "Total width of the pads", 705.652, unit="µm")
    with_squid = Param(pdt.TypeBoolean, "Boolean whether to include the squid", True)

    logo_gap = Param(pdt.TypeDouble, "Gap in logo to sides of the JJ", 20, unit="µm")

    def build(self):
        # measured from crap GDS logo file
        scaleFactor = self.logo_gap / 158.016

        # padWidth = scaleFactor * 2557.105
        # padWidth = scaleFactor * 4137.268
        padWidth = self.pads_width

        jjCoord = pya.DPoint(-326.957, 258.041) * pya.DCplxTrans(scaleFactor, 0, False, 0, 0)

        jjGap = scaleFactor * 4.034

        # Qubit base
        ground_gap_points = [
            pya.DPoint(float(self.ground_gap[0]) / 2,  float(self.ground_gap[1]) / 2),
            pya.DPoint(float(self.ground_gap[0]) / 2, -float(self.ground_gap[1]) / 2),
            pya.DPoint(-float(self.ground_gap[0]) / 2, -float(self.ground_gap[1]) / 2),
            pya.DPoint(-float(self.ground_gap[0]) / 2,  float(self.ground_gap[1]) / 2),
        ]
        ground_gap_polygon = pya.DPolygon(ground_gap_points)
        ground_gap_region = pya.Region(ground_gap_polygon.to_itype(self.layout.dbu))
        ground_gap_region.round_corners(self.ground_gap_r / self.layout.dbu,
                                        self.ground_gap_r / self.layout.dbu, self.n)

        pad_box = pya.Region(pya.DBox(-padWidth/2, -self.pads_height/2, padWidth/2, self.pads_height/2).to_itype(self.layout.dbu))
       
        # Coupler gap
        coupler_region = self._build_coupler(self.pads_height/2)

        self.cell.shapes(self.get_layer("base_metal_gap_wo_grid")).insert(
            ground_gap_region - coupler_region - pad_box
        )

        NISTlogo = self.layout.create_cell("NISTlogoIDC", Element.LIBRARY_NAME)

        self.insert_cell(NISTlogo, pya.DCplxTrans(scaleFactor, 0, False, 0, 0), "logo")

        if self.with_squid:
            junction_cell = self.add_element(Overlap2, pad_to_pad_separation=8)
            self.insert_cell(junction_cell, jjCoord)

        # Protection
        protection_polygon = pya.DPolygon([
            p + pya.DVector(
                    math.copysign(self.margin, p.x),
                    math.copysign(self.margin, p.y)
            ) for p in ground_gap_points
        ])
        protection_region = pya.Region(protection_polygon.to_itype(self.layout.dbu))
        protection_region.round_corners(
            (self.ground_gap_r + self.margin) / self.layout.dbu,
            (self.ground_gap_r + self.margin) / self.layout.dbu,
            self.n
        )
        self.cell.shapes(self.get_layer("ground_grid_avoidance")).insert(protection_region)

        # Coupler port
        self.add_port("cplr", pya.DPoint(0, float(self.ground_gap[1]) / 2),
                      direction=pya.DVector(pya.DPoint(0, float(self.ground_gap[1]))))

        # Drive port
        self.add_port("drive", pya.DPoint(float(self.drive_position[0]), float(self.drive_position[1])),
                      direction=pya.DVector(float(self.drive_position[0]), float(self.drive_position[1])))

    def _build_coupler(self, first_island_top_edge):
        coupler_top_edge = first_island_top_edge + self.coupler_offset + float(self.coupler_extent[1])
        coupler_polygon = pya.DPolygon([
            pya.DPoint(-float(self.coupler_extent[0]) / 2, coupler_top_edge),
            pya.DPoint(-float(self.coupler_extent[0]) / 2, first_island_top_edge + self.coupler_offset),
            pya.DPoint(float(self.coupler_extent[0]) / 2, first_island_top_edge + self.coupler_offset),
            pya.DPoint(float(self.coupler_extent[0]) / 2, coupler_top_edge),
        ])
        coupler_region = pya.Region(coupler_polygon.to_itype(self.layout.dbu))
        coupler_region.round_corners(self.coupler_r / self.layout.dbu, self.coupler_r / self.layout.dbu, self.n)
        coupler_path_polygon = pya.DPolygon([
            pya.DPoint(-self.coupler_a / 2, (float(self.ground_gap[1]) / 2)),
            pya.DPoint(self.coupler_a / 2, (float(self.ground_gap[1]) / 2)),
            pya.DPoint(self.coupler_a / 2, coupler_top_edge),
            pya.DPoint(-self.coupler_a / 2, coupler_top_edge),
        ])
        coupler_path = pya.Region(coupler_path_polygon.to_itype(self.layout.dbu))
        return coupler_region + coupler_path
