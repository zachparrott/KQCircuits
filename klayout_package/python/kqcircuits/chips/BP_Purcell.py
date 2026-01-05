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
from kqcircuits.pya_resolver import pya
from kqcircuits.elements.element import Element
from kqcircuits.chips.chip import Chip
from kqcircuits.elements.chip_frame import ChipFrame
from kqcircuits.util.parameters import Param, pdt, add_parameters_from, add_parameter
from kqcircuits.elements.launcher import Launcher
from kqcircuits.elements.waveguide_coplanar import WaveguideCoplanar
from kqcircuits.elements.waveguide_composite import WaveguideComposite, Node
from kqcircuits.elements.hanger_resonator import HangerResonator
from kqcircuits.elements.meander import Meander

from kqcircuits.util.refpoints import WaveguideToSimPort

from kqcircuits.qubits.double_pads import DoublePads
from kqcircuits.qubits.double_pads_round import DoublePadsRound
from kqcircuits.qubits.finger_pads_jj import FingerPadsJJ

from kqcircuits.elements.smooth_capacitor import SmoothCapacitor


@add_parameters_from(Element, b=4, a=8, margin=100)
@add_parameters_from(ChipFrame, box=pya.DBox(pya.DPoint(0, 0), pya.DPoint(7500, 7500)))
# no flip chip alignment markers
@add_parameters_from(ChipFrame, marker_types=["", "", "", ""])
@add_parameters_from(
    Chip,
    face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(7500, 7500))],
    frames_dice_width=["50"],
    name_brand="NIST",
    name_chip="",
    name_copy="",
)
class PurcellQubits(Chip):
    # parameters accessible in PCell
    filter_only = Param(pdt.TypeBoolean, "Exclude qubits and resonators.", False)
    a_launcher = Param(pdt.TypeDouble, "Pad CPW trace center", 200, unit="μm")
    b_launcher = Param(pdt.TypeDouble, "Pad CPW trace gap", 153, unit="μm")
    launcher_width = Param(pdt.TypeDouble, "Pad extent", 250, unit="μm")
    taper_length = Param(pdt.TypeDouble, "Tapering length", 200, unit="μm")
    launcher_frame_gap = Param(pdt.TypeDouble, "Gap at chip frame", 100, unit="μm")
    launcher_indent = Param(pdt.TypeDouble, "Chip edge to pad port", 700, unit="μm")

    inputCapControl = Param(pdt.TypeDouble, "Input smooth capacitor finger control.", 6.39)
    outputCapControl = Param(pdt.TypeDouble, "Output smooth capacitor finger control.", 12.29)

    filter_length = Param(pdt.TypeDouble, "CPW t-line half wavelength for filter resonator.", 8655, unit="μm")
    center_length = Param(pdt.TypeDouble, "Center to center spacing of capacitors.", 4700, unit="μm")

    lengthIN = Param(pdt.TypeDouble, "Length compensation for input capacitance.", 786, unit="μm")
    lengthOUT = Param(pdt.TypeDouble, "Length compensation for output capacitance.", 1770, unit="μm")

    lockout_length = Param(pdt.TypeDouble, "Exclusion region on x-axis for start of meanders.", 4000, unit="μm")

    filter_positions = Param(
        pdt.TypeList, "Fractional position of resonators along the bandpass resonator length.", [0.3, 0.433, 0.566, 0.7]
    )
    resonator_lengths = Param(pdt.TypeList, "Readout resonators length in um.", [9000, 9000, 9000, 8000])
    resonator_couplings = Param(pdt.TypeList, "Readout coupling length in um.", [100, 340, 340, 200])

    qubit_loading = Param(pdt.TypeList, "Resonator length to subtract on qubit loaded side in um.", [0, 0, 0, 0])

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

        return 3750 - self.filter_length / 2 + position * self.filter_length

    def _produce_readout_hangers(self):

        for i, pos in enumerate(self.filter_positions):

            x_pos = self._compute_hanger_location(pos)

            clength = self.resonator_couplings[i]

            # alternate above and below of the feedline starting with down
            if i % 2:
                name_prefix = "HR_D"
                trans = pya.DTrans(2, True, x_pos + 1 * clength / 2, 3750)
            else:
                name_prefix = "HR_U"
                trans = pya.DTrans(0, True, x_pos + -1 * clength / 2, 3750)

            name = name_prefix + f"{int((i - i % 2)/2)}"
            rlength = clength + 2 * pi * self.r / 2 + 150 * 2
            head = pi * self.r / 2 + 150

            self.insert_cell(
                HangerResonator,
                trans,
                name,
                coupling_length=clength,
                ground_width=2,
                head_length=head,
                res_b=self.b,
                res_a=self.a,
                resonator_length=rlength,
            )

    def _compute_finger_locations(self, smooth_finger_width, smooth_finger_gap, smooth_ground_gap, finger_control):

        scale = smooth_finger_width + smooth_finger_gap
        x_max = max(finger_control, 1.0 / finger_control) * scale - smooth_finger_gap / 2

        xport = x_max + smooth_ground_gap + smooth_finger_gap

        return 2 * xport

    def _readout_resonator_U(self, index, resonator_length, position, couple_length, qubit_load):
        # positioning split between the coupling sides
        rollLength = (1 - position) * resonator_length

        # length of hanger structure. clength + 2x (turn radius + 150um verticals)
        hangerLength = couple_length + 2 * pi * self.r / 2 + 150 * 2

        # subtract half of the hangerLength from both sides
        leftLength = resonator_length - rollLength - 0.5 * hangerLength
        rightLength = rollLength - 0.5 * hangerLength - qubit_load

        # fixed lengths left: 50 vert + 200 horz - 2 * turn radii on the bottom side
        # left top side: 100 vert, + 300 horz - turn radius
        # 150 is an unknown compensation
        leftFixed = 50 + 200 + 50 - 2 * self.r * (1 - pi / 2) + 100 + 300 - self.r * (1 - pi / 2) - 150

        # fixed lengths right: 50 vert + 200 horz - 2 * turn radii on the bottom side
        # top side right: 100 vert + clength/2 + 200 horz - 1* turn_radius
        # top side right contd: - 1*turn_radius + y position of qubit
        # 200 is an unknonw compensation
        rightFixed = 50 + 200 + 50 - 2 * self.r * (1 - pi / 2) - 200
        qubitVjog = self.refpoints[f"Q_U{index}_port_cplr"].y - (
            self.refpoints[f"HR_U{index}_port_resonator_b_corner"].y + 1100
        )

        # 355 comes from current 20um qubt half ground plane dimension, to be noted when changed later
        # qubitVjog = 5700 - 355 - (self.refpoints[f"HR_U{index}_port_resonator_b_corner"].y + 1100)
        print(qubitVjog)

        rightFixed += qubitVjog - 2 * self.r * (1 - pi / 2) + 100 + (couple_length / 2 + 200 + self.r)

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
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].y + 1000,
                ),
                length_before=leftLength - leftFixed,
                ab_across=True,
            ),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].x - 200,
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].y + 1100,
                ),
            ),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].x - 500,
                    self.refpoints[f"HR_U{index}_port_resonator_a_corner"].y + 1100,
                ),
            ),
        ]

        self.insert_cell(
            WaveguideComposite,
            nodes=leftNodes,
            term2=15,
        )

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
                    self.refpoints[f"HR_U{index}_port_resonator_b_corner"].y + 1000,
                ),
                length_before=rightLength - rightFixed,
                ab_across=True,
            ),
            Node(
                (
                    self.refpoints[f"HR_U{index}_port_resonator_b_corner"].x + 200,
                    self.refpoints[f"HR_U{index}_port_resonator_b_corner"].y + 1100,
                ),
            ),
            Node(
                (
                    self.refpoints[f"Q_U{index}_port_cplr_corner"].x,
                    self.refpoints[f"HR_U{index}_port_resonator_b_corner"].y + 1100,
                ),
            ),
            Node(self.refpoints[f"Q_U{index}_port_cplr_corner"], ab_across=True),
            Node(self.refpoints[f"Q_U{index}_port_cplr"]),
        ]

        self.insert_cell(
            WaveguideComposite,
            nodes=rightNodes,
            # term2=15,
        )

    def _readout_resonator_D(self, index, resonator_length, position, couple_length, qubit_load):
        # positioning split between the coupling sides
        rollLength = (1 - position) * resonator_length

        # length of hanger structure. clength + 2x (turn radius + 150um verticals)
        hangerLength = couple_length + 2 * pi * self.r / 2 + 150 * 2

        # subtract half of the hangerLength from both sides
        leftLength = resonator_length - rollLength - 0.5 * hangerLength
        rightLength = rollLength - 0.5 * hangerLength - qubit_load

        # fixed lengths left: 50 vert + 200 horz - 2 * turn radii on the bottom side
        # left top side: 100 vert, + 300 horz - turn radius
        # 150 is an unknown compensation
        leftFixed = 50 + 200 + 50 - 2 * self.r * (1 - pi / 2) + 100 + 300 - self.r * (1 - pi / 2) - 150

        # fixed lengths right: 50 vert + 200 horz - 2 * turn radii on the bottom side
        # top side right: 100 vert + clength/2 + 200 horz - 1* turn_radius
        # top side right contd: - 1*turn_radius + y position of qubit
        # 200 is an unknonw compensation
        rightFixed = 50 + 200 + 50 - 2 * self.r * (1 - pi / 2) - 200
        qubitVjog = -1 * (
            self.refpoints[f"Q_D{index}_port_cplr"].y
            - (self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y - 1100)
        )

        rightFixed += qubitVjog - 2 * self.r * (1 - pi / 2) + 100 + (couple_length / 2 + 200 + self.r)

        # left composite non qubit side
        self.insert_cell(
            WaveguideComposite,
            nodes=[
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
                        self.refpoints[f"HR_D{index}_port_resonator_b_corner"].y - 1000,
                    ),
                    length_before=leftLength - leftFixed,
                    meander_direction=-1,
                    ab_across=True,
                ),
                Node(
                    (
                        self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 200,
                        self.refpoints[f"HR_D{index}_port_resonator_b_corner"].y - 1100,
                    ),
                ),
                Node(
                    (
                        self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 500,
                        self.refpoints[f"HR_D{index}_port_resonator_b_corner"].y - 1100,
                    ),
                ),
            ],
            term2=15,
        )

        # right qubit side composite
        self.insert_cell(
            WaveguideComposite,
            nodes=[
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
                        self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y - 1000,
                    ),
                    length_before=rightLength - rightFixed,
                    meander_direction=-1,
                    ab_across=True,
                ),
                Node(
                    (
                        self.refpoints[f"HR_D{index}_port_resonator_a_corner"].x + 200,
                        self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y - 1100,
                    ),
                ),
                Node(
                    (
                        self.refpoints[f"Q_D{index}_port_cplr_corner"].x,
                        self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y - 1100,
                    ),
                ),
                Node(self.refpoints[f"Q_D{index}_port_cplr_corner"], ab_across=True),
                Node(self.refpoints[f"Q_D{index}_port_cplr"]),
            ],
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

        # Cin, Cin_refp = self.create_with_refpoints(self.layout, SmoothCapacitor, inst_name="Cin", finger_control=5)
        Cin = self.add_element(
            SmoothCapacitor,
            inst_name="Cin",
            finger_control=self.inputCapControl,
            finger_width=8,
            finger_gap=4,
            ground_gap=8,
        )
        Cout = self.add_element(
            SmoothCapacitor,
            inst_name="Cout",
            finger_control=self.outputCapControl,
            finger_width=8,
            finger_gap=4,
            ground_gap=8,
        )

        # raise ValueError(f"{Cin_refp.keys()}")

        # the smooth capacitors generate their own dimensions based on the finger_control
        Cin_length = self._compute_finger_locations(
            smooth_finger_width=8, smooth_finger_gap=4, smooth_ground_gap=4, finger_control=self.inputCapControl
        )
        Cin_x = 3750 - self.center_length / 2

        self.insert_cell(Cin, pya.DTrans(0, True, Cin_x - 0.5 * Cin_length, 3750), inst_name="Cin")

        Cout_length = self._compute_finger_locations(
            smooth_finger_width=8, smooth_finger_gap=4, smooth_ground_gap=4, finger_control=self.outputCapControl
        )
        Cout_x = 3750 + self.center_length / 2

        self.insert_cell(Cout, pya.DTrans(0, True, Cout_x + 0.5 * Cout_length, 3750), inst_name="Cout")

        self.insert_cell(
            WaveguideComposite,
            nodes=[Node(self.refpoints["W_port"]), Node(self.refpoints["Cin_port_a"], n_bridges=1)],
        )

        self.insert_cell(
            WaveguideComposite,
            nodes=[Node(self.refpoints["E_port"]), Node(self.refpoints["Cout_port_b"], n_bridges=1)],
        )

        # 50 um is the port distance from the capacitor
        meander_lengthIN = self.filter_length / 2 - self.lockout_length / 2 - self.lengthIN - 50
        meander_lengthOUT = self.filter_length / 2 - self.lockout_length / 2 - self.lengthOUT - 50

        self.insert_cell(
            WaveguideComposite,
            nodes=[
                Node(self.refpoints["Cin_port_b_corner"]),
                Node(
                    pya.DPoint(3750 + -1 * self.lockout_length / 2, 3750),
                    length_before=meander_lengthIN,
                    meander_direction=1,
                    n_bridges=1,
                ),
            ],
            inst_name="Meander_Cin",
        )
        self.insert_cell(
            WaveguideComposite, nodes=[Node(self.refpoints["Cin_port_b_corner"]), Node(self.refpoints["Cin_port_b"], n_bridges=0)]
        )

        self.insert_cell(
            WaveguideComposite,
            nodes=[
                Node(self.refpoints["Cout_port_a_corner"]),
                Node(
                    pya.DPoint(3750 + 1 * self.lockout_length / 2, 3750),
                    length_before=meander_lengthOUT,
                    meander_direction=1,
                    n_bridges=1,
                ),
            ],
            inst_name="Meander_Cout",
        )

        self.insert_cell(
            WaveguideCoplanar, path=pya.DPath([self.refpoints["Cout_port_a_corner"], self.refpoints["Cout_port_a"]], 0)
        )

        if not self.filter_only:
            self._produce_readout_hangers()

            left_ref_names = ["Meander_Cin_port_b"]
            right_ref_names = []

            # prob error for 0 length
            if len(self.filter_positions) < 2:
                left_ref_names.append(f"HR_U0_port_b")
                right_ref_names.append(f"HR_U0_port_a")
                right_ref_names.append("Meander_Cout_port_b")

            else:
                for i in range(len(self.filter_positions) - 0):
                    if i % 2:
                        left_ref_names.append(f"HR_D{int(i/2)}_port_a")
                        right_ref_names.append(f"HR_D{int(i/2)}_port_b")
                    else:
                        right_ref_names.append(f"HR_U{int(i/2)}_port_a")
                        left_ref_names.append(f"HR_U{int(i/2)}_port_b")

                right_ref_names.append("Meander_Cout_port_b")

            for i in range(len(left_ref_names)):
                self.insert_cell(
                    WaveguideComposite,
                    nodes=[
                        Node(self.refpoints[left_ref_names[i]]),
                        Node(self.refpoints[right_ref_names[i]], n_bridges=1),
                    ],
                    inst_name=f"cpw_section_{i}",
                )

            # qubit positioning coordinates
            U_coords = []
            D_coords = []

            for i, pos in enumerate(self.filter_positions):
                if i % 2:
                    # top row positioning
                    D_coords.append(pya.DTrans(0, False, self._compute_hanger_location(pos) + 0 * 500, 1800))
                else:
                    # bottom row positioning
                    U_coords.append(pya.DTrans(2, False, self._compute_hanger_location(pos) + 0 * 500, 5700))

            # Qubit U3: 20 um gap "MOD D" participation. done
            try:
                self.insert_cell(
                    DoublePads,
                    U_coords[0],
                    f"Q_U0",
                    ground_gap=["1200", "710"],
                    ground_gap_r=0.0,
                    coupler_extent=["209", "20"],
                    coupler_r=0.0,
                    coupler_offset=50.0,
                    island1_extent=["752", "120"],
                    island1_r=0.0,
                    island2_extent=["752", "120"],
                    island2_r=0.0,
                    drive_position=["-450", "0"],
                    island_island_gap=20.0,
                    _parameters='{"junction_type": "Sim"}',
                    with_squid=False,
                    island1_taper_width=0,
                    island1_taper_junction_width=0,
                    island2_taper_width=0,
                    island2_taper_junction_width=0,
                )
            except IndexError:
                print("Qubit index not requested based on resonator length array.")

            try:
                self.insert_cell(
                    DoublePads,
                    U_coords[1],
                    f"Q_U1",
                    ground_gap=["1200", "710"],
                    ground_gap_r=0.0,
                    coupler_extent=["209", "20"],
                    coupler_r=0.0,
                    coupler_offset=50.0,
                    island1_extent=["752", "120"],
                    island1_r=0.0,
                    island2_extent=["752", "120"],
                    island2_r=0.0,
                    drive_position=["-450", "0"],
                    island_island_gap=20.0,
                    _parameters='{"junction_type": "Sim"}',
                    with_squid=False,
                    island1_taper_width=0,
                    island1_taper_junction_width=0,
                    island2_taper_width=0,
                    island2_taper_junction_width=0,
                )
            except IndexError:
                print("Qubit index not requested based on resonator length array.")

            try:
                self.insert_cell(
                    DoublePads,
                    D_coords[0],
                    f"Q_D0",
                    ground_gap=["1200", "710"],
                    ground_gap_r=0.0,
                    coupler_extent=["209", "20"],
                    coupler_r=0.0,
                    coupler_offset=50.0,
                    island1_extent=["752", "120"],
                    island1_r=0.0,
                    island2_extent=["752", "120"],
                    island2_r=0.0,
                    drive_position=["-450", "0"],
                    island_island_gap=20.0,
                    _parameters='{"junction_type": "Sim"}',
                    with_squid=False,
                    island1_taper_width=0,
                    island1_taper_junction_width=0,
                    island2_taper_width=0,
                    island2_taper_junction_width=0,
                )
            except IndexError:
                print("Qubit index not requested based on resonator length array.")

            try:
                self.insert_cell(
                    DoublePads,
                    D_coords[1],
                    f"Q_D1",
                    ground_gap=["1200", "710"],
                    ground_gap_r=0.0,
                    coupler_extent=["209", "20"],
                    coupler_r=0.0,
                    coupler_offset=50.0,
                    island1_extent=["752", "120"],
                    island1_r=0.0,
                    island2_extent=["752", "120"],
                    island2_r=0.0,
                    drive_position=["-450", "0"],
                    island_island_gap=20.0,
                    _parameters='{"junction_type": "Sim"}',
                    with_squid=False,
                    island1_taper_width=0,
                    island1_taper_junction_width=0,
                    island2_taper_width=0,
                    island2_taper_junction_width=0,
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
                    )
                else:
                    self._readout_resonator_U(
                        index=int(i / 2),
                        resonator_length=self.resonator_lengths[i],
                        position=pos,
                        couple_length=self.resonator_couplings[i],
                        qubit_load=self.qubit_loading[i],
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
