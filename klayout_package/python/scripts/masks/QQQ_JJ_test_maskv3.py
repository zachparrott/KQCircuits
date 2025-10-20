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

mask = MaskSet(name="JJ0925", version=1, with_grid=False, export_path=r"C:\Users\zlp\Documents\Simulation Projects\Main Projects\QQQ_v2\readout_v3\exportGDS")

chip_layout = [["---" for _ in range(15)] for _ in range(15)]

array_finger_spread = [[3400, 3500, 3600], [3400, 3500, 3600], [3400, 3500, 3600]]

qubit_finger_spread = [[100, 112, 116],[136, 148, 152]]

squid_finger_O_spread = [[1160,1520,1880], [2280,2896,3198]]

# temp_finger = sum(qubit_finger_spread, [])
# penguin_fingers = [temp_finger[i // 3] for i in range(3 * len(temp_finger))]

penguin_fingers = [100, 100, 100, 112, 112, 112, 124, 124, 124, 136, 136, 136, 148, 148, 148, 152, 152, 152]

# temp_squid = sum(squid_finger_O_spread, [])
# penguin_squid = [temp_squid[i // 3] for i in range(3 * len(temp_squid))]

penguin_squid = [1160, 1160, 1160, 1520, 1520, 1520, 1880, 1880, 1880, 2280, 2280, 2280, 2896, 2896, 2896, 3198, 3198, 3198]

# temp_array = sum(array_finger_spread, [])
# penguin_array_widths = [temp_array[i // 2] for i in range(2 * len(temp_array))]
penguin_array_widths = [3400, 3400, 3500, 3500, 3600, 3600, 3400, 3400, 3500, 3500, 3600, 3600, 3400, 3400, 3500, 3500, 3600, 3600]

penguin_numbers = [75, 67, 75, 67, 75, 67, 59, 51, 59, 51, 59, 51, 43, 35, 43, 35, 43, 35, 43, 35]

penguin_double_array_widths = penguin_array_widths

penguin_double_numbers = [99, 91, 99, 91, 99, 91, 83, 75, 83, 75, 83, 75, 67, 59, 67, 59, 67, 59]

# full_list = ["PQ", "PA", "JO", "JO1", "JO2", "A0", "A1", "D0", "D1"]
full_list = ["PQ", "PA", "JO", "A", "D"]

for i in range(11):    
    for j in range(11):
        s = (i*(11+0) + j) % len(full_list)
        if full_list[s] == "PQ":
            tempName = full_list[s]
        elif full_list[s] == "A" or full_list[s] == "D":
            tempName = full_list[s] + f"{i % 3}"
        else:
            tempName = full_list[s] + f"{i % 2}"
        chip_layout[i+2][j+2] = tempName

print(chip_layout)

wf = mask.add_mask_layout(chip_layout, "1t1", mask_name_scale=0.5, 
                         mask_markers_dict={MaskMarkerNist: {}})
#
array_params = {
    "array_widths": [3400, 3500, 3600, 3700, 3800],
    "A_junction_number": [63, 67, 71, 75, 696],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
}
array_paramsEx1 = {
    "array_widths": [3400, 3500, 3600, 3700, 3800],
    "A_junction_number": [47, 51, 55, 59, 696],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
}
array_paramsEx2 = {
    "array_widths": [3400, 3500, 3600, 3700, 3800],
    "A_junction_number": [31, 35, 39, 43, 696],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
}

darray_params = {
    "array_widths": [3400, 3500, 3600, 3700, 3800],
    "A_junction_number": [55, 59, 63, 67, 101],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
    "array_gap": 15.0,
}
darray_paramsEx1 = {
    "array_widths": [3400, 3500, 3600, 3700, 3800],
    "A_junction_number": [71, 75, 79, 83, 101],
    "A_bridge_gap": 0.154,
    "A_gap_spacing": 0.8,
    "array_gap": 15.0,
}
darray_paramsEx2 = {
    "array_widths": [3400, 3500, 3600, 3700, 3800],
    "A_junction_number": [87, 91, 95, 99, 95],
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
        "squid_taper": 3.5,
    })])
mask.add_chip([
    (JunctionTest5Overlap, "JO1", {
        "qubit_widths": qubit_finger_spread[1],
        "bridge_width": 100*1e-3,
        "SQUID_widths": squid_finger_O_spread[1],
        "qubit_hook": 196*1e-3,
        "squid_taper": 3.5,
    }),
    ]
)

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
