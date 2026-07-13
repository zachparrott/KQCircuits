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
from kqcircuits.junctions.overlap_junction2 import Overlap2
from kqcircuits.pya_resolver import pya
from kqcircuits.elements.element import Element
from kqcircuits.chips.chip import Chip
from kqcircuits.elements.chip_frame import ChipFrame
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
@add_parameters_from(Overlap2, "*", "r")  # , "finger_width")
class PurcellQubitsIDC(Chip):
    # parameters accessible in PCell
    filter_only = Param(pdt.TypeBoolean, "Exclude qubits and resonators.", False)
    a_launcher = Param(pdt.TypeDouble, "Pad CPW trace center", 200, unit="μm")
    b_launcher = Param(pdt.TypeDouble, "Pad CPW trace gap", 153, unit="μm")
    launcher_width = Param(pdt.TypeDouble, "Pad extent", 250, unit="μm")
    taper_length = Param(pdt.TypeDouble, "Tapering length", 200, unit="μm")
    launcher_frame_gap = Param(pdt.TypeDouble, "Gap at chip frame", 100, unit="μm")
    launcher_indent = Param(pdt.TypeDouble, "Chip edge to pad port", 700, unit="μm")

    inputCapControl = Param(
        pdt.TypeDouble, "Input smooth capacitor finger control.", 6.39
    )
    outputCapControl = Param(
        pdt.TypeDouble, "Output smooth capacitor finger control.", 12.29
    )

    filter_length = Param(
        pdt.TypeDouble,
        "CPW t-line half wavelength for filter resonator.",
        8655,
        unit="μm",
    )
    center_length = Param(
        pdt.TypeDouble, "Center to center spacing of capacitors.", 4700, unit="μm"
    )

    lengthIN = Param(
        pdt.TypeDouble, "Length compensation for input caxpacitance.", 786, unit="μm"
    )
    lengthOUT = Param(
        pdt.TypeDouble, "Length compensation for output capacitance.", 1770, unit="μm"
    )

    lockout_length = Param(
        pdt.TypeDouble,
        "Exclusion region on x-axis for start of meanders.",
        4200,
        unit="μm",
    )

    grid_margin = Param(
        pdt.TypeDouble,
        "Margin from element edge to start of ground grid.",
        20,
        unit="μm",
    )

    qubit_cplr_y_spacing = Param(
        pdt.TypeList,
        "Offset of qubit coupler corner from chip centerline for each qubit.",
        [1200, 1200, 1200, 1200],
        unit="μm",
    )

    readout_spine_extra = Param(
        pdt.TypeDouble,
        "Extra offset from qubit coupler corner to readout spine.",
        100,
        unit="μm",
    )

    filter_positions = Param(
        pdt.TypeList,
        "Fractional position of resonators along the bandpass resonator length.",
        [0.35, 0.45, 0.55, 0.65],
    )
    resonator_lengths = Param(
        pdt.TypeList, "Readout resonators length in um.", [8670, 8580, 8490, 8400]
    )
    resonator_couplings = Param(
        pdt.TypeList, "Readout coupling length in um.", [322, 332, 319, 326]
    )
    hanger_ground_width = Param(
        pdt.TypeDouble, "Ground width between CPWs.", 2, unit="μm"
    )

    # loadings = []
    # for a,l in zip([10.42, 11.12, 11.87, 12.63], [8670, 8580, 8490, 8400]):
    #    loadings.append(a / 180 * l)
    qubit_loading = Param(
        pdt.TypeList,
        "Resonator length to subtract on qubit loaded side in um.",
        [501.90, 530.05, 559.87, 589.40],
    )

    labels = Param(
        pdt.TypeBoolean, "Whether to produce labels and test structures.", True
    )

    # radius
    r = 50

    def produce_two_launchers(
        self,
        a_launcher,
        b_launcher,
        launcher_width,
        taper_length,
        launcher_frame_gap,
        launcher_indent,
        pad_pitch,
        launcher_assignments=None,
        enabled=None,
        chip_box=None,
        face_id=0,
    ):

        launcher_cell = self.add_element(
            Launcher,
            s=launcher_width,
            l=taper_length,
            a_launcher=a_launcher,
            b_launcher=b_launcher,
            launcher_frame_gap=launcher_frame_gap,
            face_ids=[self.face_ids[face_id]],
        )

        pads_per_side = [0, 1, 0, 1]

        dirs = (90, 0, -90, 180)
        trans = (
            pya.DTrans(3, 0, self.box.p1.x, self.box.p2.y),
            pya.DTrans(2, 0, self.box.p2.x, self.box.p2.y),
            pya.DTrans(1, 0, self.box.p2.x, self.box.p1.y),
            pya.DTrans(0, 0, self.box.p1.x, self.box.p1.y),
        )
        _w = self.box.p2.x - self.box.p1.x
        _h = self.box.p2.y - self.box.p1.y
        sides = [_w, _h, _w, _h]

        return self._insert_launchers(
            dirs,
            enabled,
            launcher_assignments,
            None,
            launcher_cell,
            launcher_indent,
            launcher_width,
            pad_pitch,
            pads_per_side,
            sides,
            trans,
            face_id=0,
        )

    def _compute_hanger_location(self, position):

        return 3800 - self.filter_length / 2 + position * self.filter_length

    def _qubit_align_refpoint_name(self, qubit_refpoints):
        if "port_cplr_corner" in qubit_refpoints:
            return "port_cplr_corner"
        if "port_cplr" in qubit_refpoints:
            return "port_cplr"
        raise ValueError("Qubit must define a port_cplr refpoint.")

    def _qubit_coupler_ref_name(self, inst_prefix):
        corner = f"{inst_prefix}_port_cplr_corner"
        if corner in self.refpoints:
            return corner
        return f"{inst_prefix}_port_cplr"

    def _readout_spine_y(self, side, base_y, qubit_index):
        sign = 1 if side == "U" else -1
        spine_y = base_y + sign * (
            self.qubit_cplr_y_spacing[qubit_index] - self.readout_spine_extra
        )
        return spine_y

    def _readout_base_y(self, side, index):
        return self.refpoints[f"HR_{side}{index}_port_b_corner"].y

    def _qubit_target_point(self, side, index, position, qubit_index=None):
        if qubit_index is None:
            # Default: map side + index to global qubit index (left-to-right: U0=0, D0=1, U1=2, D1=3)
            qubit_index = 2 * index + (1 if side == "D" else 0)
        base_y = self._readout_base_y(side, index)
        sign = 1 if side == "U" else -1
        target_y = base_y + sign * self.qubit_cplr_y_spacing[qubit_index]
        target_x = self._compute_hanger_location(position)
        return pya.DPoint(target_x, target_y)

    def _qubit_approach_nodes(self, side, index, spine_y):
        inst_prefix = f"Q_{side}{index}"
        corner_name = self._qubit_coupler_ref_name(inst_prefix)
        corner = self.refpoints[corner_name]
        port = self.refpoints[f"{inst_prefix}_port_cplr"]
        nodes = []
        if abs(spine_y - corner.y) > 1e-6:
            nodes.append(Node((corner.x, spine_y)))
        nodes.append(Node(corner, ab_across=True))
        nodes.append(Node(port))
        return nodes

    def _produce_readout_hangers(self):

        for i, pos in enumerate(self.filter_positions):
            x_pos = self._compute_hanger_location(pos)

            clength = self.resonator_couplings[i]

            # alternate above and below of the feedline starting with down
            if i % 2:
                name_prefix = "HR_D"
                trans = pya.DTrans(2, True, x_pos + 1 * clength / 2, 3800)
            else:
                name_prefix = "HR_U"
                trans = pya.DTrans(0, True, x_pos + -1 * clength / 2, 3800)

            name = name_prefix + f"{int((i - i % 2) / 2)}"
            rlength = clength + 2 * pi * self.r / 2 + 150 * 2
            head = pi * self.r / 2 + 150

            self.insert_cell(
                HangerResonator,
                trans,
                name,
                coupling_length=clength,
                ground_width=self.hanger_ground_width,
                head_length=head,
                res_b=self.b,
                res_a=self.a,
                resonator_length=rlength,
                margin=self.grid_margin,
            )

    def _compute_finger_locations(
        self, smooth_finger_width, smooth_finger_gap, smooth_ground_gap, finger_control
    ):

        scale = smooth_finger_width + smooth_finger_gap
        x_max = (
            max(finger_control, 1.0 / finger_control) * scale - smooth_finger_gap / 2
        )

        xport = x_max + smooth_ground_gap + smooth_finger_gap

        return 2 * xport

    def _readout_resonator_U(
        self,
        index,
        resonator_length,
        position,
        couple_length,
        qubit_load,
        qubit_index=None,
    ):
        # positioning split between the coupling sides
        if position < 0.5:
            # rollLength = balance_correct * (1 - position) * resonator_length
            # translated from AWR wrong
            rollLength = position * resonator_length
        else:
            # rollLength = (2 - balance_correct) * (1 - position) * resonator_length
            rollLength = position * resonator_length

        # length of hanger structure. clength + 2x (turn radius + 150um verticals)
        hangerLength = couple_length + 2 * pi * self.r / 2 + 150 * 2

        # subtract half of the hangerLength from both sides
        leftLength = resonator_length - rollLength - 0.5 * hangerLength
        rightLength = rollLength - 0.5 * hangerLength - qubit_load

        # fixed lengths left: 50 vert + 200 horz - 2 * turn radii on the bottom side
        # left top side: 100 vert, + 300 horz - turn radius
        # 150 is an unknown compensation
        leftFixed = (
            50
            + 200
            + 50
            - 2 * self.r * (1 - pi / 2)
            + 100
            + 300
            - self.r * (1 - pi / 2)
            - 150
        )

        # fixed lengths right: 50 vert + 200 horz - 2 * turn radii on the bottom side
        # top side right: 100 vert + clength/2 + 200 horz - 1* turn_radius
        # top side right contd: - 1*turn_radius + y position of qubit
        # 200 is an unknonw compensation
        rightFixed = 50 + 200 + 50 - 2 * self.r * (1 - pi / 2) - 1 * 200
        qubit_port = self.refpoints[f"Q_U{index}_port_cplr"]
        qubit_corner = self.refpoints[self._qubit_coupler_ref_name(f"Q_U{index}")]
        qubitVjog = qubit_port.y - qubit_corner.y

        rightFixed += (
            qubitVjog
            - 2 * self.r * (1 - pi / 2)
            + 100
            + (couple_length / 2 + 200 + self.r)
        )

        base_y = self._readout_base_y("U", index)
        spine_y = self._readout_spine_y("U", base_y, qubit_index)
        meander_y = spine_y - 2 * self.r

        # left composite
        leftNodes = [
            Node(
                self.refpoints[f"HR_U{index}_port_resonator_a"],
            ),
            Node(self.refpoints[f"HR_U{index}_port_resonator_a_corner"]),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].x - 200,
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].y,
                )
            ),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].x - 200,
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].y + 50,
                ),
                ab_across=True,
            ),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].x - 200,
                    meander_y,
                ),
                length_before=leftLength - leftFixed,
                ab_across=True,
            ),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].x - 200,
                    spine_y,
                ),
            ),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].x - 500,
                    spine_y,
                ),
            ),
        ]

        left_wc = self.add_element(
            WaveguideComposite,
            nodes=leftNodes,
            # open end
            term2=15,
            margin=self.grid_margin,
        )
        self.insert_cell(left_wc)

        # right composite
        rightNodes = [
            Node(
                self.refpoints[f"HR_U{index}_port_resonator_b"],
            ),
            Node(self.refpoints[f"HR_U{index}_port_resonator_b_corner"]),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_b_corner"].x + 200,
                    self.refpoints[f"HR_U{index}_port_resonator_b_corner"].y,
                ),
            ),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_b_corner"].x + 200,
                    self.refpoints[f"HR_U{index}_port_resonator_b_corner"].y + 50,
                ),
                ab_across=True,
            ),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_b_corner"].x + 200,
                    meander_y,
                ),
                length_before=rightLength - rightFixed,
                ab_across=True,
            ),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_b_corner"].x + 200,
                    spine_y,
                ),
            ),
            *self._qubit_approach_nodes("U", index, spine_y),
        ]

        right_wc = self.add_element(
            WaveguideComposite,
            nodes=rightNodes,
            margin=self.grid_margin,
        )
        self.insert_cell(right_wc)

        # debug lengths
        # produce_label(
        #     self.cell,
        #     # f"D{index} {leftLength:.0f} {sum(left_wc.segment_lengths()):.0f} {rightLength:.0f} {sum(right_wc.segment_lengths()):.0f} um = {hangerLength + (sum(left_wc.segment_lengths()) + sum(right_wc.segment_lengths())):.0f}",
        #     f"U{index} {(resonator_length - hangerLength):.0f} {(leftLength + rightLength):.0f} {(sum(left_wc.segment_lengths()) + sum(right_wc.segment_lengths())):.0f} um",
        #     pya.DPoint(-400, -index * 300 - 400 - 1200),
        #     LabelOrigin.BOTTOMRIGHT,
        #     0,
        #     10,
        #     [self.face()["base_metal_gap_wo_grid"]],
        #     self.face()["ground_grid_avoidance"],
        #     200,
        # )

    def _readout_resonator_D(
        self,
        index,
        resonator_length,
        position,
        couple_length,
        qubit_load,
        qubit_index=None,
    ):
        # positioning split between the coupling sides
        if position < 0.5:
            rollLength = position * resonator_length
        else:
            rollLength = position * resonator_length

        # length of hanger structure. clength + 2x (turn radius + 150um verticals)
        hangerLength = couple_length + 2 * pi * self.r / 2 + 150 * 2

        # subtract half of the hangerLength from both sides
        leftLength = resonator_length - rollLength - 0.5 * hangerLength
        rightLength = rollLength - 0.5 * hangerLength - qubit_load

        # fixed lengths left: 50 vert + 200 horz - 2 * turn radii on the bottom side
        # left top side: 100 vert, + 300 horz - turn radius
        # 150 is an unknown compensation
        leftFixed = (
            50
            + 200
            + 50
            - 2 * self.r * (1 - pi / 2)
            + 100
            + 300
            - self.r * (1 - pi / 2)
            - 150
        )

        # fixed lengths right: 50 vert + 200 horz - 2 * turn radii on the bottom side
        # top side right: 100 vert + clength/2 + 200 horz - 1* turn_radius
        # top side right contd: - 1*turn_radius + y position of qubit
        # 200 is an unknonw compensation
        # zero*200 added on 7/8/2026 by ZLP in device 1 debug.
        rightFixed = 50 + 200 + 50 - 2 * self.r * (1 - pi / 2) - 1 * 200
        qubit_port = self.refpoints[f"Q_D{index}_port_cplr"]
        qubit_corner = self.refpoints[self._qubit_coupler_ref_name(f"Q_D{index}")]
        qubitVjog = qubit_port.y - qubit_corner.y

        rightFixed += (
            qubitVjog
            - 2 * self.r * (1 - pi / 2)
            + 100
            + (couple_length / 2 + 200 + self.r)
        )

        base_y = self._readout_base_y("D", index)
        spine_y = self._readout_spine_y("D", base_y, qubit_index)
        # point of blame
        # meander_y = spine_y + 2 * self.r
        meander_y = spine_y + 2 * self.r

        # left composite
        leftNodes = [
            Node(self.refpoints[f"HR_D{index}_port_resonator_b"]),
            Node(self.refpoints[f"HR_D{index}_port_resonator_b_corner"]),
            Node(
                (
                    self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 200,
                    self.refpoints[f"HR_D{index}_port_resonator_b_corner"].y,
                )
            ),
            Node(
                (
                    self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 200,
                    self.refpoints[f"HR_D{index}_port_resonator_b_corner"].y - 50,
                ),
                ab_across=True,
            ),
            Node(
                (
                    self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 200,
                    meander_y,
                ),
                length_before=leftLength - leftFixed,
                meander_direction=-1,
                ab_across=True,
            ),
            Node(
                (
                    self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 200,
                    spine_y,
                ),
            ),
            Node(
                (
                    self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 500,
                    spine_y,
                ),
            ),
        ]

        left_wc = self.add_element(
            WaveguideComposite,
            nodes=leftNodes,
            # open end
            term2=15,
            margin=self.grid_margin,
        )
        self.insert_cell(left_wc)

        # right composite
        rightNodes = [
            Node(self.refpoints[f"HR_D{index}_port_resonator_a"]),
            Node(self.refpoints[f"HR_D{index}_port_resonator_a_corner"]),
            Node(
                (
                    self.refpoints[f"HR_D{index}_port_resonator_a_corner"].x + 200,
                    self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y,
                )
            ),
            Node(
                (
                    self.refpoints[f"HR_D{index}_port_resonator_a_corner"].x + 200,
                    self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y - 50,
                ),
                ab_across=True,
            ),
            Node(
                (
                    self.refpoints[f"HR_D{index}_port_resonator_a_corner"].x + 200,
                    meander_y,
                ),
                length_before=rightLength - rightFixed,
                meander_direction=-1,
                ab_across=True,
            ),
            Node(
                (
                    self.refpoints[f"HR_D{index}_port_resonator_a_corner"].x + 200,
                    spine_y,
                ),
            ),
            *self._qubit_approach_nodes("D", index, spine_y),
        ]

        right_wc = self.add_element(
            WaveguideComposite,
            nodes=rightNodes,
            margin=self.grid_margin,
        )
        self.insert_cell(right_wc)

        produce_label(
            self.cell,
            # f"D{index} {leftLength:.0f} {sum(left_wc.segment_lengths()):.0f} {rightLength:.0f} {sum(right_wc.segment_lengths()):.0f} um = {hangerLength + (sum(left_wc.segment_lengths()) + sum(right_wc.segment_lengths())):.0f}",
            f"D{index} {resonator_length - hangerLength:.0f} {(leftLength + rightLength):.0f} {(sum(left_wc.segment_lengths()) + sum(right_wc.segment_lengths())):.0f} um",
            pya.DPoint(-400, -index * 300 - 400),
            LabelOrigin.BOTTOMRIGHT,
            0,
            10,
            [self.face()["base_metal_gap_wo_grid"]],
            self.face()["ground_grid_avoidance"],
            200,
        )

    def build(self):
        self.launchers = self.produce_two_launchers(
            self.launcher_width,
            self.b_launcher,
            self.launcher_width,
            self.taper_length,
            self.launcher_frame_gap,
            self.launcher_indent,
            100,
            launcher_assignments={1: "E", 2: "W"},
        )

        Cin = self.add_element(
            SmoothCapacitor,
            inst_name="Cin",
            finger_control=self.inputCapControl,
            finger_width=8,
            finger_gap=4,
            ground_gap=8,
            margin=self.grid_margin,
        )
        Cout = self.add_element(
            SmoothCapacitor,
            inst_name="Cout",
            finger_control=self.outputCapControl,
            finger_width=8,
            finger_gap=4,
            ground_gap=8,
            margin=self.grid_margin,
        )

        # the smooth capacitors generate their own dimensions based on the finger_control
        Cin_length = self._compute_finger_locations(
            smooth_finger_width=8,
            smooth_finger_gap=4,
            smooth_ground_gap=4,
            finger_control=self.inputCapControl,
        )
        Cin_x = 3800 - self.center_length / 2

        self.insert_cell(
            Cin, pya.DTrans(0, True, Cin_x - 0.5 * Cin_length, 3800), inst_name="Cin"
        )

        Cout_length = self._compute_finger_locations(
            smooth_finger_width=8,
            smooth_finger_gap=4,
            smooth_ground_gap=4,
            finger_control=self.outputCapControl,
        )
        Cout_x = 3800 + self.center_length / 2

        self.insert_cell(
            Cout,
            pya.DTrans(0, True, Cout_x + 0.5 * Cout_length, 3800),
            inst_name="Cout",
        )

        self.insert_cell(
            WaveguideComposite,
            nodes=[
                Node(self.refpoints["W_port"]),
                Node(self.refpoints["Cin_port_a"], n_bridges=1),
            ],
            margin=self.grid_margin,
        )

        self.insert_cell(
            WaveguideComposite,
            nodes=[
                Node(self.refpoints["E_port"]),
                Node(self.refpoints["Cout_port_b"], n_bridges=1),
            ],
            margin=self.grid_margin,
        )

        # 50 um is the port distance from the capacitor
        meander_lengthIN = (
            self.filter_length / 2 - self.lockout_length / 2 - self.lengthIN - 50
        )
        meander_lengthOUT = (
            self.filter_length / 2 - self.lockout_length / 2 - self.lengthOUT - 50
        )

        self.insert_cell(
            WaveguideComposite,
            nodes=[
                Node(self.refpoints["Cin_port_b_corner"]),
                Node(
                    pya.DPoint(3800 + -1 * self.lockout_length / 2, 3800),
                    length_before=meander_lengthIN,
                    meander_direction=-1,
                    n_bridges=1,
                ),
            ],
            inst_name="Meander_Cin",
            margin=self.grid_margin,
        )
        self.insert_cell(
            WaveguideComposite,
            nodes=[
                Node(self.refpoints["Cin_port_b_corner"]),
                Node(self.refpoints["Cin_port_b"], n_bridges=0),
            ],
            margin=self.grid_margin,
        )

        self.insert_cell(
            WaveguideComposite,
            nodes=[
                Node(self.refpoints["Cout_port_a_corner"]),
                Node(
                    pya.DPoint(3800 + 1 * self.lockout_length / 2, 3800),
                    length_before=meander_lengthOUT,
                    meander_direction=-1,
                    n_bridges=1,
                ),
            ],
            inst_name="Meander_Cout",
            margin=self.grid_margin,
        )

        self.insert_cell(
            WaveguideCoplanar,
            path=pya.DPath(
                [self.refpoints["Cout_port_a_corner"], self.refpoints["Cout_port_a"]], 0
            ),
            margin=self.grid_margin,
        )

        if not self.filter_only:
            self._produce_readout_hangers()

            left_ref_names = ["Meander_Cin_port_b"]
            right_ref_names = []

            # prob error for 0 length
            if len(self.filter_positions) < 2:
                left_ref_names.append("HR_U0_port_b")
                right_ref_names.append("HR_U0_port_a")
                right_ref_names.append("Meander_Cout_port_b")

            else:
                for i in range(len(self.filter_positions) - 0):
                    if i % 2:
                        left_ref_names.append(f"HR_D{int(i / 2)}_port_a")
                        right_ref_names.append(f"HR_D{int(i / 2)}_port_b")
                    else:
                        right_ref_names.append(f"HR_U{int(i / 2)}_port_a")
                        left_ref_names.append(f"HR_U{int(i / 2)}_port_b")

                right_ref_names.append("Meander_Cout_port_b")

            for i in range(len(left_ref_names)):
                self.insert_cell(
                    WaveguideComposite,
                    nodes=[
                        Node(self.refpoints[left_ref_names[i]]),
                        Node(self.refpoints[right_ref_names[i]], n_bridges=1),
                    ],
                    inst_name=f"cpw_section_{i}",
                    margin=self.grid_margin,
                )

            u_positions = [
                pos for i, pos in enumerate(self.filter_positions) if i % 2 == 0
            ]
            d_positions = [
                pos for i, pos in enumerate(self.filter_positions) if i % 2 == 1
            ]

            island2_widths = [843.7, 874.8, 903.6, 935.5]
            finger_lengths = [100.2, 124.4, 149.7, 177.0]

            common_params = {
                "ground_gap_r": 10,
                "coupler_a": 8,
                "coupler_r": 10,
                "island1_r": 10,
                "island2_r": 10,
                "island_island_gap": 70,
                "island1_taper_width": 50,
                "island1_taper_junction_width": 25,
                "island2_taper_width": 50,
                "island2_taper_junction_width": 25,
                "idc_finger_gap": 20,
                "idc_finger_width": 30,
                "idc_finger_number": 7,
                "coupler_extent": [350, 100],
                "ground_coupler_extend": 0,
                "drive_position": ["-450", "0"],
                "junction_type": "Overlap2",
                "base_metal_separation": 12,
                "with_squid": True,
                # sets the margin before ground grid
                "margin": self.grid_margin,
            }
            # Bridge the mask-level sweep parameters down to the Qubit SQUID
            common_params.update(
                {
                    "finger_width": self.finger_width,
                    "hook_thickness": self.hook_thickness,
                    "hook_undercut": self.hook_undercut,
                    "hook_lead_thickness": self.hook_lead_thickness,
                    "bridge_gap": self.bridge_gap,
                    "noSQUID": self.noSQUID,
                }
            )

            # Qubit U0 (global index 0)
            try:
                qubit_cell, qubit_ref = DoublePadsIDC.create_with_refpoints(
                    self.layout,
                    library=self.LIBRARY_NAME,
                    island1_extent=[island2_widths[0] - 400, 300],
                    island2_extent=[island2_widths[0], 500],
                    idc_finger_length=finger_lengths[0],
                    junction_rotate=True,
                    grid_pads=True,
                    **common_params,
                )
                align_ref = self._qubit_align_refpoint_name(qubit_ref)
                self.insert_cell(
                    qubit_cell,
                    trans=pya.DTrans(2, False, 0, 0),
                    inst_name="Q_U0",
                    align_to=self._qubit_target_point("U", 0, u_positions[0]),
                    align=align_ref,
                )
            except IndexError:
                print("Qubit index not requested based on resonator length array.")

            # Qubit U1 (global index 2)
            try:
                qubit_cell, qubit_ref = DoublePadsIDC.create_with_refpoints(
                    self.layout,
                    library=self.LIBRARY_NAME,
                    island1_extent=[island2_widths[2] - 400, 300],
                    island2_extent=[island2_widths[2], 500],
                    idc_finger_length=finger_lengths[2],
                    junction_rotate=True,
                    grid_pads=False,
                    **common_params,
                )
                align_ref = self._qubit_align_refpoint_name(qubit_ref)
                self.insert_cell(
                    qubit_cell,
                    trans=pya.DTrans(2, False, 0, 0),
                    inst_name="Q_U1",
                    align_to=self._qubit_target_point("U", 1, u_positions[1]),
                    align=align_ref,
                )
            except IndexError:
                print("Qubit index not requested based on resonator length array.")

            # Qubit D0 (global index 1)
            try:
                qubit_cell, qubit_ref = DoublePadsIDC.create_with_refpoints(
                    self.layout,
                    library=self.LIBRARY_NAME,
                    island1_extent=[island2_widths[1] - 400, 300],
                    island2_extent=[island2_widths[1], 500],
                    idc_finger_length=finger_lengths[1],
                    grid_pads=False,
                    **common_params,
                )
                align_ref = self._qubit_align_refpoint_name(qubit_ref)
                self.insert_cell(
                    qubit_cell,
                    trans=pya.DTrans(0, False, 0, 0),
                    inst_name="Q_D0",
                    align_to=self._qubit_target_point("D", 0, d_positions[0]),
                    align=align_ref,
                )
            except IndexError:
                print("Qubit index not requested based on resonator length array.")

            # Qubit D1 (global index 3)
            try:
                qubit_cell, qubit_ref = DoublePadsIDC.create_with_refpoints(
                    self.layout,
                    library=self.LIBRARY_NAME,
                    island1_extent=[island2_widths[3] - 400, 300],
                    island2_extent=[island2_widths[3], 500],
                    idc_finger_length=finger_lengths[3],
                    grid_pads=False,
                    **common_params,
                )
                align_ref = self._qubit_align_refpoint_name(qubit_ref)
                self.insert_cell(
                    qubit_cell,
                    trans=pya.DTrans(0, False, 0, 0),
                    inst_name="Q_D1",
                    align_to=self._qubit_target_point("D", 1, d_positions[1]),
                    align=align_ref,
                )
            except IndexError:
                print("Qubit index not requested based on resonator length array.")

            for i, pos in enumerate(self.filter_positions):
                if i % 2:
                    self._readout_resonator_D(
                        index=int(i / 2),
                        resonator_length=self.resonator_lengths[i],
                        position=pos,
                        couple_length=self.resonator_couplings[i],
                        qubit_load=self.qubit_loading[i],
                        qubit_index=i,
                    )
                else:
                    self._readout_resonator_U(
                        index=int(i / 2),
                        resonator_length=self.resonator_lengths[i],
                        position=pos,
                        couple_length=self.resonator_couplings[i],
                        qubit_load=self.qubit_loading[i],
                        qubit_index=i,
                    )

        else:
            left_ref_names = ["Meander_Cin_port_b"]
            right_ref_names = ["Meander_Cout_port_b"]

            self.insert_cell(
                WaveguideComposite,
                nodes=[
                    Node(self.refpoints[left_ref_names[0]]),
                    Node(
                        self.refpoints[right_ref_names[0]],
                        n_bridges=6,
                    ),
                ],
                a=8,
                b=4,
            )

        self.insert_cell(
            TaperedJJTestPads,
            pya.DTrans(0, False, 700, 1155),
            pad_grid=[1, 2],
            pad_size=200,
        )

        if self.labels:
            # load OAs
            load_libraries(path=TestStructure.LIBRARY_PATH)
            load_libraries(path=Element.LIBRARY_PATH)

            produce_label(
                self.cell,
                "IN",
                self.refpoints["W_port"] + pya.DPoint(-400, 400),
                LabelOrigin.BOTTOMLEFT,
                0,
                10,
                [self.face()["base_metal_gap_wo_grid"]],
                self.face()["ground_grid_avoidance"],
                200,
            )

            produce_label(
                self.cell,
                "OUT",
                self.refpoints["E_port"] + pya.DPoint(400, 400),
                LabelOrigin.BOTTOMRIGHT,
                0,
                10,
                [self.face()["base_metal_gap_wo_grid"]],
                self.face()["ground_grid_avoidance"],
                200,
            )

            NISTlogo = self.layout.create_cell("NISTlogo", Element.LIBRARY_NAME)

            # measured from crap GDS logo file/ 40 is letter line width
            scaleFactor = 60 / 158.016
            self.insert_cell(
                NISTlogo, pya.DCplxTrans(scaleFactor, 0, False, 6800, 6630), "logo"
            )

            AMPlogo2 = self.layout.create_cell("hbarAMP", Element.LIBRARY_NAME)
            scaleFactor = 10 / 0.529
            self.insert_cell(
                AMPlogo2, pya.DCplxTrans(scaleFactor, 0, False, 6840, 3100), "amp"
            )

            produce_label(
                self.cell,
                "Z Parrott",
                pya.DPoint(6720, 6300),
                LabelOrigin.BOTTOMLEFT,
                0,
                10,
                [self.face()["base_metal_gap_wo_grid"]],
                self.face()["ground_grid_avoidance"],
                75,
            )

            resolution = self.layout.create_cell(
                "ResolutionTestStructure_NB", TestStructure.LIBRARY_NAME
            )
            self.insert_cell(
                resolution,
                pya.DTrans(0, False, 6320 + 670 - 100, 4200 - 100 - 3425 + 200),
                "res",
            )

            produce_label(
                self.cell,
                f"{self.finger_width * 1e3:.0f} nm",
                pya.DPoint(420, 1560),
                LabelOrigin.BOTTOMLEFT,
                0,
                10,
                [self.face()["base_metal_gap_wo_grid"]],
                self.face()["ground_grid_avoidance"],
                57,
            )

            if self.grid_margin < 0:
                ground_avoid = pya.Region(
                    pya.DBox(pya.DPoint(0, 0), pya.DPoint(7600, 7600)).to_itype(
                        self.layout.dbu
                    )
                )
                self.cell.shapes(self.get_layer("ground_grid_avoidance")).insert(
                    ground_avoid
                )
