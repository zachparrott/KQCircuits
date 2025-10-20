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
from kqcircuits.qubits.double_pads_round import DoublePadsRound
from kqcircuits.qubits.finger_pads_jj import FingerPadsJJ

@add_parameters_from(Element, b = 4.6, a = 10, margin=100)
@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200)))
# no flip chip alignment markers
@add_parameters_from(ChipFrame, marker_types=['','','',''])
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(5200, 5200))],
                     frames_dice_width=['150'], name_brand='NIST', name_chip='T1 PR', name_copy='v3')

class NISTpart354(Chip):
    # parameters accessible in PCell
    a_launcher = Param(pdt.TypeDouble, "Pad CPW trace center", 200, unit="μm")
    b_launcher = Param(pdt.TypeDouble, "Pad CPW trace gap", 153, unit="μm")
    launcher_width = Param(pdt.TypeDouble, "Pad extent", 250, unit="μm")
    taper_length = Param(pdt.TypeDouble, "Tapering length", 200, unit="μm")
    launcher_frame_gap = Param(pdt.TypeDouble, "Gap at chip frame", 100, unit="μm") 
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
                name_prefix = "HR_D"
                trans = pya.DTrans(2, True, 3000 - 250 + i*650 + 1 * (clength + self.r), 2600)
            else:
                name_prefix = "HR_U"
                trans = pya.DTrans(0, True, 1550 + 250 + i*650 + -1 * (clength + self.r), 2600)

            name = name_prefix + f"{int((i - i % 2)/2)}"
            rlength = clength + pi*self.r/2 + 100

            self.insert_cell(HangerResonator, trans, name, coupling_length=clength, ground_width=6,
                             head_length=0, res_b=self.b, res_a=self.a, resonator_length=rlength)

            left_ref_names = ["W_port"]
            right_ref_names = []
            left_ref_names.append(f"HR_U0_port_sim_b")
            left_ref_names.append(f"HR_D0_port_sim_a")
            right_ref_names.append(f"HR_U0_port_sim_a")
            right_ref_names.append(f"HR_D0_port_sim_b")
            right_ref_names.append("E_port")

        for i in range(3):
            self.insert_cell(
                WaveguideCoplanar, 
                path=pya.DPath([
                    self.refpoints[left_ref_names[i]],
                    self.refpoints[right_ref_names[i]]
                ], 0),
            )

    def _produce_u_res(self, i, length, adjust):
        self.insert_cell(
                WaveguideComposite,
                nodes = [
                    Node(self.refpoints[f"HR_U{i}_port_resonator_b"]), 
                    Node((self.refpoints[f"HR_U{i}_port_resonator_b"].x, self.refpoints[f"Q_U{i}_port_cplr_corner"].y - 245), 
                         length_before=(length - adjust)),
                    Node((self.refpoints[f"HR_U{i}_port_resonator_b"].x, self.refpoints[f"Q_U{i}_port_cplr_corner"].y)),
                    Node((self.refpoints[f"Q_U{i}_port_cplr_corner"].x, self.refpoints[f"Q_U{i}_port_cplr_corner"].y)),
                    # Node((self.refpoints[f"Q_U{i}_port_cplr_corner"].x, self.refpoints[f"Q_U{i}_port_cplr_corner"].y)),
                    Node(self.refpoints[f"Q_U{i}_port_cplr"])
                ],  
            )

    def _produce_d_res(self, i, length, adjust):
        self.insert_cell(
                WaveguideComposite,
                nodes = [
                    Node(self.refpoints[f"HR_D{i}_port_resonator_b"]), 
                    Node((self.refpoints[f"HR_D{i}_port_resonator_b"].x, self.refpoints[f"Q_D{i}_port_cplr_corner"].y + 245), 
                         length_before=(length - adjust)),
                    Node((self.refpoints[f"HR_D{i}_port_resonator_b"].x, self.refpoints[f"Q_D{i}_port_cplr_corner"].y - 100)),
                    Node((self.refpoints[f"Q_D{i}_port_cplr_corner"].x, self.refpoints[f"Q_D{i}_port_cplr_corner"].y - 100)),
                    # Node((self.refpoints[f"Q_D{i}_port_cplr_corner"].x, self.refpoints[f"Q_D{i}_port_cplr_corner"].y - 100)),
                    Node(self.refpoints[f"Q_D{i}_port_cplr"])
                ],
            )

    def build(self):
        self.launchers = self.produce_two_launchers(self.launcher_width, self.b_launcher, self.launcher_width, 
                                   self.taper_length, self.launcher_frame_gap, self.launcher_indent, 100, launcher_assignments={1: "E", 2: "W"})

        res_lengths2 = [4206.2, 4171.4]
        
        coupling_lengths = [ 113., 112.]
        
        hanger_coupling_lengths = []
        for i in range(2):
                hanger_coupling_lengths.append(coupling_lengths[i])
                

        self.hangers = self._produce_readout_hangers(hanger_coupling_lengths)

        # top row positioning
        U_coords = [pya.DTrans(1, False, 1550 + 1755 + 250 + i * 1300, 4150 - 400) for i in range(1)]
        # bottom row positioning
        D_coords = [pya.DTrans(2, False, 3650 -1755- 250 + i * 1300, 1050 + 550) for i in range(1)]


        # Qubit U3: 20 um gap "MOD D" participation. done
        self.insert_cell(
            DoublePads, U_coords[0], f"Q_U0", ground_gap=['1200', '710'], 
            ground_gap_r=0.0, coupler_extent=['65.5', '20'], coupler_r=0.0, coupler_offset=50.0, 
            island1_extent=['738', '120'], island1_r=0.0, island2_extent=['738', '120'], 
            island2_r=0.0, drive_position=['-450', '0'], island_island_gap=20.0,
            _parameters='{"junction_type": "Sim"}', with_squid=False,
            island1_taper_width=0, island1_taper_junction_width=0, 
            island2_taper_width=0, island2_taper_junction_width=0, 
        )

        # qubit D0: 20 um gap "MOD D" participation
        self.insert_cell(
            DoublePads, D_coords[0], f"Q_D0", ground_gap=['1200', '710'], 
            ground_gap_r=0.0, coupler_extent=['86.2', '20'], coupler_r=0.0, coupler_offset=50.0, 
            island1_extent=['799', '120'], island1_r=0.0, island2_extent=['799', '120'], 
            island2_r=0.0, drive_position=['-450', '0'], island_island_gap=20.0,
            _parameters='{"junction_type": "Sim"}', with_squid=False,
            island1_taper_width=0, island1_taper_junction_width=0, 
            island2_taper_width=0, island2_taper_junction_width=0, 
        )

        res_final = [res_lengths2[i] for i in range(2)]

        rad_adj = 1 * self.r * (2 - pi / 2)

        # 20 um 735, rounded 845, idc 515

        res_params= {
            
            'U0': {'len': res_final[0], 'adj': 960 + coupling_lengths[0] - rad_adj},

            'D0': {'len': res_final[1], 'adj': 2405 + coupling_lengths[1] - rad_adj},
            
        }

        for key in res_params:
            if key[0] == 'U':
                self._produce_u_res(key[1], res_params[key]['len'], res_params[key]['adj'])
            elif key[0] == 'D':
                self._produce_d_res(key[1], res_params[key]['len'], res_params[key]['adj'])
            else:
                pass
