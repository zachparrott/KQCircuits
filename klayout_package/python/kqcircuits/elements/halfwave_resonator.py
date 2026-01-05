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

@add_parameters_from(Element, b = 4, a = 8, margin=100)

class HalfWaveResonator(Element):
    # parameters accessible in PCell
    filter_only = Param(pdt.TypeBoolean, "Exclude qubits and resonators.", False)
    a_launcher = Param(pdt.TypeDouble, "Pad CPW trace center", 200, unit="μm")
    b_launcher = Param(pdt.TypeDouble, "Pad CPW trace gap", 153, unit="μm")
    launcher_width = Param(pdt.TypeDouble, "Pad extent", 250, unit="μm")
    taper_length = Param(pdt.TypeDouble, "Tapering length", 200, unit="μm")
    launcher_frame_gap = Param(pdt.TypeDouble, "Gap at chip frame", 100, unit="μm") 
    launcher_indent = Param(pdt.TypeDouble, "Chip edge to pad port", 700, unit="μm") 

    inputCapControl = Param(pdt.TypeDouble, "Input smooth capacitor finger control.", 2.1)
    outputCapControl = Param(pdt.TypeDouble, "Output smooth capacitor finger control.", 2.1)

    filter_length = Param(pdt.TypeDouble, "CPW t-line half wavelength for filter resonator.", 9076, unit="μm") 
    center_length = Param(pdt.TypeDouble, "Center to center spacing of capacitors.", 5400, unit="μm") 

    lengthIN = Param(pdt.TypeDouble, "Length compensation for input capacitance.", 751, unit="μm")
    lengthOUT = Param(pdt.TypeDouble, "Length compensation for output capacitance.", 1472, unit="μm")

    lockout_length = 4600

    filter_positions = Param(pdt.TypeList, "Fractional position of resonators along the bandpass resonator length.", [0.5])
    resonator_lengths = Param(pdt.TypeList, "Readout resonators length in um.", [9000,  ])
    resonator_couplings = Param(pdt.TypeList, "Readout coupling length in um.", [100, ])

    qubit_loading = Param(pdt.TypeList, "Resonator length to subtract on qubit loaded side in um.", [0])

    # radius
    r = 50

    def _compute_hanger_location(self, position):

        return 3750 - self.filter_length / 2 + position * self.filter_length

    def _produce_readout_hangers(self):

        for i, pos in enumerate(self.filter_positions):

            # x_pos = self._compute_hanger_location(pos)
            x_pos = 3750

            clength = self.resonator_couplings[i]

            # alternate above and below of the feedline starting with down
            if i % 2:
                name_prefix = "HR_D"
                trans = pya.DTrans(2, True, x_pos + 1 * clength/2, 3750)
            else:
                name_prefix = "HR_U"
                trans = pya.DTrans(0, True, x_pos + -1 * clength/2, 3750)

            name = name_prefix + f"{int((i - i % 2)/2)}"
            rlength = clength + 2 * pi*self.r/2 + 150 * 2
            head = pi*self.r/2 + 150

            self.insert_cell(HangerResonator, trans, name, coupling_length=clength, ground_width=2,
                             head_length= head, res_b=self.b, res_a=self.a, resonator_length=rlength)

    def _compute_finger_locations(self, smooth_finger_width, smooth_finger_gap, smooth_ground_gap, finger_control):

        scale = smooth_finger_width + smooth_finger_gap
        x_max = max(finger_control, 1.0 / finger_control) * scale - smooth_finger_gap / 2

        xport = x_max + smooth_ground_gap + smooth_finger_gap

        return 2 * xport      

    def _readout_resonator_U(self, index, resonator_length, position, couple_length, qubit_load):
        # positioning split between the coupling sides
        rollLength = (1 - position) * resonator_length

        # length of hanger structure. clength + 2x (turn radius + 150um verticals)
        hangerLength = couple_length + 2 * pi*self.r/2 + 150 * 2

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
        rightFixed = 50 + 200 + 50 - 2 *self.r * (1 - pi / 2)  - 200
        # qubitVjog = self.refpoints[f"Q_U{index}_port_cplr"].y - (self.refpoints[f"HR_U{index}_port_resonator_b_corner"].y + 1100)

        # 355 comes from current 20um qubt half ground plane dimension, to be noted when changed later
        qubitVjog = 5700 - 355 - (self.refpoints[f"HR_U{index}_port_resonator_b_corner"].y + 1100)
        print(qubitVjog)

        rightFixed += qubitVjog - 2 * self.r * (1 - pi / 2) + 100 + (couple_length/2 + 200 + self.r)

        leftNodes = [
                Node(
                    self.refpoints[f"HR_U{index}_port_resonator_a"],
                    # ab_across=True,
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
                    # length_before=950,
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
        

        # left composite
        layout = pya.Layout()
        leftComposite = WaveguideComposite.create(
            layout=layout,
            r = self.r,
            nodes = leftNodes,
            term2=15,
        )

        # self.insert_cell(leftComposite)
        self.insert_cell(
            WaveguideComposite,
            nodes=leftNodes,
            term2=15,
        )

        rightNodes = [
                Node(
                    self.refpoints[f"HR_U{index}_port_resonator_b"],
                    # ab_across=True,
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
                # Node((self.refpoints[f"Q_U{index}_port_cplr_corner"].x,
                Node(
                    (
                        # self._compute_hanger_location(position),
                        3750,
                        self.refpoints[f"HR_U{index}_port_resonator_b_corner"].y + 1100,
                    ),
                ),
                # Node(self.refpoints[f"Q_U{index}_port_cplr_corner"]),
                # Node(self.refpoints[f"Q_U{index}_port_cplr"]),
                Node(
                    # (self._compute_hanger_location(position), 5700 - 355)
                    (3750, 5700 - 355)
                ),
            ]

        # right composite
        rightComposite = WaveguideComposite.create(
            layout=layout, r = self.r, 
            nodes=rightNodes,
            term2=15,
        )

        self.insert_cell(
            WaveguideComposite,
            nodes=rightNodes,
            term2=15,
        )

        # print(leftFixed, rightFixed)
        # print(leftLength - leftFixed, rightLength - rightFixed)
        # print("leftc", sum(leftComposite.segment_lengths()))
        # print("rightc", sum(rightComposite.segment_lengths()))

        print("total", sum(leftComposite.segment_lengths()) + sum(rightComposite.segment_lengths()) + hangerLength)

    def _readout_resonator_D(self, index, resonator_length, position, couple_length, qubit_load):
        # positioning split between the coupling sides
        rollLength = (1 - position) * resonator_length

        # length of hanger structure. clength + 2x (turn radius + 150um verticals)
        hangerLength = couple_length + 2 * pi*self.r/2 + 150 * 2

        # subtract half of the hangerLength from both sides
        leftLength = resonator_length - rollLength - 0.5 * hangerLength
        rightLength = rollLength - 0.5 * hangerLength - qubit_load

        # fixed lengths left: 50 vert + 200 horz - 2 * turn radii on the bottom side
        # left top side: 100 vert, + 300 horz - turn radius
        leftFixed = 50 + 200 - 2 * self.r * (1 - pi / 2) + 100 + 300 - self.r * (1 - pi / 2)

        # fixed lengths right: 50 vert + 200 horz - 2 * turn radii on the bottom side
        # top side right: 100 vert + clength/2 + 200 horz - 1* turn_radius
        # top side right contd: - 1*turn_radius + y position of qubit
        rightFixed = 50 + 200 - 2 *self.r * (1 - pi / 2) + 100 + (couple_length/2 + 200) - self.r * (1 - pi / 2)
        qubitVjog = -1 * (self.refpoints[f"Q_D{index}_port_cplr"].y - (self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y - 1100))
        rightFixed += qubitVjog - self.r * (1 - pi / 2)

        # left composite non qubit side
        self.insert_cell(
            WaveguideComposite,
            nodes = [
                Node(self.refpoints[f"HR_D{index}_port_resonator_b"]),
                Node(self.refpoints[f"HR_D{index}_port_resonator_b_corner"]),
                Node((self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 200,
                      self.refpoints[f"HR_D{index}_port_resonator_b_corner"].y,
                      )),
                Node((self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 200,
                      self.refpoints[f"HR_D{index}_port_resonator_b_corner"].y - 50,
                      )),
                Node((self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 200,
                      self.refpoints[f"HR_D{index}_port_resonator_b_corner"].y - 1000,
                      ),
                     length_before= leftLength - leftFixed,
                     meander_direction = -1),
                Node((self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 200,
                      self.refpoints[f"HR_D{index}_port_resonator_b_corner"].y - 1100,
                      ),), 
                Node((self.refpoints[f"HR_D{index}_port_resonator_b_corner"].x - 500,
                      self.refpoints[f"HR_D{index}_port_resonator_b_corner"].y - 1100,
                      ),),             
            ],
            term2=15
        )

        # right qubit side composite
        self.insert_cell(
            WaveguideComposite,
            nodes = [
                Node(self.refpoints[f"HR_D{index}_port_resonator_a"]),
                Node(self.refpoints[f"HR_D{index}_port_resonator_a_corner"]),
                Node((self.refpoints[f"HR_D{index}_port_resonator_a_corner"].x + 200,
                      self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y,
                      )),
                Node((self.refpoints[f"HR_D{index}_port_resonator_a_corner"].x + 200,
                      self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y - 50,
                      )),
                Node((self.refpoints[f"HR_D{index}_port_resonator_a_corner"].x + 200,
                      self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y - 1000,
                      ),
                     length_before= rightLength - rightFixed,
                    meander_direction = -1),
                Node((self.refpoints[f"HR_D{index}_port_resonator_a_corner"].x + 200,
                      self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y - 1100,
                      ),),
                Node((self.refpoints[f"Q_D{index}_port_cplr_corner"].x,
                      self.refpoints[f"HR_D{index}_port_resonator_a_corner"].y - 1100),
                      ),
                Node(self.refpoints[f"Q_D{index}_port_cplr_corner"]),
                Node(self.refpoints[f"Q_D{index}_port_cplr"])
            ],
        ) 

    def build(self):

        self._produce_readout_hangers()

        # left_ref_names = ["Meander_Cin_port_b"]
        # right_ref_names = []

        # left_ref_names.append(f"HR_U0_port_b")
        # right_ref_names.append(f"HR_U0_port_a")
        # right_ref_names.append("Meander_Cout_port_b")

        # for i in range(len(left_ref_names)):
        #     self.insert_cell(
        #         WaveguideCoplanar,
        #         path=pya.DPath([
        #             self.refpoints[left_ref_names[i]],
        #             self.refpoints[right_ref_names[i]]
        #         ], 0),
        #         inst_name = f"cpw_section_{i}",
        #     )

        # qubit positioning coordinates
        self.U_coords = []
        self.D_coords = []                

        for i, pos in enumerate(self.filter_positions):
            if i % 2:
                # top row positioning
                self.D_coords.append(pya.DTrans(0, False, self._compute_hanger_location(pos) + 0*500, 1800))
            else:
                # bottom row positioning
                self.U_coords.append(pya.DTrans(2, False, self._compute_hanger_location(pos) + 0*500, 5700))

        # Qubit U3: 20 um gap "MOD D" participation. done
        # try:
        #     self.insert_cell(
        #         DoublePads, self.U_coords[0], f"Q_U0", ground_gap=['1200', '710'],
        #         ground_gap_r=0.0, coupler_extent=['209', '20'], coupler_r=0.0, coupler_offset=50.0,
        #         island1_extent=['752', '120'], island1_r=0.0, island2_extent=['752', '120'],
        #         island2_r=0.0, drive_position=['-450', '0'], island_island_gap=20.0,
        #         _parameters='{"junction_type": "Sim"}', with_squid=False,
        #         island1_taper_width=0, island1_taper_junction_width=0,
        #         island2_taper_width=0, island2_taper_junction_width=0,
        #     )
        # except IndexError:
        #     print("Qubit index not requested based on resonator length array.")

        for i, pos in enumerate(self.filter_positions):
            if i % 2:
                self._readout_resonator_D(
                    index = int(i / 2), resonator_length=self.resonator_lengths[i], position=pos,
                    couple_length=self.resonator_couplings[i], qubit_load=self.qubit_loading[i]
                )
            else:
                self._readout_resonator_U(
                    index = int(i / 2), resonator_length=self.resonator_lengths[i], position=pos,
                    couple_length=self.resonator_couplings[i], qubit_load=self.qubit_loading[i]
                                            )

        self.layout

    @classmethod
    def get_sim_ports(cls, simulation):
        return [
            WaveguideToSimPort("HR_U0_port_a", use_internal_ports=False, a=simulation.a, b=simulation.b),
            WaveguideToSimPort("HR_U0_port_b", use_internal_ports=False, a=simulation.a, b=simulation.b),
        ]
