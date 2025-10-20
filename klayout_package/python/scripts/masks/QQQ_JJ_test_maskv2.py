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


from kqcircuits.chips.junction_test_5_overlap import JunctionTest5Overlap
from kqcircuits.chips.junction_test_5_arrayv2 import JunctionTestArray5v2
from kqcircuits.chips.junction_test_5_arrayv2double import JunctionTestArray5v2Double
from kqcircuits.chips.junction_test_QQQ import JunctionTestQQQ
from kqcircuits.chips.junction_test_QCC import JunctionTestQCC
from kqcircuits.chips.junction_test_QCCdouble import JunctionTestQCCDouble

from kqcircuits.elements.markers.marker import Marker
from kqcircuits.elements.markers.mask_marker_nist import MaskMarkerNist

mask = MaskSet(name="JJ1224", version=1, with_grid=False, export_path=r"C:\Users\zlp\Documents\Simulation Projects\Main Projects\QQQ_v2\readout_v3\exportGDS")

chip_layout = [["---" for _ in range(15)] for _ in range(15)]

array_finger_spread = [[3400, 3450, 3500], [3400, 3450, 3500], [3400, 3450, 3500]]

qubit_finger_spread = [[100, 108, 116],[124, 132, 140]]

squid_finger_O_spread = [[924,1012,1100],[1188,1276,1364]]

# temp_finger = sum(qubit_finger_spread, [])
# penguin_fingers = [temp_finger[i // 3] for i in range(3 * len(temp_finger))]

penguin_fingers = [100, 100, 100, 108, 108, 108, 116, 116, 116, 124, 124, 124, 132, 132, 132, 140, 140, 140]

# temp_squid = sum(squid_finger_O_spread, [])
# penguin_squid = [temp_squid[i // 3] for i in range(3 * len(temp_squid))]

penguin_squid = [924, 924, 924, 1012, 1012, 1012, 1100, 1100, 1100, 1188, 1188, 1188, 1276, 1276, 1276, 1364, 1364, 1364]

# temp_array = sum(array_finger_spread, [])
# penguin_array_widths = [temp_array[i // 2] for i in range(2 * len(temp_array))]
penguin_array_widths = [3400, 3400, 3450, 3450, 3500, 3500, 3400, 3400, 3450, 3450, 3500, 3500, 3400, 3400, 3450, 3450, 3500, 3500]

penguin_numbers = [65, 63, 65, 63, 65, 63, 61, 59, 61, 59, 61, 59, 57, 55, 57, 55, 57, 55, 57, 55]

penguin_double_array_widths = penguin_array_widths

penguin_double_numbers = [115, 113, 115, 113, 115, 113, 111, 109, 111, 109, 111, 109, 107, 105, 107, 105, 107, 105]

# full_list = ["PQ", "PA", "JO", "JO1", "JO2", "A0", "A1", "D0", "D1"]
full_list = ["PQ", "PA", "JO", "A", "D"]

for i in range(11):    
    for j in range(11):
        s = (i*(11+0) + j) % len(full_list)
        if full_list[s] == "PQ":
            tempName = full_list[s]
        else:
            tempName = full_list[s] + f"{i % 2}"
        chip_layout[i+2][j+2] = tempName

print(chip_layout)

wf = mask.add_mask_layout(chip_layout, "1t1", mask_name_scale=0.5, 
                         mask_markers_dict={MaskMarkerNist: {}})
#
array_params = {
    "array_widths": [3400, 3450, 3500, 3550, 3600],
    "A_junction_number": [59, 57, 55, 53, 101],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
}
array_paramsEx1 = {
    "array_widths": [3400, 3450, 3500, 3550, 3600],
    "A_junction_number": [67, 65, 63, 61, 101],
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
    "A_junction_number": [109, 107, 105, 103, 101],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
    "array_gap": 15.0,
}
darray_paramsEx1 = {
    "array_widths": [3400, 3450, 3500, 3550, 3600],
    "A_junction_number": [117, 115, 113, 111, 101],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
    "array_gap": 15.0,
}
darray_paramsEx2 = {
    "array_widths": array_finger_spread[2],
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
    (JunctionTest5Overlap, "JO0", {
        "qubit_widths": qubit_finger_spread[0],
        "bridge_width": 100*1e-3,
        "SQUID_widths": squid_finger_O_spread[0],
        "qubit_hook": 196*1e-3,
        "squid_taper": 2.0,
    }),
    (JunctionTest5Overlap, "JO1", {
        "qubit_widths": qubit_finger_spread[1],
        "bridge_width": 100*1e-3,
        "SQUID_widths": squid_finger_O_spread[1],
        "qubit_hook": 196*1e-3,
        "squid_taper": 2.0,
    })
])

penguin = {
    "Q_bridge_gap": 100*1e-3,
    "Q_hook_thickness": 196*1e-3,
    "Q_finger_widths": penguin_fingers,
    "S_finger_widths": penguin_squid,
    "S_bridge_gap": 100*1e-3,
    "S_taper": 3.5
}
penguin_array = {
    "Q_finger_widths": penguin_fingers,
    "Q_bridge_gap": 100*1e-3,
    "Q_hook_thickness": 196*1e-3,
    "A_bridge_gap": 0.194,
    "A_gap_spacing": 0.8,
    "A_array_widths": penguin_array_widths,
    "A_junction_number": penguin_numbers,
}

penguin_double_array = {
    "Q_finger_widths": penguin_fingers,
    "Q_bridge_gap": 100*1e-3,
    "Q_hook_thickness": 196*1e-3,
    "A_bridge_gap": 0.194,
    "A_gap_spacing": 0.8,
    "A_array_widths": penguin_double_array_widths,
    "A_junction_number": penguin_double_numbers,
}

mask.add_chip([(JunctionTestQQQ, "PQ", penguin)])

mask.add_chip([(JunctionTestQCC, "PA0", penguin_array)])

mask.add_chip([(JunctionTestQCCDouble, "PA1", penguin_double_array)])

mask.build()
mask.export()
