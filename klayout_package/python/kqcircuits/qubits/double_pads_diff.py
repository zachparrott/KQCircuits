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
from kqcircuits.junctions.squid import Squid
from kqcircuits.junctions.manhattan import Manhattan
from kqcircuits.junctions.manhattan_single_junction import ManhattanSingleJunction
from kqcircuits.util.parameters import Param, pdt, add_parameters_from
from kqcircuits.qubits.qubit import Qubit
from kqcircuits.pya_resolver import pya
from kqcircuits.util.refpoints import WaveguideToSimPort, JunctionSimPort


@add_parameters_from(Squid, junction_type="Manhattan")
@add_parameters_from(Manhattan)
@add_parameters_from(ManhattanSingleJunction)
class DoublePadsDifferential(Qubit):
    """A two-island qubit, consisting of two rounded rectangles shunted by a junction, with one capacitive coupler.

    Contains a coupler on the north edge and two separate qubit islands in the center
    joined by a junction or SQUID loaded from another library.
    Refpoint for a readout line at the opening to the coupler and a modifiable refpoint for
    a driveline.

    Modified for stronger coupling to readout. 
    """

    ground_gap = Param(pdt.TypeList, "Width, height of the ground gap (µm, µm)", [756, 600])
    ground_coupler_extend = Param(pdt.TypeDouble, "Extend coupler side ground edge.", 0, unit="μm")
    ground_gap_r = Param(pdt.TypeDouble, "Ground gap rounding radius", 0, unit="μm")
    coupler_extent = Param(pdt.TypeList, "Width, height of the coupler (µm, µm)", [103.5, 155])
    coupler_r = Param(pdt.TypeDouble, "Coupler rounding radius", 0, unit="μm")
    coupler_a = Param(pdt.TypeDouble, "Width of the coupler waveguide center conductor", Element.a, unit="μm")
    coupler_offset = Param(pdt.TypeDouble, "Distance from first qubit island to coupler", 10, unit="μm")
    squid_offset = Param(pdt.TypeDouble, "Offset between SQUID center and qubit center", -100, unit="μm")
    island1_extent = Param(pdt.TypeList, "Width, height of the first qubit island (µm, µm)", [247, 120])
    island1_r = Param(pdt.TypeDouble, "First qubit island rounding radius", 0, unit="μm")
    island2_extent = Param(pdt.TypeList, "Width, height of the second qubit island (µm, µm)", [506, 120])
    island2_r = Param(pdt.TypeDouble, "Second qubit island rounding radius", 0, unit="μm")
    drive_position = Param(pdt.TypeList, "Coordinate for the drive port (µm, µm)", [-450, 0])
    island1_taper_width = Param(pdt.TypeDouble, "First qubit island tapering width on the island side", 10, unit="µm")
    island1_taper_junction_width = Param(pdt.TypeDouble,
                                         "First qubit island tapering width on the junction side", 10, unit="µm")
    island2_taper_width = Param(pdt.TypeDouble, "Second qubit island tapering width on the island side", 10, unit="µm")
    island2_taper_junction_width = Param(pdt.TypeDouble,
                                         "Second qubit island tapering width on the junction side", 10, unit="µm")

    island_island_gap = Param(pdt.TypeDouble, "Island to island gap distance", 20, unit="µm")
    with_squid = Param(pdt.TypeBoolean, "Boolean whether to include the squid", True)

    def build(self):

        # SQUID geometry calculation
        # Create temporary SQUID cell to calculate SQUID height
        temp_squid_cell = self.add_element(Squid, junction_type=self.junction_type)
        temp_squid_ref = self.get_refpoints(temp_squid_cell)
        squid_height = temp_squid_ref["port_common"].distance(pya.DPoint(0, 0))
        
        # Calculate SQUID center position (this is where the ground gap will be centered)
        squid_center_y = self.squid_offset
        
        # Qubit base - ground gap centered on SQUID position
        ground_gap_points = [
            pya.DPoint(float(self.ground_gap[0]) / 2,  squid_center_y + float(self.ground_gap[1]) / 2 + self.ground_coupler_extend),
            pya.DPoint(float(self.ground_gap[0]) / 2, squid_center_y - float(self.ground_gap[1]) / 2),
            pya.DPoint(-float(self.ground_gap[0]) / 2, squid_center_y - float(self.ground_gap[1]) / 2),
            pya.DPoint(-float(self.ground_gap[0]) / 2, squid_center_y + float(self.ground_gap[1]) / 2 + self.ground_coupler_extend),
        ]
        ground_gap_polygon = pya.DPolygon(ground_gap_points)
        ground_gap_region = pya.Region(ground_gap_polygon.to_itype(self.layout.dbu))
        ground_gap_region.round_corners(self.ground_gap_r / self.layout.dbu,
                                        self.ground_gap_r / self.layout.dbu, self.n)

        # Now actually add SQUID
        squid_transf = pya.DCplxTrans(1, 0, False, pya.DVector(0, self.squid_offset - squid_height / 2))

        if self.with_squid:
            self.produce_squid(squid_transf)

        taper_height = (self.island_island_gap - squid_height)/2

        # First island
        island1_region = self._build_island1(squid_height, taper_height)

        # Second island
        island2_region = self._build_island2(squid_height, taper_height)

        # Coupler gap
        coupler_region = self._build_coupler((self.squid_offset + squid_height / 2)
                                             + taper_height + float(self.island1_extent[1]))

        self.cell.shapes(self.get_layer("base_metal_gap_wo_grid")).insert(
            ground_gap_region - coupler_region - island1_region - island2_region
        )

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

        # Coupler port - now needs to account for offset ground gap
        coupler_port_y = squid_center_y + float(self.ground_gap[1]) / 2 + self.ground_coupler_extend
        self.add_port("cplr", pya.DPoint(0, coupler_port_y),
                      direction=pya.DVector(pya.DPoint(0, coupler_port_y)))

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
            pya.DPoint(-self.coupler_a / 2, self.squid_offset + float(self.ground_gap[1]) / 2 + self.ground_coupler_extend),
            pya.DPoint(self.coupler_a / 2, self.squid_offset + float(self.ground_gap[1]) / 2 + self.ground_coupler_extend),
            pya.DPoint(self.coupler_a / 2, coupler_top_edge),
            pya.DPoint(-self.coupler_a / 2, coupler_top_edge),
        ])
        coupler_path = pya.Region(coupler_path_polygon.to_itype(self.layout.dbu))
        return coupler_region + coupler_path

    def _build_island1(self, squid_height, taper_height):
        """Build first qubit island with integrated junction taper in a single merged polygon.
        
        Key polygon points (ordered counterclockwise):
        - Points 0-7: Island perimeter with coupler cutout
        - Points 8-11: Junction taper transition (expanding downward)
        - taper_height: Vertical distance from island1_bottom to island body
        - coupler_offset: Horizontal gap between island edge and coupler edge
        """
        island1_bottom = self.squid_offset + squid_height / 2
        island1_polygon = pya.DPolygon([
            # Left side at taper-body junction
            pya.DPoint(-float(self.island1_extent[0]) / 2, island1_bottom + taper_height),
            # Left side up to coupler bottom
            pya.DPoint(-float(self.island1_extent[0]) / 2, 
                       island1_bottom + taper_height + float(self.island1_extent[1]) + self.coupler_offset + float(self.coupler_extent[1])),
            # Left inset to coupler edge (left cutout upper corner)
            pya.DPoint(-1*(float(self.coupler_extent[0])/2 + self.coupler_offset), 
                       island1_bottom + taper_height + float(self.island1_extent[1]) + self.coupler_offset + float(self.coupler_extent[1])),
            # Left inset down to island top (left cutout lower corner)
            pya.DPoint(-1*(float(self.coupler_extent[0])/2 + self.coupler_offset), 
                       island1_bottom + taper_height + float(self.island1_extent[1])),
            # Right inset down to island top (right cutout lower corner)
            pya.DPoint((float(self.coupler_extent[0])/2 + self.coupler_offset), 
                       island1_bottom + taper_height + float(self.island1_extent[1])),
            # Right inset up to coupler bottom (right cutout upper corner)
            pya.DPoint((float(self.coupler_extent[0])/2 + self.coupler_offset), 
                       island1_bottom + taper_height + float(self.island1_extent[1]) + self.coupler_offset + float(self.coupler_extent[1])),
            # Right side up to coupler bottom
            pya.DPoint(float(self.island1_extent[0]) / 2, 
                       island1_bottom + taper_height + float(self.island1_extent[1]) + self.coupler_offset + float(self.coupler_extent[1])),
            # Right side down to taper-body junction
            pya.DPoint(float(self.island1_extent[0]) / 2, island1_bottom + taper_height),
            # Taper right outer edge
            pya.DPoint(self.island1_taper_width / 2, island1_bottom + taper_height),
            # Taper right junction connection (narrower)
            pya.DPoint(self.island1_taper_junction_width / 2, island1_bottom),
            # Taper left junction connection (narrower)
            pya.DPoint(-self.island1_taper_junction_width / 2, island1_bottom),
            # Taper left outer edge
            pya.DPoint(-self.island1_taper_width / 2, island1_bottom + taper_height),
        ])
        island1_region = pya.Region(island1_polygon.to_itype(self.layout.dbu))
        island1_region.round_corners(self.island1_r / self.layout.dbu, self.island1_r / self.layout.dbu, self.n)
        
        return island1_region

    def _build_island2(self, squid_height, taper_height):
        island2_top = self.squid_offset - squid_height / 2
        island2_polygon = pya.DPolygon([
            pya.DPoint(-float(self.island2_extent[0]) / 2,
                       island2_top - taper_height - float(self.island2_extent[1])),
            pya.DPoint(float(self.island2_extent[0]) / 2,
                       island2_top - taper_height - float(self.island2_extent[1])),
            pya.DPoint(float(self.island2_extent[0]) / 2, island2_top - taper_height),
            pya.DPoint(self.island2_taper_width / 2, island2_top - taper_height),
            pya.DPoint(self.island2_taper_junction_width / 2, island2_top),
            pya.DPoint(-self.island2_taper_junction_width / 2, island2_top),
            pya.DPoint(-self.island2_taper_width / 2, island2_top - taper_height),
            pya.DPoint(-float(self.island2_extent[0]) / 2, island2_top - taper_height),
        ])
        island2_region = pya.Region(island2_polygon.to_itype(self.layout.dbu))
        island2_region.round_corners(self.island2_r / self.layout.dbu, self.island2_r / self.layout.dbu, self.n)
        
        return island2_region

    @classmethod
    def get_sim_ports(cls, simulation):
        return[
            JunctionSimPort(floating=True), WaveguideToSimPort("port_cplr", side="top")
        ]
