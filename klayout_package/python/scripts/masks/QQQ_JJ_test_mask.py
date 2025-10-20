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

from kqcircuits.chips.junction_test_5 import JunctionTest5
from kqcircuits.chips.junction_test_5_overlap import JunctionTest5Overlap
from kqcircuits.chips.junction_test_5_arrayv2 import JunctionTestArray5v2
from kqcircuits.chips.junction_test_5_arrayv2double import JunctionTestArray5v2Double
from kqcircuits.chips.junction_test_QQQ import JunctionTestQQQ

from kqcircuits.elements.markers.marker import Marker
from kqcircuits.elements.markers.mask_marker_nist import MaskMarkerNist

mask = MaskSet(name="JJ1124", version=1, with_grid=False)

chip_layout = [["---" for _ in range(15)] for _ in range(15)]

qubit_finger_spread = [[100,104,108],[112,116,120],[124,128,132]]
squid_finger_L_spread = [[2200,2288,2376],[2464,2552,2640],[2728,2816,2904]]
squid_finger_O_spread = [[1100,1144,1188],[1232,1276,1320],[1364,1408,1452]]

temp_finger = sum(qubit_finger_spread, [])
penguin_fingers = [temp_finger[i // 2] for i in range(2 * len(temp_finger))]
temp_squid = sum(squid_finger_O_spread, [])
penguin_squid = [temp_squid[i // 2] for i in range(2 * len(temp_squid))]

for i in range(11):    
    for j in range(11):
        s = (i + j) % 3
        if j % 4 == 0:
            if i % 2 == 0:
                chip_layout[i+2][j+2] = f"JL{s}"
            else:
                chip_layout[i+2][j+2] = f"JO{s}"
        elif j % 4 == 1:
            chip_layout[i+2][j+2] = f"JP"
        elif j % 4 == 2:
            if i % 3 == 0:
                chip_layout[i+2][j+2] = f"A0"
            elif i % 3 == 1:
                chip_layout[i+2][j+2] = f"A1"
            else:
                chip_layout[i+2][j+2] = f"A2"
        else:
            if i % 3 == 0:
                chip_layout[i+2][j+2] = f"D0"
            elif i % 3 == 1:
                chip_layout[i+2][j+2] = f"D1"
            else:
                chip_layout[i+2][j+2] = f"D2"

# add junction test chip
# chip_layout[5][8] = "JJ"

wf = mask.add_mask_layout(chip_layout, "1t1", mask_name_scale=0.5, 
                         mask_markers_dict={MaskMarkerNist: {}})

array_params = {
    "array_widths": [3400, 3450, 3500, 3550, 3600],
    "A_junction_number": [57, 55, 53, 51, 49],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
}
array_paramsEx1 = {
    "array_widths": [3400, 3450, 3500, 3550, 3600],
    "A_junction_number": [67, 65, 63, 61, 59],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
}
array_paramsEx2 = {
    "array_widths": [3400, 3450, 3500, 3550, 3600],
    "A_junction_number": [47, 45, 43, 41, 49],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
}

darray_params = {
    "array_widths": [3400, 3450, 3500, 3550, 3600],
    "A_junction_number": [111, 109, 107, 105, 103],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
    "array_gap": 15.0,
}
darray_paramsEx1 = {
    "array_widths": [3400, 3450, 3500, 3550, 3600],
    "A_junction_number": [121, 119, 117, 115, 113],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
    "array_gap": 15.0,
}
darray_paramsEx2 = {
    "array_widths": [3400, 3450, 3500, 3550, 3600],
    "A_junction_number": [101, 99, 97, 95, 95],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
    "array_gap": 15.0,
}

mask.add_chip([(JunctionTestArray5v2, "A0", array_params)])
mask.add_chip([(JunctionTestArray5v2, "A1", array_paramsEx1)])
mask.add_chip([(JunctionTestArray5v2, "A2", array_paramsEx2)])

mask.add_chip([(JunctionTestArray5v2Double, "D0", darray_params)])
mask.add_chip([(JunctionTestArray5v2Double, "D1", darray_paramsEx1)])
mask.add_chip([(JunctionTestArray5v2Double, "D2", darray_paramsEx2)])

mask.add_chip([
    (JunctionTest5, f"JL{s}", {
    "qubit_widths": qubit_finger_spread[s],
    "bridge_width": 100*1e-3,
    "SQUID_widths": squid_finger_L_spread[s],
    "qubit_hook": 196*1e-3,
    "squid_hook": 196*1e-3,
    "squid_hook_width": 3.5,
    }) 
    for s in range(len(qubit_finger_spread))
])

mask.add_chip([
    (JunctionTest5Overlap, f"JO{s}", {
    "qubit_widths": qubit_finger_spread[s],
    "bridge_width": 100*1e-3,
    "SQUID_widths": squid_finger_O_spread[s],
    "qubit_hook": 196*1e-3,
    "squid_taper": 2.0,
    }) 
    for s in range(len(qubit_finger_spread))
])

penguin = {
    "Q_bridge_gap": 100*1e-3,
    "Q_hook_thickness": 196*1e-3,
    "Q_finger_widths": penguin_fingers,
    "S_finger_widths": penguin_squid,
    "S_bridge_gap": 100*1e-3,
    "S_taper": 3.5
}

mask.add_chip([(JunctionTestQQQ, "JP", penguin)])


mask.build()
mask.export()
