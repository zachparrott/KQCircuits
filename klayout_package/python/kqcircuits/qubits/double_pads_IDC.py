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
from kqcircuits.junctions.overlap_junction2 import Overlap2
from kqcircuits.junctions.squid import Squid

from kqcircuits.util.parameters import Param, pdt, add_parameters_from
from kqcircuits.qubits.qubit import Qubit
from kqcircuits.pya_resolver import pya
from kqcircuits.util.refpoints import WaveguideToSimPort, JunctionSimPort


@add_parameters_from(Squid, junction_type="Overlap2")
@add_parameters_from(Overlap2)  # , "finger_width")
class DoublePadsIDC(Qubit):
    """A two-island qubit with an interdigitated capacitor (IDC) coupling between island1 and the readout coupler.

    The overall structure follows DoublePadsDifferential:
    - Two rectangular qubit islands (island1 above, island2 below) connected by a SQUID/junction.
    - A rectangular coupler pad above island1, connected to the exterior readout port via a thin arm.

    The key difference: the capacitive gap between the coupler's bottom edge and island1's top edge is replaced by an
    interdigitated capacitor. Even-indexed fingers are rooted on island1 (pointing up) and odd-indexed fingers are
    rooted on the coupler pad (pointing down). All fingers are centred at x=0 and have equal width/spacing.

    The IDC zone height is derived automatically as ``idc_finger_length + idc_finger_gap``, so ``idc_finger_gap``
    controls both the lateral spacing between adjacent fingers *and* the longitudinal end-gap from each finger tip
    to the opposing pad. For actual interdigitation the user should keep ``idc_finger_length > idc_finger_gap``.

    Ports:
    - ``cplr``: readout port at the top of the ground gap.
    - ``drive``: drive port at a configurable position.
    """

    ground_coupler_extend = Param(
        pdt.TypeDouble,
        "Additional upward extension of the ground gap.",
        0,
        unit="μm",
    )
    ground_gap_r = Param(pdt.TypeDouble, "Ground gap rounding radius", 0, unit="μm")
    coupler_extent = Param(
        pdt.TypeList, "Width, height of the coupler (µm, µm)", [250, 50]
    )
    coupler_r = Param(pdt.TypeDouble, "Coupler rounding radius", 10.0, unit="μm")
    coupler_a = Param(
        pdt.TypeDouble,
        "Width of the coupler waveguide center conductor",
        Element.a,
        unit="μm",
    )
    squid_offset = Param(
        pdt.TypeDouble, "Offset between SQUID center and qubit center", -100, unit="μm"
    )
    island1_extent = Param(
        pdt.TypeList, "Width, height of the first qubit island (µm, µm)", [250, 300]
    )
    island1_r = Param(
        pdt.TypeDouble, "First qubit island rounding radius", 10.0, unit="μm"
    )
    island2_extent = Param(
        pdt.TypeList, "Width, height of the second qubit island (µm, µm)", [734.9, 300]
    )
    island2_r = Param(
        pdt.TypeDouble, "Second qubit island rounding radius", 10.0, unit="μm"
    )
    drive_position = Param(
        pdt.TypeList, "Coordinate for the drive port (µm, µm)", [-450, 0]
    )
    island1_taper_width = Param(
        pdt.TypeDouble,
        "First qubit island tapering width on the island side",
        10,
        unit="µm",
    )
    island1_taper_junction_width = Param(
        pdt.TypeDouble,
        "First qubit island tapering width on the junction side",
        10,
        unit="µm",
    )
    island2_taper_width = Param(
        pdt.TypeDouble,
        "Second qubit island tapering width on the island side",
        10,
        unit="µm",
    )
    island2_taper_junction_width = Param(
        pdt.TypeDouble,
        "Second qubit island tapering width on the junction side",
        10,
        unit="µm",
    )
    island_island_gap = Param(
        pdt.TypeDouble, "Island to island gap distance", 20, unit="µm"
    )
    grid_pads = Param(pdt.TypeBoolean, "Boolean whether to include grid pads", False)
    with_squid = Param(pdt.TypeBoolean, "Boolean whether to include the squid", True)

    # IDC parameters
    idc_finger_number = Param(
        pdt.TypeInt,
        "Total number of IDC fingers (half rooted on island1, half on coupler)",
        6,
    )
    idc_finger_width = Param(pdt.TypeDouble, "Width of each IDC finger", 30, unit="µm")
    idc_finger_gap = Param(
        pdt.TypeDouble,
        "Gap between coupler and island1 in IDC fingers.",
        10,
        unit="µm",
    )
    idc_finger_length = Param(
        pdt.TypeDouble,
        "Length of each IDC finger. End-gap to opposing pad = idc_finger_gap.",
        200,
        unit="µm",
    )
    idc_finger_r = Param(
        pdt.TypeDouble,
        "Rounding radius applied to the finger tips and finger-root junctions",
        2,
        unit="µm",
    )
    junction_rotate = Param(
        pdt.TypeBoolean, "Rotate the junction by 180 degrees", False
    )

    @property
    def coupler_offset(self):
        """Computed IDC zone height: finger_length + finger_gap.

        This ensures the longitudinal end-gap from each finger tip to the opposing
        pad equals ``idc_finger_gap``.
        """
        return self.idc_finger_length + self.idc_finger_gap

    def build(self):

        self.ground_gap = [
            self.island2_extent[0] + 100,
            self.island2_extent[1]
            + self.island_island_gap
            + self.island1_extent[1]
            + 100
            + 200,
        ]

        # Probe SQUID height from refpoints
        temp_squid_cell = self.add_element(
            Squid,
            junction_type=self.junction_type,
            finger_width=self.finger_width,
            hook_thickness=self.hook_thickness,
            hook_undercut=self.hook_undercut,
            hook_lead_thickness=self.hook_lead_thickness,
            bridge_gap=self.bridge_gap,
        )
        temp_squid_ref = self.get_refpoints(temp_squid_cell)
        squid_height = temp_squid_ref["port_common"].distance(pya.DPoint(0, 0))

        squid_center_y = self.squid_offset

        # Compute taper_height early so we can use it for ground-gap centering.
        taper_height = (self.island_island_gap - squid_height) / 2

        # Auto-centre the ground gap around the full qubit content.
        # The coupler side extends further from squid_offset than island2 does;
        # auto_extend compensates so the margin is equal on both sides.
        # ground_coupler_extend lets the user nudge the top edge manually on top.
        content_above = (
            squid_height / 2
            + taper_height
            + float(self.island1_extent[1])
            + self.coupler_offset
            + float(self.coupler_extent[1])
        )
        content_below = squid_height / 2 + taper_height + float(self.island2_extent[1])
        auto_extend = content_above - content_below
        ground_gap_top = (
            squid_center_y
            + float(self.ground_gap[1]) / 2
            + auto_extend
            + self.ground_coupler_extend
        )

        # Ground gap
        ground_gap_points = [
            pya.DPoint(float(self.ground_gap[0]) / 2, ground_gap_top),
            pya.DPoint(
                float(self.ground_gap[0]) / 2,
                squid_center_y - float(self.ground_gap[1]) / 2,
            ),
            pya.DPoint(
                -float(self.ground_gap[0]) / 2,
                squid_center_y - float(self.ground_gap[1]) / 2,
            ),
            pya.DPoint(-float(self.ground_gap[0]) / 2, ground_gap_top),
        ]
        ground_gap_polygon = pya.DPolygon(ground_gap_points)
        ground_gap_region = pya.Region(ground_gap_polygon.to_itype(self.layout.dbu))
        ground_gap_region.round_corners(
            self.ground_gap_r / self.layout.dbu,
            self.ground_gap_r / self.layout.dbu,
            self.n,
        )

        # Insert SQUID
        squid_transf = pya.DCplxTrans(
            1, 0, False, pya.DVector(0, self.squid_offset - squid_height / 2)
        )
        if self.junction_rotate:
            squid_transf = squid_transf * pya.DCplxTrans(
                1,
                180,
                False,
                pya.DVector(0, +squid_height),
            )

        if self.with_squid:
            # self.produce_squid(squid_transf, **params["finger_width"])
            self.produce_squid(squid_transf)

        # taper_height already computed above for ground-gap centering

        # Island 1 — flat-top rectangle with junction taper at base
        island1_top_edge = (
            (self.squid_offset + squid_height / 2)
            + taper_height
            + float(self.island1_extent[1])
        )

        # IDC fingers — split by which pad they are rooted on so each set can be
        # merged with its parent pad before rounding.
        island1_fingers, coupler_fingers = self._build_idc(island1_top_edge)

        island1_region = self._build_island1(
            squid_height, taper_height, island1_fingers
        )
        island1_region_prot = self._build_island1_protection(squid_height, taper_height)

        # Island 2
        island2_region = self._build_island2(squid_height, taper_height)
        island2_region_prot = self._build_island2_protection(squid_height, taper_height)

        # Coupler — rectangular pad (with coupler fingers merged in) + thin arm
        coupler_region = self._build_coupler(
            island1_top_edge, coupler_fingers, ground_gap_top
        )
        coupler_prot_region = self._build_coupler_protection(island1_top_edge)

        self.cell.shapes(self.get_layer("base_metal_gap_wo_grid")).insert(
            ground_gap_region - coupler_region - island1_region - island2_region
        )

        # Protection
        protection_polygon = pya.DPolygon(
            [
                p
                + pya.DVector(
                    math.copysign(self.margin, p.x), math.copysign(self.margin, p.y)
                )
                for p in ground_gap_points
            ]
        )
        protection_region = pya.Region(protection_polygon.to_itype(self.layout.dbu))
        protection_region.round_corners(
            (self.ground_gap_r + self.margin) / self.layout.dbu,
            (self.ground_gap_r + self.margin) / self.layout.dbu,
            self.n,
        )
        if self.grid_pads:
            self.cell.shapes(self.get_layer("ground_grid_avoidance")).insert(
                protection_region
                - island1_region_prot
                - island2_region_prot
                - coupler_prot_region
            )
        else:
            self.cell.shapes(self.get_layer("ground_grid_avoidance")).insert(
                protection_region
            )

        # Coupler port — at the top edge of the ground gap
        self.add_port(
            "cplr",
            pya.DPoint(0, ground_gap_top),
            direction=pya.DVector(pya.DPoint(0, ground_gap_top)),
        )

        # Drive port
        self.add_port(
            "drive",
            pya.DPoint(float(self.drive_position[0]), float(self.drive_position[1])),
            direction=pya.DVector(
                float(self.drive_position[0]), float(self.drive_position[1])
            ),
        )

    # ------------------------------------------------------------------
    # IDC
    # ------------------------------------------------------------------

    def _build_idc(self, island1_top_edge):
        """Build the IDC finger metal between island1's top edge and the coupler's bottom edge.

        Even-indexed fingers (0, 2, …) are rooted on island1 and point upward.
        Odd-indexed fingers (1, 3, …) are rooted on the coupler and point downward.
        All fingers are centred symmetrically about x = 0.

        The IDC zone height equals ``coupler_offset = idc_finger_length + idc_finger_gap``,
        so the end-gap from each finger tip to the opposing pad is ``idc_finger_gap``.

        Args:
            island1_top_edge: y-coordinate of the top of island1's body.

        Returns:
            Tuple ``(island1_fingers, coupler_fingers)``: two separate ``pya.Region`` objects
            containing the unrounded rectangular finger bodies for each pad. These are intended
            to be merged into the respective pad before rounding is applied.
        """
        n = int(self.idc_finger_number)
        coupler_bottom = island1_top_edge + self.coupler_offset

        total_width = n * self.idc_finger_width + (n - 1) * self.idc_finger_gap
        x_origin = -total_width / 2  # left edge of finger 0

        island1_polys = []
        coupler_polys = []
        for i in range(n):
            x_left = x_origin + i * (self.idc_finger_width + self.idc_finger_gap)
            x_right = x_left + self.idc_finger_width

            if i % 2 == 0:
                # Island-1-rooted finger: grows upward from island1_top_edge
                island1_polys.append(
                    pya.DPolygon(
                        [
                            pya.DPoint(x_left, island1_top_edge),
                            pya.DPoint(x_right, island1_top_edge),
                            pya.DPoint(
                                x_right, island1_top_edge + self.idc_finger_length
                            ),
                            pya.DPoint(
                                x_left, island1_top_edge + self.idc_finger_length
                            ),
                        ]
                    )
                )
            else:
                # Coupler-rooted finger: grows downward from coupler_bottom
                coupler_polys.append(
                    pya.DPolygon(
                        [
                            pya.DPoint(x_left, coupler_bottom - self.idc_finger_length),
                            pya.DPoint(
                                x_right, coupler_bottom - self.idc_finger_length
                            ),
                            pya.DPoint(x_right, coupler_bottom),
                            pya.DPoint(x_left, coupler_bottom),
                        ]
                    )
                )

        island1_fingers = pya.Region(
            [p.to_itype(self.layout.dbu) for p in island1_polys]
        )
        coupler_fingers = pya.Region(
            [p.to_itype(self.layout.dbu) for p in coupler_polys]
        )
        return island1_fingers, coupler_fingers

    # ------------------------------------------------------------------
    # Islands
    # ------------------------------------------------------------------

    def _build_island1(self, squid_height, taper_height, fingers_region=None):
        """Build first qubit island: flat-top rectangle with a tapering neck at the base.

        The island body spans from ``island1_bottom + taper_height`` (bottom) to
        ``island1_bottom + taper_height + island1_extent[1]`` (top, flat). A
        trapezoidal/rectangular taper narrows from ``island1_taper_width`` at the body
        bottom down to ``island1_taper_junction_width`` at the SQUID connection point.

        Args:
            squid_height: Height of the SQUID cell (distance from SQUID origin to port_common).
            taper_height: Vertical distance from SQUID connection to island body base.
            fingers_region: Optional ``pya.Region`` of island1-rooted IDC fingers. When
                provided the fingers are merged with the island body and the combined shape
                is rounded with ``idc_finger_r`` on top of the island's own ``island1_r``.
        """
        island1_bottom = self.squid_offset + squid_height / 2

        island1_points = [
            # Flat-top rectangle
            pya.DPoint(
                -float(self.island1_extent[0]) / 2, island1_bottom + taper_height
            ),
            pya.DPoint(
                -float(self.island1_extent[0]) / 2,
                island1_bottom + taper_height + float(self.island1_extent[1]),
            ),
            pya.DPoint(
                float(self.island1_extent[0]) / 2,
                island1_bottom + taper_height + float(self.island1_extent[1]),
            ),
            pya.DPoint(
                float(self.island1_extent[0]) / 2, island1_bottom + taper_height
            ),
            # Junction taper (narrows from island body width to junction contact width)
            pya.DPoint(self.island1_taper_width / 2, island1_bottom + taper_height),
            pya.DPoint(self.island1_taper_junction_width / 2, island1_bottom),
            pya.DPoint(-self.island1_taper_junction_width / 2, island1_bottom),
            pya.DPoint(-self.island1_taper_width / 2, island1_bottom + taper_height),
        ]

        island1_region = pya.Region(
            pya.DPolygon(island1_points).to_itype(self.layout.dbu)
        )
        # Round the island body first (island1_r may differ from idc_finger_r)
        island1_region.round_corners(
            self.island1_r / self.layout.dbu, self.island1_r / self.layout.dbu, self.n
        )

        if fingers_region is not None:
            # Merge fingers into island, then round the combined outline so finger
            # tips and root junctions both receive the idc_finger_r treatment.
            island1_region = (island1_region + fingers_region).merged()
            island1_region.round_corners(
                self.idc_finger_r / self.layout.dbu,
                self.idc_finger_r / self.layout.dbu,
                self.n,
            )

        return island1_region

    def _build_island2(self, squid_height, taper_height):
        island2_top = self.squid_offset - squid_height / 2
        island2_points = [
            pya.DPoint(
                -float(self.island2_extent[0]) / 2,
                island2_top - taper_height - float(self.island2_extent[1]),
            ),
            pya.DPoint(
                float(self.island2_extent[0]) / 2,
                island2_top - taper_height - float(self.island2_extent[1]),
            ),
            pya.DPoint(float(self.island2_extent[0]) / 2, island2_top - taper_height),
            pya.DPoint(self.island2_taper_width / 2, island2_top - taper_height),
            pya.DPoint(self.island2_taper_junction_width / 2, island2_top),
            pya.DPoint(-self.island2_taper_junction_width / 2, island2_top),
            pya.DPoint(-self.island2_taper_width / 2, island2_top - taper_height),
            pya.DPoint(-float(self.island2_extent[0]) / 2, island2_top - taper_height),
        ]

        island2_polygon = pya.DPolygon(island2_points)
        island2_region = pya.Region(island2_polygon.to_itype(self.layout.dbu))
        island2_region.round_corners(
            self.island2_r / self.layout.dbu, self.island2_r / self.layout.dbu, self.n
        )
        return island2_region

    # ------------------------------------------------------------------
    # Protection regions
    # ------------------------------------------------------------------

    def _build_island1_protection(self, squid_height, taper_height):
        """Flat-top bounding box for island1 (inset by margin on all sides — protection region)."""
        island1_bottom = self.squid_offset + squid_height / 2

        island1_points = [
            pya.DPoint(
                -float(self.island1_extent[0]) / 2 + self.margin,
                island1_bottom + taper_height + self.margin,
            ),
            pya.DPoint(
                -float(self.island1_extent[0]) / 2 + self.margin,
                island1_bottom
                + taper_height
                + float(self.island1_extent[1])
                - self.margin,
            ),
            pya.DPoint(
                float(self.island1_extent[0]) / 2 - self.margin,
                island1_bottom
                + taper_height
                + float(self.island1_extent[1])
                - self.margin,
            ),
            pya.DPoint(
                float(self.island1_extent[0]) / 2 - self.margin,
                island1_bottom + taper_height + self.margin,
            ),
        ]

        island1_polygon = pya.DPolygon(island1_points)
        island1_region = pya.Region(island1_polygon.to_itype(self.layout.dbu))
        island1_region.round_corners(
            (self.island1_r + self.margin) / self.layout.dbu,
            (self.island1_r + self.margin) / self.layout.dbu,
            self.n,
        )
        return island1_region

    def _build_island2_protection(self, squid_height, taper_height):
        island2_top = self.squid_offset - squid_height / 2
        island2_points = [
            pya.DPoint(
                -float(self.island2_extent[0]) / 2 + self.margin,
                island2_top
                - taper_height
                - float(self.island2_extent[1])
                + self.margin,
            ),
            pya.DPoint(
                float(self.island2_extent[0]) / 2 - self.margin,
                island2_top
                - taper_height
                - float(self.island2_extent[1])
                + self.margin,
            ),
            pya.DPoint(
                float(self.island2_extent[0]) / 2 - self.margin,
                island2_top - taper_height - self.margin,
            ),
            pya.DPoint(
                -float(self.island2_extent[0]) / 2 + self.margin,
                island2_top - taper_height - self.margin,
            ),
        ]

        island2_polygon = pya.DPolygon(island2_points)
        island2_region = pya.Region(island2_polygon.to_itype(self.layout.dbu))
        island2_region.round_corners(
            (self.island2_r + self.margin) / self.layout.dbu,
            (self.island2_r + self.margin) / self.layout.dbu,
            self.n,
        )
        return island2_region

    # ------------------------------------------------------------------
    # Coupler
    # ------------------------------------------------------------------

    def _build_coupler(
        self, first_island_top_edge, fingers_region=None, ground_gap_top=None
    ):
        coupler_bottom = first_island_top_edge + self.coupler_offset
        coupler_top_edge = coupler_bottom + float(self.coupler_extent[1])

        coupler_body = pya.Region(
            pya.DPolygon(
                [
                    pya.DPoint(-float(self.coupler_extent[0]) / 2, coupler_top_edge),
                    pya.DPoint(-float(self.coupler_extent[0]) / 2, coupler_bottom),
                    pya.DPoint(float(self.coupler_extent[0]) / 2, coupler_bottom),
                    pya.DPoint(float(self.coupler_extent[0]) / 2, coupler_top_edge),
                ]
            ).to_itype(self.layout.dbu)
        )
        # Round the coupler body first
        coupler_body.round_corners(
            self.coupler_r / self.layout.dbu, self.coupler_r / self.layout.dbu, self.n
        )

        if fingers_region is not None:
            # Merge coupler-rooted fingers into body, then round the combined shape
            coupler_body = (coupler_body + fingers_region).merged()
            coupler_body.round_corners(
                self.idc_finger_r / self.layout.dbu,
                self.idc_finger_r / self.layout.dbu,
                self.n,
            )

        # Thin arm connecting the coupler body to the readout port opening.
        # arm_top must reach the actual top edge of the ground gap (passed in as ground_gap_top).
        arm_top = (
            ground_gap_top
            if ground_gap_top is not None
            else (
                self.squid_offset
                + float(self.ground_gap[1]) / 2
                + self.ground_coupler_extend
            )
        )
        coupler_path = pya.Region(
            pya.DPolygon(
                [
                    pya.DPoint(-self.coupler_a / 2, arm_top),
                    pya.DPoint(self.coupler_a / 2, arm_top),
                    pya.DPoint(self.coupler_a / 2, coupler_top_edge),
                    pya.DPoint(-self.coupler_a / 2, coupler_top_edge),
                ]
            ).to_itype(self.layout.dbu)
        )

        return coupler_body + coupler_path

    def _build_coupler_protection(self, first_island_top_edge):
        coupler_top_edge = (
            first_island_top_edge + self.coupler_offset + float(self.coupler_extent[1])
        )
        protection_polygon = pya.DPolygon(
            [
                pya.DPoint(
                    -float(self.coupler_extent[0]) / 2 + self.margin,
                    coupler_top_edge - self.margin,
                ),
                pya.DPoint(
                    -float(self.coupler_extent[0]) / 2 + self.margin,
                    first_island_top_edge + self.coupler_offset + self.margin,
                ),
                pya.DPoint(
                    float(self.coupler_extent[0]) / 2 - self.margin,
                    first_island_top_edge + self.coupler_offset + self.margin,
                ),
                pya.DPoint(
                    float(self.coupler_extent[0]) / 2 - self.margin,
                    coupler_top_edge - self.margin,
                ),
            ]
        )
        protection_region = pya.Region(protection_polygon.to_itype(self.layout.dbu))
        protection_region.round_corners(
            (self.coupler_r + self.margin) / self.layout.dbu,
            (self.coupler_r + self.margin) / self.layout.dbu,
            self.n,
        )
        return protection_region

    @classmethod
    def get_sim_ports(cls, simulation):
        return [
            JunctionSimPort(floating=True),
            WaveguideToSimPort("port_cplr", side="top"),
        ]
