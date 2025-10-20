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
from kqcircuits.test_structures.profilometer import Profilometer
from kqcircuits.util.label import produce_label, LabelOrigin

from kqcircuits.test_structures.test_structure import TestStructure
from kqcircuits.elements.element import Element

from kqcircuits.util.groundgrid import make_grid

from kqcircuits.util.library_helper import load_libraries


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
    name_chip="",
    frames_marker_dist=[250, 250],
    name_mask="",
    name_copy="",
)

# @add_parameters_from(Junction, "junction_type")
# @add_parameters_from(Junction, "junction_type")


class LogoNIST(Chip):
    """C ."""

    def produce_ground_grid(self):
        # no ground grid on test junction chip
        pass 

    def build(self):

        # create a box to subtract from, all the move and Box dimensions need to be in nanometers?
        chip_region = pya.Region(pya.DPolygon(pya.DBox(0, 0, 5200e3, 5200e3)))

        # layer 1/0 as exported from HFSS
        # Get the different layers that are exported
        # qubit_shapes_base_metal_gap_wo_grid = qubit_cell.shapes(self.layout.layer(1, 0))
        # qubit_shapes_ground_grid_avoidance = qubit_cell.shapes(self.layout.layer(2, 0))

        # pattern = pya.Region(qubit_shapes_base_metal_gap_wo_grid).moved(2600e3, 2600e3)
        # difference_pattern = chip_region - pattern
        # protection_pattern = pya.Region(qubit_shapes_ground_grid_avoidance).moved(2600e3, 2600e3)

        # self.cell.shapes(self.get_layer("base_metal_gap_wo_grid", 0)).insert(difference_pattern)
        # self.cell.shapes(self.get_layer("ground_grid_avoidance", 0)).insert(protection_pattern)

        # load_libraries(path=TestStructure.LIBRARY_PATH)
        # penguin = self.layout.create_cell("QQQv2_pads", TestStructure.LIBRARY_NAME)
        # penguin_translations = [pya.DTrans(0, False, 4400 - i * 650, 4150) for i in range(2)]

        # for i, trans in enumerate(penguin_translations):
        #     if i == 0:
        #         self.insert_cell(penguin, trans)

        load_libraries(path=Element.LIBRARY_PATH)
        NISTlogo = self.layout.create_cell("NISTlogo", Element.LIBRARY_NAME)
        flatiron = self.layout.create_cell("flatiron2", Element.LIBRARY_NAME)
        CUlogo = self.layout.create_cell("CU", Element.LIBRARY_NAME)
        qqq_logo = self.layout.create_cell("qqq_logo", Element.LIBRARY_NAME)
        AMPlogo = self.layout.create_cell("AMPlogo", Element.LIBRARY_NAME)

        scaleFactor = 4805 / 233.193
        self.insert_cell(flatiron, pya.DCplxTrans(scaleFactor, 0, False, -52, 500), "flats")

        scaleFactor = 1200 / 37
        self.insert_cell(qqq_logo, pya.DCplxTrans(scaleFactor, 0, False, 3960, 3100), "qqqs")

        scaleFactor = 800 / 41.217
        self.insert_cell(CUlogo, pya.DCplxTrans(scaleFactor, 0, False, 500, 3400), "cu")

        scaleFactor = 3000 / 155
        self.insert_cell(AMPlogo, pya.DCplxTrans(scaleFactor, 0, False, 2800, 3900), "AMP")

        # measured from crap GDS logo file
        scaleFactor = 70 / 158.016
        # self.insert_cell(NISTlogo, pya.DCplxTrans(scaleFactor, 0, False, 4200, 4000), "logo")
        self.insert_cell(NISTlogo, pya.DCplxTrans(scaleFactor, 0, False, 1000, 3000), "logo")

        # produce_label(
        #     self.cell,
        #     label="Z.Parrott",
        #     location=pya.DPoint(325, 4275),
        #     origin=LabelOrigin.TOPLEFT,
        #     origin_offset=0,
        #     margin=10,
        #     layers=[self.face()["base_metal_gap_wo_grid"]],
        #     layer_protection=self.face()["ground_grid_avoidance"],
        #     size=50,
        # )
