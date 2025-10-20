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


@add_parameters_from(Squid, junction_type="Sim")
@add_parameters_from(Manhattan)
@add_parameters_from(ManhattanSingleJunction)
class FingerPadsAlternate(Qubit):
    """A two-island qubit, consisting of two interdigitated fingers shunted by a junction, with one capacitive coupler.

    Contains a coupler on the north edge and two separate qubit islands in the center
    joined by a junction or SQUID loaded from another library.
    Refpoint for a readout line at the opening to the coupler and a modifiable refpoint for
    a driveline.
    """

    ground_gap = Param(pdt.TypeList, "Width, height of the ground gap (µm, µm)", [700, 700])
    ground_gap_r = Param(pdt.TypeDouble, "Ground gap rounding radius", 20, unit="μm")
    coupler_extent = Param(pdt.TypeList, "Width, height of the coupler (µm, µm)", [150, 20])
    coupler_r = Param(pdt.TypeDouble, "Coupler rounding radius", 10, unit="μm")
    coupler_a = Param(pdt.TypeDouble, "Width of the coupler waveguide center conductor", Element.a, unit="μm")
    coupler_offset = Param(pdt.TypeDouble, "Distance from first qubit island to coupler", 50, unit="μm")
    # squid_offset = Param(pdt.TypeDouble, "Offset between SQUID center and qubit center", 0, unit="μm")
    drive_position = Param(pdt.TypeList, "Coordinate for the drive port (µm, µm)", [-450, 0])
    island1_taper_width = Param(pdt.TypeDouble, "First qubit island tapering width on the island side", 10, unit="µm")
    island1_taper_junction_width = Param(pdt.TypeDouble,
                                         "First qubit island tapering width on the junction side", 10, unit="µm")
    island2_taper_width = Param(pdt.TypeDouble, "Second qubit island tapering width on the island side", 10, unit="µm")
    island2_taper_junction_width = Param(pdt.TypeDouble,
                                         "Second qubit island tapering width on the junction side", 10, unit="µm")

    finger_backstop_length = Param(pdt.TypeDouble, "Backstop length behind fingers", 20, unit="μm")
    finger_number = Param(pdt.TypeInt, "Number of fingers", 5)
    finger_width = Param(pdt.TypeDouble, "Width of a finger", 20, unit="μm")
    finger_gap = Param(pdt.TypeDouble, "Gap between the fingers", 20, unit="μm")
    finger_length = Param(pdt.TypeDouble, "Length of the fingers", 80, unit="μm")
    corner_r = Param(pdt.TypeDouble, "Corner radius", 2, unit="μm")
    finger_gap_end = Param(pdt.TypeDouble, "Gap between the finger and other pad", 40, unit="μm")
    ground_padding = Param(pdt.TypeDouble, "Ground plane padding", 50, unit="μm")

    def can_create_from_shape_impl(self):
        return self.shape.is_path()

    def build(self):
        x_mid = self.finger_area_width() / 2
        x_bottom = self.a / 2
        x_top = self.a / 2
        y_mid = self.finger_area_length() / 2
        # y_bottom = y_mid + self.finger_width + (self.ground_padding if x_bottom > x_mid else 0.0)
        # y_top = y_mid + self.finger_width + (self.ground_padding if x_top > x_mid else 0.0)
        # y_end = y_mid + self.finger_width + self.ground_padding
        y_bottom = y_mid + self.finger_backstop_length + (self.ground_padding if x_bottom > x_mid else 0.0)
        y_top = y_mid + self.finger_backstop_length + (self.ground_padding if x_top > x_mid else 0.0)
        y_end = y_mid + self.finger_backstop_length + self.ground_padding
        # y_max = y_end + self.corner_r

        region_ground = self.get_ground_region()

        region_taper_top = pya.Region([pya.DPolygon([
            pya.DPoint(x_mid, y_mid),
            pya.DPoint(x_mid, y_top),
            pya.DPoint(-x_mid, y_top),
            pya.DPoint(-x_mid, y_mid)
        ]).to_itype(self.layout.dbu)])
        region_taper_bottom = pya.Region([pya.DPolygon([
            pya.DPoint(x_mid, -y_mid),
            pya.DPoint(x_mid, -y_bottom),
            pya.DPoint(-x_mid, -y_bottom),
            pya.DPoint(-x_mid, -y_mid)
        ]).to_itype(self.layout.dbu)])

        polys_fingers = []
        for i in range(self.finger_number):
            x = i * (self.finger_width + self.finger_gap) - x_mid
            y = (i % 2) * self.finger_gap_end - y_mid
            polys_fingers.append(pya.DPolygon([
                pya.DPoint(x + self.finger_width, y + self.finger_length),
                pya.DPoint(x + self.finger_width, y),
                pya.DPoint(x, y),
                pya.DPoint(x, y + self.finger_length)
            ]))

        # SQUID
        # Create temporary SQUID cell to calculate SQUID height
        temp_squid_cell = self.add_element(Squid, junction_type=self.junction_type)
        temp_squid_ref = self.get_refpoints(temp_squid_cell)
        squid_height = temp_squid_ref["port_common"].distance(pya.DPoint(0, 0))
        # Now actually add SQUID

        # location is dependent on number of fingers
        squid_loc_y1 = self.finger_length / 2 - squid_height / 2
        squid_loc_y2 = - self.finger_length / 2 - squid_height / 2

        squid_x = 0 if self.finger_number % 2 else (self.finger_gap + self.finger_width) / 2
        squid_y = squid_loc_y2 if self.finger_number % 4 in (2,3) else squid_loc_y1

        squid_transf = pya.DCplxTrans(1, 0, False, pya.DVector(squid_x, squid_y))
        self.produce_squid(squid_transf)

        # make the tapers to junction
        taper_height = (self.finger_gap_end - squid_height) / 2

        if self.finger_number % 4 in (2,3):
            top_pos = (self.finger_gap_end - self.finger_length)/2
            bottom_pos = -(self.finger_length + self.finger_gap_end)/2
        else:
            top_pos = (self.finger_gap_end + self.finger_length)/2
            bottom_pos = (self.finger_length - self.finger_gap_end)/2
            
        taper_bottom = self._build_taper_bottom(squid_height, taper_height, squid_x, bottom_pos)
        taper_top = self._build_taper_top(squid_height, taper_height, squid_x, top_pos)

        region_fingers = pya.Region([
            poly.to_itype(self.layout.dbu) for poly in polys_fingers
        ])
        region_etch = region_taper_bottom + region_taper_top + region_fingers 
        region_etch.round_corners(self.corner_r / self.layout.dbu, self.corner_r / self.layout.dbu, self.n)
        self.cut_region(region_etch, x_mid, y_end)
        
        # add coupler
        coupler_region = self._build_coupler(self.finger_area_length() / 2 + self.finger_backstop_length)

        region = region_ground - region_etch - taper_bottom - taper_top - coupler_region

        self.cell.shapes(self.get_layer("base_metal_gap_wo_grid")).insert(region)

        # protection
        region_protection = region_ground.size(self.margin / self.layout.dbu, self.margin / self.layout.dbu, 2).merged()
        self.add_protection(region_protection)

        # Coupler port
        self.add_port("cplr", pya.DPoint(0, float(self.ground_gap[1]) / 2),
                      direction=pya.DVector(pya.DPoint(0, float(self.ground_gap[1]))))
        
        # Drive port
        self.add_port("drive", pya.DPoint(float(self.drive_position[0]), float(self.drive_position[1])),
                      direction=pya.DVector(float(self.drive_position[0]), float(self.drive_position[1])))

        # adds annotation based on refpoints calculated above

    def _build_taper_bottom(self, squid_height, taper_height, x0, y0):
        island2_bottom = 0 #+ squid_height / 2

        island2_taper = pya.Region(pya.DPolygon([
            pya.DPoint(x0 + self.island2_taper_junction_width / 2, y0 + island2_bottom),
            pya.DPoint(x0 + self.island2_taper_width / 2, y0 + island2_bottom + taper_height),
            pya.DPoint(x0 + -self.island2_taper_width / 2, y0 + island2_bottom + taper_height),
            pya.DPoint(x0 + -self.island2_taper_junction_width / 2, y0 + island2_bottom),
        ]).to_itype(self.layout.dbu))

        return island2_taper

    def _build_taper_top(self, squid_height, taper_height, x0, y0):
        island1_top = 0 #- squid_height / 2
        
        island2_taper = pya.Region(pya.DPolygon([
            pya.DPoint(x0 + self.island1_taper_width / 2, y0 + island1_top),
            pya.DPoint(x0 + self.island1_taper_junction_width / 2, y0 + island1_top - taper_height),
            pya.DPoint(x0 + -self.island1_taper_junction_width / 2, y0 + island1_top - taper_height),
            pya.DPoint(x0 + -self.island1_taper_width / 2, y0 + island1_top),
        ]).to_itype(self.layout.dbu))
        return island2_taper

    def get_ground_region(self):
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

        return ground_gap_region

    def finger_area_width(self):
        return self.finger_number * self.finger_width + (self.finger_number - 1) * self.finger_gap

    def finger_area_length(self):
        return self.finger_length + self.finger_gap_end

    def cut_region(self, region, x_max, y_max):
        cutter = pya.Region([pya.DPolygon([
            pya.DPoint(x_max, -y_max),
            pya.DPoint(x_max, y_max),
            pya.DPoint(-x_max, y_max),
            pya.DPoint(-x_max, -y_max)
        ]).to_itype(self.layout.dbu)])
        region &= cutter

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


    @classmethod
    def get_sim_ports(cls, simulation):
        return Element.bottom_and_top_waveguides(simulation)

    
    # @classmethod
    # def get_sim_ports(cls, simulation):
    #     return [JunctionSimPort(), WaveguideToSimPort("port_cplr", side="top")]
