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

from kqcircuits.test_structures.test_structure import TestStructure
from kqcircuits.test_structures.profilometer import Profilometer
from kqcircuits.test_structures.junction_test_pads.junction_test_pads_simple import JunctionTestPadsSimple

from kqcircuits.junctions.overlap_array import OverlapArray


from kqcircuits.util.label import produce_label, LabelOrigin


@add_parameters_from(
    ChipFrame,
    box=pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200)),
    marker_types=["Marker Dummy"] * 4,
    chip_dicing_width=50,
    chip_dicing_in_base_metal=True,
)
@add_parameters_from(
    Chip,
    face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200))],
    frames_dice_width=[200, 200],
    name_brand="",
    name_chip="JJ",
    frames_marker_dist=[250, 250],
    name_mask="test",
    name_copy="",
)
class JunctionTestArray5v2Double(Chip):
    """Chip with grid of test junctions."""

    array_widths = Param(pdt.TypeList, "Array bridge lengths.", [2300, 2600, 2900, 3200, 3500], unit="[nm]")

    array_gap = Param(pdt.TypeDouble, "Distance between arrays", 4.0, unit="μm")
    # Array junctions
    A_bridge_gap = Param(pdt.TypeDouble, "Bridge width.", 0.15, unit="μm")
    A_gap_spacing = Param(pdt.TypeDouble, "Spacing between gaps.", 0.8, unit="μm")
    A_junction_number = Param(pdt.TypeList, "Number of junctions.", [97, 101, 105, 109, 113])

    def _add_shapes(self, shapes, layer):
        """Merge shapes into a region and add it to layer."""
        region = pya.Region(shapes).merged()
        self.cell.shapes(self.get_layer(layer)).insert(region)

    def build(self):

        # testpad2 = self.add_element(JunctionTestPadsSimple, pad_width=250, area_height=1850, area_width=3600, pad_spacing=100, only_pads=True)
        # self.insert_cell(testpad2, pya.DTrans(1, True, 2900, 700), "array_test")
        # self.insert_cell(testpad2, pya.DTrans(1, True, 450, 700), "array_test1")

        testpad2 = self.add_element(
            JunctionTestPadsSimple, pad_width=250, area_height=3600, area_width=3600, pad_spacing=100, only_pads=True
        )

        self.insert_cell(testpad2, pya.DTrans(1, True, 900, 700 + 190), "array_test1")

        array_params = {
            "bridge_gap": self.A_bridge_gap,
            "gap_spacing": self.A_gap_spacing,
            # "junction_number": self.A_junction_number,
            "pad_to_pad_separation": 100,
        }
        array_short_params = {
            "bridge_gap": 0,
            "gap_spacing": self.A_gap_spacing,
            # "junction_number": self.A_junction_number,
            "pad_to_pad_separation": 100,
        }

        # Array junctions
        for i in range(len(self.array_widths)):

            array_width = int(float(self.array_widths[i]))

            for j in range(len(self.A_junction_number)):
                if j < 4:
                    jj_num = self.A_junction_number[j]

                    test_cell = self.add_element(
                        OverlapArray, bridge_length=array_width * 1e-3, junction_number=jj_num, **array_params
                    )

                    self.insert_cell(
                        test_cell,
                        pya.DTrans(
                            0, False, 1125 - (array_width * 1e-3 + self.array_gap) / 2 + i * 700, 3900 + 190 - j * 700
                        ),
                        f"{i}{j}_00",
                    )
                    self.insert_cell(
                        test_cell,
                        pya.DTrans(
                            0, False, 1125 + (array_width * 1e-3 + self.array_gap) / 2 + i * 700, 3900 + 190 - j * 700
                        ),
                        f"{i}{j}_0",
                    )

                    self.insert_cell(
                        test_cell,
                        pya.DTrans(
                            0, False, 1475 - (array_width * 1e-3 + self.array_gap) / 2 + i * 700, 3900 + 190 - j * 700
                        ),
                        f"{i}{j}_1",
                    )
                    self.insert_cell(
                        test_cell,
                        pya.DTrans(
                            0, False, 1475 + (array_width * 1e-3 + self.array_gap) / 2 + i * 700, 3900 + 190 - j * 700
                        ),
                        f"{i}{j}_2",
                    )

                # produce shorts
                else:
                    test_cell = self.add_element(
                        OverlapArray, bridge_length=array_width * 1e-3, junction_number=jj_num, **array_short_params
                    )

                    self.insert_cell(
                        test_cell,
                        pya.DTrans(
                            0, False, 1125 - (array_width * 1e-3 + self.array_gap) / 2 + i * 700, 3900 + 190 - j * 700
                        ),
                        f"{i}{j}_3",
                    )
                    self.insert_cell(
                        test_cell,
                        pya.DTrans(
                            0, False, 1125 + (array_width * 1e-3 + self.array_gap) / 2 + i * 700, 3900 + 190 - j * 700
                        ),
                        f"{i}{j}_4",
                    )

                    self.insert_cell(
                        test_cell,
                        pya.DTrans(
                            0, False, 1475 - (array_width * 1e-3 + self.array_gap) / 2 + i * 700, 3900 + 190 - j * 700
                        ),
                        f"{i}{j}_5",
                    )
                    self.insert_cell(
                        test_cell,
                        pya.DTrans(
                            0, False, 1475 + (array_width * 1e-3 + self.array_gap) / 2 + i * 700, 3900 + 190 - j * 700
                        ),
                        f"{i}{j}_6",
                    )

            produce_label(
                self.cell,
                f"{array_width}",
                pya.DPoint(1150 + i * 700, 4450 + 190),
                LabelOrigin.TOPLEFT,
                0,
                0,
                [self.face()["base_metal_gap_wo_grid"]],
                self.face()["ground_grid_avoidance"],
                75,
            )

        for j in range(len(self.A_junction_number)):
            jj_num = self.A_junction_number[j]
            label = f"{jj_num}"
            if j < 4:
                produce_label(
                    self.cell,
                    label,
                    pya.DPoint(650, 4140 - j * 700),
                    LabelOrigin.TOPLEFT,
                    0,
                    0,
                    [self.face()["base_metal_gap_wo_grid"]],
                    self.face()["ground_grid_avoidance"],
                    75,
                )
            else:
                produce_label(
                    self.cell,
                    "short",
                    pya.DPoint(550, 4140 - j * 700),
                    LabelOrigin.TOPLEFT,
                    0,
                    0,
                    [self.face()["base_metal_gap_wo_grid"]],
                    self.face()["ground_grid_avoidance"],
                    75,
                )

        # array separation test
        pts = [
            pya.DPoint(1500, 500),
            pya.DPoint(5200 - 1500 - 750, 500),
            pya.DPoint(5200 - 1500 - 750, 600),
            pya.DPoint(1500, 600),
        ]
        self._add_shapes(pya.DPolygon(pts).to_itype(self.layout.dbu), "base_metal_gap_wo_grid")

        gap_width = 3.5
        gap_cell = self.add_element(OverlapArray, junction_number=81, bridge_length=gap_width, **array_params)
        loop_widths = [
            0.3,
            0.45,
            0.6,
            0.75,
            0.9,
            1.00,
            1.25,
            1.5,
            1.75,
            2.0,
            2.25,
            2.5,
            2.75,
            3.00,
            3.25,
            3.5,
            3.75,
            4.00,
        ]

        for i, lw in enumerate(loop_widths):
            self.insert_cell(gap_cell, pya.DTrans(0, False, 1530 + i * 80, 550), f"g{i}{j}_00")
            self.insert_cell(gap_cell, pya.DTrans(0, False, 1530 + i * 80 + lw + gap_width, 550), f"g{i}{j}_01")

            produce_label(
                self.cell,
                f"{int(lw*1000)}",
                pya.DPoint(1520 + i * 80, 450),
                LabelOrigin.TOPLEFT,
                0,
                0,
                [self.face()["base_metal_gap_wo_grid"]],
                self.face()["ground_grid_avoidance"],
                20,
            )

        produce_label(
            self.cell,
            "double ARRAY",
            pya.DPoint(1800, 4900),
            LabelOrigin.TOPLEFT,
            0,
            0,
            [self.face()["base_metal_gap_wo_grid"]],
            self.face()["ground_grid_avoidance"],
            150,
        )

        produce_label(
            self.cell,
            "JJ Number",
            pya.DPoint(250, 4200 + 190),
            LabelOrigin.TOPLEFT,
            0,
            0,
            [self.face()["base_metal_gap_wo_grid"]],
            self.face()["ground_grid_avoidance"],
            75,
        )
        produce_label(
            self.cell,
            "Bridge width",
            pya.DPoint(250, 4400 + 190),
            LabelOrigin.TOPLEFT,
            0,
            0,
            [self.face()["base_metal_gap_wo_grid"]],
            self.face()["ground_grid_avoidance"],
            75,
        )

        resolution = self.layout.create_cell("ResolutionTestStructure_NB", TestStructure.LIBRARY_NAME)
        self.insert_cell(resolution, pya.DTrans(0, False, 3700, 500), "res")
        self.insert_cell(resolution, pya.DTrans(1, False, 4750, 1200 + 190), "res2")
        # self.insert_cell(Profilometer, pya.DTrans(0, False, 3700, 700), "pro")

        # profilometer = self.layout.create_cell("profilometer", TestStructure.LIBRARY_NAME)
        # self.insert_cell(profilometer, pya.DTrans(0, False, 1200, 500), "pro")
