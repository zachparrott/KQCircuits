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

from kqcircuits.masks.mask_set import MaskSet

from klayout_package.python.kqcircuits.chips.QQQ_v5_2_3 import ChipQQQ
from kqcircuits.chips.QQQ_PIQUE_IDC import ChipPiqueIDC
from kqcircuits.chips.QQQ_PIQUE_uncoupled import ChipPiqueUncoupled
from kqcircuits.chips.junction_test_5 import JunctionTest5

from kqcircuits.elements.markers.marker import Marker
from kqcircuits.elements.markers.mask_marker_nist import MaskMarkerNist

mask = MaskSet(name="ZP0324", version=1, with_grid=False)

chip_layout = [["---" for _ in range(15)] for _ in range(15)]

qubit_finger_spread = [96, 104, 112, 120, 128, 136, 144, 152, 160, 168, 176]
for i in range(11):
    for j in range(11): 
        chip_layout[i+2][j+2] = f"Q{qubit_finger_spread[j]}"

# add junction test chip
chip_layout[5][8] = "JJ"
chip_layout[8][5] = "JJ"
chip_layout[10][10] = "JJ"

# add some PIQUE chips
chip_layout[5][2] = "I96"
chip_layout[8][3] = "I104"
chip_layout[3][4] = "I112"
chip_layout[6][5] = "I120"
chip_layout[11][6] = "I128"
chip_layout[2][7] = "I136"
chip_layout[9][8] = "I144"
chip_layout[4][9] = "I152"
chip_layout[7][10] = "I160"
chip_layout[10][11] = "I168"
chip_layout[5][12] = "I176"

chip_layout[9][2] = "U96"
chip_layout[4][3] = "U104"
chip_layout[9][4] = "U112"
chip_layout[4][5] = "U120"
chip_layout[5][6] = "U128"
chip_layout[10][7] = "U136"
chip_layout[12][8] = "U144"
chip_layout[8][9] = "U152"
chip_layout[3][10] = "U160"
chip_layout[6][11] = "U168"
chip_layout[8][12] = "U176"

wf = mask.add_mask_layout(chip_layout, "1t1", mask_name_scale=0.5, 
                         mask_markers_dict={MaskMarkerNist: {}})

mask.add_chip([
    (ChipQQQ, f"Q{f_width}", {
        "Q_finger_width": f_width*1e-3,
        "Q_bridge_gap": 150*1e-3,
        "Q_hook_thickness": 100*1e-3,
        "S_finger_width": 11 * f_width * 1e-3,
        "S_bridge_gap": 150*1e-3,
        "S_hook_thickness": 200*1e-3,
        }) 
    for f_width in set(qubit_finger_spread)
])
mask.add_chip([
    (ChipPiqueIDC, f"I{f_width}", {
        "Q_finger_width": f_width*1e-3,
        "Q_bridge_gap": 150*1e-3,
        "Q_hook_thickness": 100*1e-3,
        "S_finger_width": 11 * f_width * 1e-3,
        "S_bridge_gap": 150*1e-3,
        "S_hook_thickness": 200*1e-3,
        }) 
    for f_width in set(qubit_finger_spread)
])
mask.add_chip([
    (ChipPiqueUncoupled, f"U{f_width}", {
        "Q_finger_width": f_width*1e-3,
        "Q_bridge_gap": 150*1e-3,
        "Q_hook_thickness": 100*1e-3,
        "S_finger_width": 11 * f_width * 1e-3,
        "S_bridge_gap": 150*1e-3,
        "S_hook_thickness": 200*1e-3,
        }) 
    for f_width in set(qubit_finger_spread)
])

jjtest_params = {
    "qubit_widths": qubit_finger_spread,
    "bridge_width": 300*1e-3,
    "SQUID_ratio": 22,
    "qubit_hook": 100*1e-3,
    "squid_hook": 200*1e-3,
    }

mask.add_chip([(JunctionTest5, "JJ", jjtest_params)])

mask.build()
mask.export()
