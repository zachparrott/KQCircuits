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
from kqcircuits.qubits.double_pads_diff import DoublePadsDifferential


# from kqcircuits.chips.empty5 import Test5
# from kqcircuits.elements.waveguide_coplanar import WaveguideCoplanar


# Test51, Test51_refpoints = Test5.create_with_refpoints(layout, rec_levels=0, b=4.6000000000000005,
# frames_enabled=['0'], frames_marker_dist=['1500', '1000'], frames_diagonal_squares=['10', '2'],
# frames_mirrored=['false', 'true'], frames_dice_width=['100', '140'], name_chip='T1 PR', name_copy='',
# name_brand='SQMS', a_launcher=200.0, b_launcher=160.0, launcher_width=250.0, taper_length=200.0, launcher_frame_gap=50.0, launcher_indent=700.0)
# view.insert_cell(Test51, pya.DTrans())

@add_parameters_from(Element, b = 4.5, a = 10, margin=100)
@add_parameters_from(ChipFrame, box = pya.DBox(pya.DPoint(0, 0), pya.DPoint(7500, 7500)))
# no flip chip alignment markers
@add_parameters_from(ChipFrame, marker_types=['','','',''])
@add_parameters_from(Chip,
                     face_boxes=[None, pya.DBox(pya.DPoint(0, 0), pya.DPoint(7500, 7500))],
                     frames_dice_width=['50'], name_brand='NIST', name_chip='QP', name_copy='v1')

class NISTQuasiParticle(Chip):
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
            # if i > 3:
                rotate_factor = 1
                name_prefix = "HR_D"
                # opposing directions
                trans = pya.DTrans(2, True, 1185 + i*715 + 1 * (clength + self.r), 3750)
                # same directions
                # trans = pya.DTrans(0, False, 1000 + i*715 + 1 * (clength + self.r), 3750)
            else:
                rotate_factor = -1
                name_prefix = "HR_U"
                trans = pya.DTrans(0, True, 1400 + i*715 + -1 * (clength + self.r), 3750)


            #orig
            # trans = pya.DTrans((rotate_factor + 1), True, 1250 + i*715 + rotate_factor * (clength + self.r)/2, 3750)

            name = name_prefix + f"{int((i - i % 2)/2)}"
            rlength = clength + pi*self.r/2 + 150

            self.insert_cell(HangerResonator, trans, name, coupling_length=clength, ground_width=6,
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

    def _produce_u_res(self, i, length, adjust):
        self.insert_cell(
                WaveguideComposite,
                nodes = [
                    Node(self.refpoints[f"HR_U{i}_port_resonator_b"]), 
                    Node((self.refpoints[f"HR_U{i}_port_resonator_b"].x, self.refpoints[f"Q_U{i}_port_cplr_corner"].y - 950), 
                         length_before=(length - adjust)),
                    Node((self.refpoints[f"HR_U{i}_port_resonator_b"].x, self.refpoints[f"Q_U{i}_port_cplr_corner"].y - 800)),
                    Node((self.refpoints[f"Q_U{i}_port_cplr_corner"].x + 155, self.refpoints[f"Q_U{i}_port_cplr_corner"].y - 800)),
                    Node((self.refpoints[f"Q_U{i}_port_cplr_corner"].x + 155, self.refpoints[f"Q_U{i}_port_cplr_corner"].y)),
                    Node(self.refpoints[f"Q_U{i}_port_cplr"])
                ], 
            )

    def _produce_d_res(self, i, length, adjust):
        self.insert_cell(
                WaveguideComposite,
                nodes = [
                    Node(self.refpoints[f"HR_D{i}_port_resonator_b"]), 
                    Node((self.refpoints[f"HR_D{i}_port_resonator_b"].x, self.refpoints[f"Q_D{i}_port_cplr_corner"].y + 950), 
                         length_before=(length - adjust)),
                    Node((self.refpoints[f"HR_D{i}_port_resonator_b"].x, self.refpoints[f"Q_D{i}_port_cplr_corner"].y + 800)),
                    Node((self.refpoints[f"Q_D{i}_port_cplr_corner"].x - 155, self.refpoints[f"Q_D{i}_port_cplr_corner"].y + 800)),
                    Node((self.refpoints[f"Q_D{i}_port_cplr_corner"].x - 155, self.refpoints[f"Q_D{i}_port_cplr_corner"].y)),
                    Node(self.refpoints[f"Q_D{i}_port_cplr"])
                ],
            )

    def build(self):
        self.launchers = self.produce_two_launchers(self.launcher_width, self.b_launcher, self.launcher_width, 
                                   self.taper_length, self.launcher_frame_gap, self.launcher_indent, 100, launcher_assignments={1: "E", 2: "W"})

        res_lengths2 = [3754, 3725, 3695, 3667, 3639, 3612, 3585, 3558]
        # res_lengths2 = [4000] * 8

        # coupling lengths in produce readout hangers need to alternate. 
        # but to keep consistent with resonator definition we need to do Us then Ds
        coupling_lengths = [101., 100.,  99.,  98.,  97.,  96.,  95.,  94.]
        # coupling_lengths = [100]*8

        hanger_coupling_lengths = []
        for i in range(4):
                hanger_coupling_lengths.append(coupling_lengths[i])
                hanger_coupling_lengths.append(coupling_lengths[i+4])

        self.hangers = self._produce_readout_hangers(hanger_coupling_lengths)

        # top row positioning
        U_coords = [pya.DTrans(3, False, 1650 + i * 1430, 5650) for i in range(4)]
        # bottom row positioning
        D_coords = [pya.DTrans(1, False, 1650 + i * 1430, 1850) for i in range(4)]

        for i in range(4):
            self.insert_cell(
                DoublePadsDifferential, U_coords[i], f"Q_U{i}", ground_gap=['756', '600'], 
                ground_gap_r=0.0, coupler_extent=['103.5', '155'], coupler_r=0.0, coupler_offset=20.0, 
                island1_extent=['247', '120'], island1_r=0.0, island2_extent=['506', '120'], 
                island2_r=0.0, drive_position=['-450', '0'], island_island_gap=20.0,
                _parameters='{"junction_type": "Sim"}', with_squid=False,
                island1_taper_width=0, island1_taper_junction_width=0, 
                island2_taper_width=0, island2_taper_junction_width=0, 
            )
        
            self.insert_cell(
                DoublePadsDifferential, D_coords[i], f"Q_D{i}", ground_gap=['756', '600'], 
                ground_gap_r=0.0, coupler_extent=['103.5', '155'], coupler_r=0.0, coupler_offset=20.0, 
                island1_extent=['247', '120'], island1_r=0.0, island2_extent=['506', '120'], 
                island2_r=0.0, drive_position=['-450', '0'], island_island_gap=20.0,
                _parameters='{"junction_type": "Sim"}', with_squid=False,
                island1_taper_width=0, island1_taper_junction_width=0, 
                island2_taper_width=0, island2_taper_junction_width=0, 
            )

        res_final = [res_lengths2[i] for i in range(8)]

        rad_adj = 4 * self.r * (2 - pi / 2)

        # 55 for the skinnier than normal 20um ground gap
        # The .4 and .1 were errors from the HFSS lines, or maybe 4.6 gap
        # U_20_factor = 2505.4 + 55 - 200
        U_20_factor = 2505 + 55 - 200
        # D_20_factor = 2505.1 + 55 - 200
        D_20_factor = 2505 + 55 - 200

        res_params= {
            'U0': {'len': res_final[0], 'adj': U_20_factor + coupling_lengths[0] - rad_adj},
            'U1': {'len': res_final[1], 'adj': U_20_factor + coupling_lengths[1] - rad_adj},
            'U2': {'len': res_final[2], 'adj': U_20_factor + coupling_lengths[2] - rad_adj},
            'U3': {'len': res_final[3], 'adj': U_20_factor + coupling_lengths[3] - rad_adj},

            'D0': {'len': res_final[4], 'adj': D_20_factor + coupling_lengths[4] - rad_adj},
            'D1': {'len': res_final[5], 'adj': D_20_factor + coupling_lengths[5] - rad_adj},
            'D2': {'len': res_final[6], 'adj': D_20_factor + coupling_lengths[6] - rad_adj},
            'D3': {'len': res_final[7], 'adj': D_20_factor + coupling_lengths[7] - rad_adj},
        }

        for key in res_params:
            if key[0] == 'U':
                self._produce_u_res(key[1], res_params[key]['len'], res_params[key]['adj'])
            elif key[0] == 'D':
                self._produce_d_res(key[1], res_params[key]['len'], res_params[key]['adj'])
            else:
                pass
