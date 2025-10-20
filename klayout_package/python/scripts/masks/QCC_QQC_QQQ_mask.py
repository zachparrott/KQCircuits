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

from kqcircuits.chips.QQQ_v5_2_3 import ChipQQQ
from kqcircuits.chips.QQC_v10_7_2 import ChipQQC
from kqcircuits.chips.QCC_v10_7_2 import ChipQCC
from kqcircuits.chips.QCC_v10_7_2_double import ChipQCCD

from kqcircuits.chips.junction_test_5 import JunctionTest5

from kqcircuits.elements.markers.marker import Marker
from kqcircuits.elements.markers.mask_marker_nist import MaskMarkerNist

mask = MaskSet(name="ZZ0424", version=1, with_grid=False)

chip_layout = [["---" for _ in range(15)] for _ in range(15)]

chip_rows = []
for i in range(11):
    for j in range(11): 
        if j % 2:
            if i % 2:
                chip_layout[i+2][j+2] = "C_"
            else:
                chip_layout[i+2][j+2] = "B_"
        else:
            chip_layout[i+2][j+2] = "A_"

# qubit_finger_spread = a, bc, a, bc, a, bc, a, bc, a, 152, bc]
qubit_finger_spread = [120, 120, 128, 128, 136, 136, 136, 144, 144, 152, 152]
# squid_ratio = [19, 19, 26, 26, 22, 22, 22, 32, 32, 43, 43]
squid_ratio = [19, 19, 23, 23, 22, 22, 22, 24, 24, 25.7, 25.7]

for i in range(11):
    for j in range(11): 
        chip_layout[i+2][j+2] += f"{qubit_finger_spread[j]}_{squid_ratio[i]}"

# add junction test chip
chip_layout[5][8] = "JJ"
chip_layout[8][5] = "JJ"
chip_layout[10][10] = "JJ"

wf = mask.add_mask_layout(chip_layout, "1t1", mask_name_scale=0.5, 
                         mask_markers_dict={MaskMarkerNist: {}})

mask.add_chip([
    (ChipQQQ, f"B_{f_width}_{squid_ratio}", {
        "Q_finger_width": f_width*1e-3,
        "Q_bridge_gap": 150*1e-3,
        "Q_hook_thickness": 196*1e-3,
        "S_finger_width": 0.5 * squid_ratio * 136 * 1e-3,
        "S_bridge_gap": 150*1e-3,
        "S_hook_thickness": 196*1e-3,
        }) 
    for squid_ratio in set(squid_ratio) for f_width in set(qubit_finger_spread)
])

mask.add_chip([
    (ChipQQC, f"C_{f_width}_{squid_ratio}", {
        "Q_finger_width": f_width*1e-3,
        "Q_bridge_gap": 150*1e-3,
        "Q_hook_thickness": 196*1e-3,
        
        "S_finger_width": 0.5 * squid_ratio * 136 * 1e-3,
        "S_bridge_gap": 150*1e-3,
        "S_hook_thickness": 196*1e-3,

        "A_bridge_gap": 150*1e-3,
        "A_gap_spacing": 0.8,
        "A_bridge_length": 1.6,
        "A_junction_number": 81,
        }) 
    for squid_ratio in set(squid_ratio) for f_width in set(qubit_finger_spread)
])

mask.add_chip([
    (ChipQCC, f"A_{f_width}_{squid_ratio}", {
        "Q_finger_width": f_width*1e-3,
        "Q_bridge_gap": 150*1e-3,
        "Q_hook_thickness": 196*1e-3,
        
        "S_finger_width": 0.5 * squid_ratio * 136 * 1e-3,
        "S_bridge_gap": 150*1e-3,
        "S_hook_thickness": 196*1e-3,
        
        "A_bridge_gap": 150*1e-3,
        "A_gap_spacing": 0.8,
        "A_bridge_length": 1.6,
        "A_junction_number": 81,
        }) 
    for squid_ratio in set(squid_ratio) for f_width in set(qubit_finger_spread)
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
