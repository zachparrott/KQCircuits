# This code is part of KQCircuits
# Copyright (C) 2026 Zachary Parrott
# Copyright (C) 2026 IQM Finland Oy
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
from kqcircuits.junctions.overlap_junction2 import Overlap2
from kqcircuits.junctions.squid import Squid
from kqcircuits.qubits.qubit import Qubit
from kqcircuits.test_structures.test_structure import TestStructure
from kqcircuits.util.parameters import Param, add_parameters_from, pdt
from kqcircuits.pya_resolver import pya
from kqcircuits.defaults import default_junction_test_pads_type
from kqcircuits.test_structures.junction_test_pads import (
    junction_test_pads_type_choices,
)


@add_parameters_from(Qubit, "junction_type", "mirror_squid", "junction_width")
@add_parameters_from(Overlap2)
class TaperedJJTestPads(TestStructure):
    """Test structure with tapered junctions and pads."""

    default_type = default_junction_test_pads_type
    pad_size = Param(pdt.TypeDouble, "Pad size", 500, unit="μm")
    taper_pad_width = Param(pdt.TypeDouble, "Taper width", 50, unit="μm")
    taper_junction_width = Param(pdt.TypeDouble, "Taper junction width", 25, unit="μm")
    pad_pad_gap = Param(pdt.TypeDouble, "Gap between pads", 70, unit="μm")

    pad_grid = Param(pdt.TypeList, "Grid of pads (rows, columns)", [3, 3])

    junction_test_pads_type = Param(
        pdt.TypeString,
        "Type of junction test pads",
        default_type,
        choices=junction_test_pads_type_choices,
    )

    produce_squid = Qubit.produce_squid

    def _produce_squid(self, trans, index):
        squid_ref_rel = self.produce_squid(trans, False, squid_index=index)

    def _build_bottom_pad(self, junction_height, taper_height):
        pad_bottom = junction_height / 2

        polygon = pya.DPolygon(
            [
                pya.DPoint(
                    -float(self.pad_size) / 2,
                    pad_bottom + taper_height + float(self.pad_size),
                ),
                pya.DPoint(
                    float(self.pad_size) / 2,
                    pad_bottom + taper_height + float(self.pad_size),
                ),
                pya.DPoint(float(self.pad_size) / 2, pad_bottom + taper_height),
                pya.DPoint(self.taper_pad_width / 2, pad_bottom + taper_height),
                pya.DPoint(self.taper_junction_width / 2, pad_bottom),
                pya.DPoint(-self.taper_junction_width / 2, pad_bottom),
                pya.DPoint(-self.taper_pad_width / 2, pad_bottom + taper_height),
                pya.DPoint(-float(self.pad_size) / 2, pad_bottom + taper_height),
            ]
        )
        pad_region = pya.Region(polygon.to_itype(self.layout.dbu))
        pad_region.round_corners(
            0.5 * 10 / self.layout.dbu,
            10 / self.layout.dbu,
            self.n,
        )
        return pad_region

    def _build_top_pad(self, junction_height, taper_height):
        pad_top = -junction_height / 2

        polygon = pya.DPolygon(
            [
                pya.DPoint(
                    -float(self.pad_size) / 2,
                    pad_top - taper_height - float(self.pad_size),
                ),
                pya.DPoint(
                    float(self.pad_size) / 2,
                    pad_top - taper_height - float(self.pad_size),
                ),
                pya.DPoint(float(self.pad_size) / 2, pad_top - taper_height),
                pya.DPoint(self.taper_pad_width / 2, pad_top - taper_height),
                pya.DPoint(self.taper_junction_width / 2, pad_top),
                pya.DPoint(-self.taper_junction_width / 2, pad_top),
                pya.DPoint(-self.taper_pad_width / 2, pad_top - taper_height),
                pya.DPoint(-float(self.pad_size) / 2, pad_top - taper_height),
            ]
        )
        pad_region = pya.Region(polygon.to_itype(self.layout.dbu))
        pad_region.round_corners(
            0.5 * 10 / self.layout.dbu,
            10 / self.layout.dbu,
            self.n,
        )
        return pad_region

    def build(self):

        ground_height = (2 * self.pad_size + self.pad_pad_gap) * self.pad_grid[
            0
        ] + self.pad_pad_gap * (self.pad_grid[0] + 1)
        ground_width = (self.pad_size) * self.pad_grid[1] + self.pad_pad_gap * (
            self.pad_grid[1] + 1
        )

        ground_gap_region = pya.Region(
            pya.DBox(ground_width, ground_height).to_itype(self.layout.dbu)
        )

        # Protection
        protection_region = pya.Region(
            pya.DBox(
                ground_width + 2 * self.margin, ground_height + 2 * self.margin
            ).to_itype(self.layout.dbu)
        )
        self.cell.shapes(self.get_layer("ground_grid_avoidance")).insert(
            protection_region
        )

        temp_junction_cell = self.add_element(
            Squid, junction_type=self.junction_type, taper_width=8
        )
        temp_junction_ref = self.get_refpoints(temp_junction_cell)
        junction_height = temp_junction_ref["port_common"].distance(pya.DPoint(0, 0))

        junction_transf = pya.DTrans(0, False, 0, -junction_height / 2)

        taper_height = (self.pad_pad_gap - junction_height) / 2

        bottom_pad_region = self._build_bottom_pad(junction_height, taper_height)
        top_pad_region = self._build_top_pad(junction_height, taper_height)

        base_trans = pya.DTrans(
            0,
            False,
            (-ground_width / 2 + self.pad_pad_gap + self.pad_size / 2),
            (-ground_height / 2 + 1.5 * self.pad_pad_gap + self.pad_size),
        )

        translations = [
            [
                base_trans
                * pya.DTrans(
                    0,
                    False,
                    j * (self.pad_size + self.pad_pad_gap),
                    i * (2 * self.pad_size + 2 * self.pad_pad_gap),
                )
                for j in range(self.pad_grid[1])
            ]
            for i in range(self.pad_grid[0])
        ]

        subtract_region = pya.Region()

        for i, row in enumerate(translations):
            for j, t in enumerate(row):
                subtract_region += bottom_pad_region.transformed(
                    t.to_itype(self.layout.dbu)
                )
                subtract_region += top_pad_region.transformed(
                    t.to_itype(self.layout.dbu)
                )

                self._produce_squid(junction_transf * t, index=i * self.pad_grid[1] + j)

        # subtract_region += bottom_pad_region.transformed(pya.DTrans(0, False, 0, 200))
        # subtract_region += top_pad_region

        self.cell.shapes(self.get_layer("base_metal_gap_wo_grid")).insert(
            ground_gap_region - subtract_region
        )
