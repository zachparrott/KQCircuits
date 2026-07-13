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

from math import pi

import numpy as np
from kqcircuits.junctions.overlap_junction2 import Overlap2
from kqcircuits.pya_resolver import pya
from kqcircuits.elements.element import Element
from kqcircuits.chips.chip import Chip
from kqcircuits.elements.chip_frame import ChipFrame
from kqcircuits.test_structures.profilometer import Profilometer
from kqcircuits.test_structures.test_structure import TestStructure
from kqcircuits.util.library_helper import load_libraries
from kqcircuits.util.parameters import Param, pdt, add_parameters_from
from kqcircuits.elements.launcher import Launcher
from kqcircuits.elements.waveguide_coplanar import WaveguideCoplanar
from kqcircuits.elements.waveguide_composite import WaveguideComposite, Node
from kqcircuits.elements.hanger_resonator import HangerResonator

from kqcircuits.util.label import produce_label, LabelOrigin

from kqcircuits.qubits.double_pads_IDC import DoublePadsIDC

from kqcircuits.elements.smooth_capacitor import SmoothCapacitor

from kqcircuits.test_structures.tapered_jj_test_pads import TaperedJJTestPads


# also sets margin
@add_parameters_from(Element, b=4, a=8, margin=100)
@add_parameters_from(ChipFrame, box=pya.DBox(pya.DPoint(0, 0), pya.DPoint(7600, 7600)))
# no flip chip alignment markers
@add_parameters_from(
    ChipFrame,
    marker_types=["Marker Dummy"] * 4,
    chip_dicing_width=50,
    chip_dicing_in_base_metal=True,
)
@add_parameters_from(
    Chip,
    face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(7600, 7600))],
    name_brand="NIST",
    name_chip="",
    name_copy="",
    frames_dice_width=[200, 200],
    frames_marker_dist=[250, 250],
)
class HangerCPW(Chip):
    """
    Test chip for MLA optical litho validation of minimal dimensions for CPW.
    """

    # radius
    r = 50

    def _produce_cpw_tests(self, positions, centers, gaps):
        for i, pos in enumerate(positions):
            x_pos = pos.x
            y_pos = pos.y
            center = centers[i]
            gap = gaps[i]

            name = f"CPW_{i}"
            self.insert_cell(
                WaveguideComposite,
                nodes=[
                    Node(pya.DPoint(x_pos, y_pos)),
                    Node(pya.DPoint(x_pos + 400, y_pos)),
                ],
                a=center,
                b=gap,
                margin=100,
                inst_name=name,
            )
            produce_label(
                self.cell,
                f"{center * 1e3:.0f} {gap * 1e3:.0f}",
                self.refpoints[f"{name}_port_a"],
                origin=LabelOrigin.BOTTOMLEFT,
                layers=[self.face()["base_metal_gap_wo_grid"]],
                size=50,
                origin_offset=gap * 2,
                margin=10,
                layer_protection=self.face()["ground_grid_avoidance"],
            )

    def _produce_readout_hangers(self, positions, ground_widths):

        for i, pos in enumerate(positions):
            x_pos = pos.x
            y_pos = pos.y
            clength = 300

            trans = pya.DTrans(0, True, x_pos + -1 * clength / 2, y_pos)

            name = f"HR_{i}"
            rlength = clength + 2 * pi * self.r / 2 + 150 * 2
            head = pi * self.r / 2 + 150

            self.insert_cell(
                HangerResonator,
                trans,
                name,
                coupling_length=clength,
                ground_width=ground_widths[i],
                head_length=head,
                res_b=self.b,
                res_a=self.a,
                resonator_length=rlength,
                margin=100,
            )
            self.insert_cell(
                WaveguideComposite,
                nodes=[
                    Node(self.refpoints[f"HR_{i}_port_b"]),
                    Node(self.refpoints[f"HR_{i}_port_b_corner"]),
                ],
            )
            self.insert_cell(
                WaveguideComposite,
                nodes=[
                    Node(self.refpoints[f"HR_{i}_port_a"]),
                    Node(self.refpoints[f"HR_{i}_port_a_corner"]),
                ],
            )
            produce_label(
                self.cell,
                f"{ground_widths[i] * 1e3:.0f} nm",
                self.refpoints[f"HR_{i}_port_resonator_a_corner"],
                origin=LabelOrigin.BOTTOMLEFT,
                layers=[self.face()["base_metal_gap_wo_grid"]],
                size=75,
                origin_offset=0,
                margin=10,
                layer_protection=self.face()["ground_grid_avoidance"],
            )

    def _smooth_capacitor_test(
        self, position, finger_control, finger_width, finger_gap
    ):
        name = f"SC_{finger_control:.2f}"
        self.insert_cell(
            SmoothCapacitor,
            trans=pya.DTrans(0, True, position.x, position.y),
            inst_name=name,
            finger_control=finger_control,
            finger_width=finger_width,
            finger_gap=finger_gap,
            ground_gap=8,
            margin=50,
        )
        produce_label(
            self.cell,
            f"{finger_width * 1e3:.0f} {finger_gap * 1e3:.0f}",
            self.refpoints[f"{name}_port_a"] + pya.DPoint(0, 200),
            origin=LabelOrigin.BOTTOMLEFT,
            layers=[self.face()["base_metal_gap_wo_grid"]],
            size=50,
            origin_offset=0,
            margin=10,
            layer_protection=self.face()["ground_grid_avoidance"],
        )

    def _jj_tests(self, position, finger_width):
        jj_params = {
            "hook_thickness": 0.1,
            "hook_undercut": 0.5,
            "hook_lead_thickness": 0.2,
            "bridge_gap": 0.150,
            "junction_type": "Overlap2",
            "noSQUID": True,
        }

        self.insert_cell(
            TaperedJJTestPads,
            pya.DTrans(0, False, position.x, position.y),
            f"tjj_{finger_width:.2f}",
            pad_grid=[1, 5],
            pad_size=200,
            finger_width=finger_width,
            **jj_params,
        )

        produce_label(
            self.cell,
            f"{finger_width * 1e3:.0f} nm",
            position + pya.DPoint(0, 350),
            origin=LabelOrigin.BOTTOMLEFT,
            layers=[self.face()["base_metal_gap_wo_grid"]],
            size=75,
            origin_offset=0,
            margin=10,
            layer_protection=self.face()["ground_grid_avoidance"],
        )

    def build(self):

        hanger_grid = np.array(
            [
                [pya.DPoint(1500 + i * 800, 4800 + j * 500) for i in range(5)]
                for j in range(4)
            ]
        ).flatten()
        ground_widths = np.linspace(1, 4.8, 20)

        self._produce_readout_hangers(hanger_grid, ground_widths.tolist())

        centers = np.array([[7, 7.5, 8, 8.5, 9] for _ in range(5)]).flatten()
        gaps = np.array([[3, 3.5, 4, 4.5, 5] for _ in range(5)]).transpose().flatten()

        self._produce_cpw_tests(
            np.array(
                [
                    [pya.DPoint(1000 + i * 800, 3500 + j * 200) for i in range(5)]
                    for j in range(5)
                ]
            ).flatten(),
            centers=centers,
            gaps=gaps,
        )

        centers = np.array([[7, 7.5, 8, 8.5, 9] for _ in range(5)]).flatten()
        gaps = np.array([[3, 3.5, 4, 4.5, 5] for _ in range(5)]).transpose().flatten()

        for i in range(5):
            for j in range(5):
                self._smooth_capacitor_test(
                    position=pya.DPoint(1000 + i * 500, 1000 + j * 500),
                    finger_control=12,
                    finger_width=centers[i + j * 5],
                    finger_gap=gaps[i + j * 5],
                )

        load_libraries(path=TestStructure.LIBRARY_PATH)
        load_libraries(path=Element.LIBRARY_PATH)

        resolution = self.layout.create_cell(
            "ResolutionTestStructure_NB", TestStructure.LIBRARY_NAME
        )
        self.insert_cell(
            resolution,
            pya.DTrans(0, False, 6890, 875),
            "res",
        )
        self.insert_cell(
            resolution,
            pya.DTrans(1, False, 6890, 1300),
            "res1",
        )
        self.insert_cell(Profilometer, pya.DTrans(0, False, 6500, 1000), "pro")

        qubit_finger_spread = [100, 120, 152, 180, 200]

        for i, finger_width in enumerate(qubit_finger_spread):
            self._jj_tests(pya.DPoint(4500 + 1300, 2000 + i * 800), finger_width / 1000)

        ground_avoid = pya.Region(
            pya.DBox(pya.DPoint(0, 0), pya.DPoint(7600, 7600)).to_itype(self.layout.dbu)
        )
        self.cell.shapes(self.get_layer("ground_grid_avoidance")).insert(ground_avoid)
