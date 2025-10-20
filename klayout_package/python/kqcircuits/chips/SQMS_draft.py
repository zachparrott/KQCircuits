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

from kqcircuits.qubits.double_pads import DoublePads
from kqcircuits.qubits.finger_pads_jj import FingerPadsJJ

# from kqcircuits.chips.empty5 import Test5
# from kqcircuits.elements.waveguide_coplanar import WaveguideCoplanar


# Test51, Test51_refpoints = Test5.create_with_refpoints(layout, rec_levels=0, b=4.6000000000000005,
# frames_enabled=['0'], frames_marker_dist=['1500', '1000'], frames_diagonal_squares=['10', '2'],
# frames_mirrored=['false', 'true'], frames_dice_width=['100', '140'], name_chip='T1 PR', name_copy='',
# name_brand='SQMS', a_launcher=200.0, b_launcher=160.0, launcher_width=250.0, taper_length=200.0, launcher_frame_gap=50.0, launcher_indent=700.0)
# view.insert_cell(Test51, pya.DTrans())

@add_parameters_from(Element, b = 4.6, a = 10, margin=100)
@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(7500, 7500)))
# no flip chip alignment markers
@add_parameters_from(ChipFrame, marker_types=['','','',''])
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(7500, 7500))],
                     frames_dice_width=['100'], name_brand='SQMS', name_chip='T1 PR', name_copy='')

class SQMS(Chip):
    # parameters accessible in PCell
    a_launcher = Param(pdt.TypeDouble, "Pad CPW trace center", 200, unit="μm")
    b_launcher = Param(pdt.TypeDouble, "Pad CPW trace gap", 160, unit="μm")
    launcher_width = Param(pdt.TypeDouble, "Pad extent", 250, unit="μm")
    taper_length = Param(pdt.TypeDouble, "Tapering length", 200, unit="μm")
    launcher_frame_gap = Param(pdt.TypeDouble, "Gap at chip frame", 50, unit="μm") 
    launcher_indent = Param(pdt.TypeDouble, "Chip edge to pad port", 700, unit="μm") 

    def produce_two_launchers(self, a_launcher, b_launcher, launcher_width, taper_length, launcher_frame_gap, 
                              launcher_indent, pad_pitch, launcher_assignments=None,  enabled=None, chip_box=None,
                            face_id=0):
        
        launcher_cell = self.add_element(Launcher, s=launcher_width, l=taper_length,
                                             a_launcher=a_launcher, b_launcher=b_launcher,
                                             launcher_frame_gap=launcher_frame_gap, face_ids=[self.face_ids[face_id]])

        pads_per_side = [0,1,0,1]

        dirs = (90, 0, -90, 180)
        trans = (pya.DTrans(3, 0, self.box.p1.x, self.box.p2.y),
                 pya.DTrans(2, 0, self.box.p2.x, self.box.p2.y),
                 pya.DTrans(1, 0, self.box.p2.x, self.box.p1.y),
                 pya.DTrans(0, 0, self.box.p1.x, self.box.p1.y))
        _w = self.box.p2.x - self.box.p1.x
        _h = self.box.p2.y - self.box.p1.y
        sides = [_w, _h, _w, _h]

        return self._insert_launchers(dirs, enabled, launcher_assignments, None, launcher_cell, launcher_indent,
                                      launcher_width, pad_pitch, pads_per_side, sides, trans, face_id=0)

    def _produce_readout_hangers(self, coupling_lengths):
        # alternate flipping up and down. Position on center not port a
        for i,clength in enumerate(coupling_lengths):
            if i % 2:
                rotate_factor = 1
                name_prefix = "HR_D"
            else:
                rotate_factor = -1
                name_prefix = "HR_U"

            
            trans = pya.DTrans((rotate_factor + 1), True, 1250 + i*715 + rotate_factor * (clength + self.r)/2, 3750)
            name = name_prefix + f"{int((i - i % 2)/2)}"
            rlength = clength + pi*self.r/2 + 150

            self.insert_cell(HangerResonator, trans, name, coupling_length=clength,
                             head_length=0, res_b=self.b, res_a=self.a, resonator_length=rlength)

            left_ref_names = ["W_port"]
            right_ref_names = []
            for i in range(4):
                left_ref_names.append(f"HR_U{i}_port_sim_b")
                left_ref_names.append(f"HR_D{i}_port_sim_a")
                right_ref_names.append(f"HR_U{i}_port_sim_a")
                right_ref_names.append(f"HR_D{i}_port_sim_b")
            right_ref_names.append("E_port")

        for i in range(9):
            self.insert_cell(
                WaveguideCoplanar, 
                path=pya.DPath([
                    self.refpoints[left_ref_names[i]],
                    self.refpoints[right_ref_names[i]]
                ], 0),
            )

    def build(self):
        self.launchers = self.produce_two_launchers(self.launcher_width, self.b_launcher, self.launcher_width, 
                                   self.taper_length, self.launcher_frame_gap, self.launcher_indent, 100, launcher_assignments={1: "E", 2: "W"})

        coupling_lengths = [200 for _ in range(8)]

        self.hangers = self._produce_readout_hangers(coupling_lengths)

        # top row positioning
        U_coords = [pya.DTrans(3, False, 1650 + i * 1400, 5850) for i in range(4)]
        # bottom row positioning
        D_coords = [pya.DTrans(1, False, 1650 + i * 1400, 1650) for i in range(4)]


        # Qubit U0: 20 um gap "MOD D" participation with length:
        self.insert_cell(
            DoublePads, U_coords[0], f"Q_U0", ground_gap=['800', '800'], 
            ground_gap_r=0.0, coupler_extent=['50', '10'], coupler_r=0.0, coupler_offset=30.0, 
            island1_extent=['420', '120'], island1_r=0.0, island2_extent=['420', '120'], 
            island2_r=0.0, drive_position=['-450', '0'], island_island_gap=20.0,
            _parameters='{"junction_type": "Sim"}'
        )

        # Qubit U1: 20 um gap "MOD D" participation with length: 
        self.insert_cell(
            DoublePads, U_coords[1], f"Q_U1", ground_gap=['800', '800'], 
            ground_gap_r=0.0, coupler_extent=['50', '10'], coupler_r=0.0, coupler_offset=30.0, 
            island1_extent=['450', '120'], island1_r=0.0, island2_extent=['450', '120'], 
            island2_r=0.0, drive_position=['-450', '0'], island_island_gap=20.0,
            _parameters='{"junction_type": "Sim"}'
        )

        # Qubit U2: 70 um gap "MOD E" participation
        self.insert_cell(
            DoublePads, U_coords[2], f"Q_U2", ground_gap=['800', '800'], 
            ground_gap_r=0.0, coupler_extent=['50', '10'], coupler_r=0.0, coupler_offset=30.0, 
            island1_extent=['420', '200'], island1_r=10.0, island2_extent=['420', '200'], 
            island2_r=10.0, drive_position=['-450', '0'], island_island_gap=70.0,
            _parameters='{"junction_type": "Sim"}'
        )

        # Qubit U3: 70 um gap "MOD E" participation
        self.insert_cell(
            DoublePads, U_coords[3], f"Q_U3", ground_gap=['800', '800'], 
            ground_gap_r=0.0, coupler_extent=['50', '10'], coupler_r=0.0, coupler_offset=30.0, 
            island1_extent=['450', '180'], island1_r=10.0, island2_extent=['450', '180'], 
            island2_r=10.0, drive_position=['-450', '0'], island_island_gap=70.0,
            _parameters='{"junction_type": "Sim"}'
        )

        # qubit D0: 3 um finger IDC
        self.insert_cell(
            FingerPadsJJ, D_coords[0], f"Q_D0", ground_gap=['500', '300'], 
            ground_gap_r=0.0, coupler_extent=['50', '10'], coupler_r=0.0, coupler_offset=30.0, 
            finger_width=3, finger_gap=3, finger_gap_end=3, finger_length=50, finger_number=20,
            corner_r=0, 
        )

        # qubit D1: 3 um finger IDC
        self.insert_cell(
            FingerPadsJJ, D_coords[1], f"Q_D1", ground_gap=['500', '300'], 
            ground_gap_r=0.0, coupler_extent=['50', '10'], coupler_r=0.0, coupler_offset=30.0, 
            finger_width=3, finger_gap=3, finger_gap_end=3, finger_length=50, finger_number=24,
            corner_r=0, 
        )

        # qubit D0: 6 um finger IDC
        self.insert_cell(
            FingerPadsJJ, D_coords[2], f"Q_D2", ground_gap=['500', '300'], 
            ground_gap_r=0.0, coupler_extent=['50', '10'], coupler_r=0.0, coupler_offset=30.0, 
            finger_width=6, finger_gap=6, finger_gap_end=6, finger_length=50, finger_number=20,
            corner_r=0, 
        )

        # qubit D0: 6 um finger IDC
        self.insert_cell(
            FingerPadsJJ, D_coords[3], f"Q_D3", ground_gap=['500', '300'], 
            ground_gap_r=0.0, coupler_extent=['50', '10'], coupler_r=0.0, coupler_offset=30.0, 
            finger_width=6, finger_gap=6, finger_gap_end=6, finger_length=50, finger_number=24,
            corner_r=0, 
        )

        # res_lengths = {
        #     0: 4362,
        #     1: 4338,
        #     2: 4314,
        #     3: 4290,
        #     4: 4266,
        #     5: 4243,
        #     6: 4220,
        #     7: 4197
        # }
        res_lengths = {
            0: 4362,
            1: 4350,
            2: 4338,
            3: 4326,
            4: 4314,
            5: 4302,
            6: 4290,
            7: 4278
        }

        # use all 800x800 ground gaps and then evenly spread out. #1950 found by guess and adjust for 200 um gap length. And 1615 for smaller ground plane
        for i in range(4):       
            self.insert_cell(
                WaveguideComposite,
                nodes = [
                    Node(self.refpoints[f"HR_U{i}_port_resonator_b"]), 
                    Node((self.refpoints[f"HR_U{i}_port_resonator_b"].x, self.refpoints[f"Q_U{i}_port_cplr_corner"].y - 800), 
                         length_before=(res_lengths[i] - 2050)),
                    Node((self.refpoints[f"Q_U{i}_port_cplr_corner"].x, self.refpoints[f"Q_U{i}_port_cplr_corner"].y - 800)),
                    Node(self.refpoints[f"Q_U{i}_port_cplr_corner"]),
                    Node(self.refpoints[f"Q_U{i}_port_cplr"])
                ], 
            )
            
            self.insert_cell(
                WaveguideComposite,
                nodes = [
                    Node(self.refpoints[f"HR_D{i}_port_resonator_b"]), 
                    Node((self.refpoints[f"HR_D{i}_port_resonator_b"].x, self.refpoints[f"Q_D{i}_port_cplr_corner"].y + 800), 
                         length_before=(res_lengths[i+4] - 1715)),
                    Node((self.refpoints[f"Q_D{i}_port_cplr_corner"].x, self.refpoints[f"Q_D{i}_port_cplr_corner"].y + 800)),
                    Node(self.refpoints[f"Q_D{i}_port_cplr_corner"]),
                    Node(self.refpoints[f"Q_D{i}_port_cplr"])
                ],
            )
