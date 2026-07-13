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

from kqcircuits.chips.junction_test_QQQ import JunctionTestQQQ
from kqcircuits.chips.junction_test_QCC import JunctionTestQCC
from kqcircuits.chips.junction_test_QCCdouble import JunctionTestQCCDouble

from kqcircuits.chips.QQQv2 import ChipQQQv2
from kqcircuits.chips.QQQv2_unpump import ChipQQQv2Unpump
from kqcircuits.chips.QQQv2_PIDC import ChipQQQv2PIDC
from kqcircuits.chips.QQQv2_PISO import ChipQQQv2PISO

from kqcircuits.chips.xmons_direct_coupling import XMonsDirectCoupling
from kqcircuits.chips.NIST_PR_v353 import NISTpart353

from kqcircuits.chips.QCCv2_single import ChipQCCv2Single
from kqcircuits.chips.QCCv2_single_unpump import ChipQCCv2SingleUnpump
from kqcircuits.chips.QCCv2_double import ChipQCCv2Double

from kqcircuits.elements.markers.marker import Marker
from kqcircuits.elements.markers.mask_marker_nist import MaskMarkerNist

mask = MaskSet(name="QQQ0225", version=1, with_grid=False, export_path=r"C:\Users\zlp\Documents\Simulation Projects\Main Projects\QQQ_v2\KQCircuit Exports")

chip_layout = [["---" for _ in range(15)] for _ in range(15)]


full_list = ["Q", "Q", "CS", "CD"]

# Main tiling
for i in range(11):    
    for j in range(11):
        s = (i*(11+0) + j) % len(full_list)
        if full_list[s] == "PQ":
            tempName = full_list[s]
        else:
            tempName = full_list[s] + f"{i % 3}"
        chip_layout[i+2][j+2] = tempName

# Sprinkle in the unpumped
chip_layout[10][6] = "QU2"
chip_layout[9][5] = "QU1"
chip_layout[11][7] = "QU0"

chip_layout[10][4] = "CSU2"
chip_layout[9][3] = "CSU1"
chip_layout[11][5] = "CSU0"

chip_layout[5][2] = "IDC"
chip_layout[6][2] = "ISO"

chip_layout[3][5] = "PR"

# Sprinkle in the Penguins
chip_layout[5][10] = "PQ"
chip_layout[10][10] = "PQ"
chip_layout[4][10] = "PCS"
chip_layout[10][9] = "PCD"

mask.add_mask_layout(chip_layout, "1t1", mask_name_scale=0.5, mask_markers_dict={MaskMarkerNist: {}})

# SQUID dimension 1276
# qubit dimension 100x148, 140, 132
#
# QCC stick with the 100x100 JJ 11.5 kOhm
# 3500 wide JJ 85 double 43 single
# 3500 wide JJ 93 double 47 single
# QCC stick with the 100x148 JJ 8.7 kOhm
# 3500 wide JJ 61 double 31 single
# 3500 wide JJ 69 double 35 single

qubit_finger_spread = [[148, 140, 132],[124, 116, 108]]
squid_finger_O_spread = [[1276, 1276, 1276],[1276, 1276, 1276]]

penguin_fingers = [x for sublist in qubit_finger_spread for x in sublist for _ in range(3)]
penguin_squid = [x for sublist in squid_finger_O_spread for x in sublist for _ in range(3)]

array_finger_spread = [[3500, 3500, 3500], [3500, 3500, 3500], [3500, 3500, 3500]]
penguin_array_widths = [x for sublist in array_finger_spread for x in sublist for _ in range(2)]
penguin_double_array_widths = penguin_array_widths

penguin_numbers = [47, 45, 47, 45, 47, 45, 43, 35, 43, 35, 43, 35, 33, 31, 33, 31, 33, 31, 33, 31]
penguin_double_numbers = [93, 89, 93, 89, 93, 89, 85, 69, 85, 69, 85, 69, 67, 61, 33, 61, 67, 61, 67, 61]

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

mask.add_chip([(JunctionTestQQQ, "PQ", penguin), 
               (JunctionTestQCC, "PCS", penguin_array), 
               (JunctionTestQCCDouble, "PCD", penguin_double_array)
               ])

QQQ_fingers = [148, 140, 132]
QCC_fingers = [100, 100, 148, 148]
QCC_s_arrays = [43, 47, 31, 34]
QCC_d_arrays = [85, 93, 61, 69]

################

qqq_params = {'Q_bridge_gap': 100 * 1e-3,
            'Q_hook_thickness': 0.196,
            'S_finger_width': 1.272,
            'S_bridge_gap': 100 * 1e-3,
            'S_hook_thickness': 2,  }

# QQQ chip spread
################
mask.add_chip(
    [
        (ChipQQQv2, "Q0",
         {
            'Q_finger_width': QQQ_fingers[0]* 1e-3,
            **qqq_params                   
        }),
        (ChipQQQv2, "Q1", {
            'Q_finger_width': QQQ_fingers[1]* 1e-3,
            **qqq_params                         
        }),
        (ChipQQQv2, "Q2", {
            'Q_finger_width': QQQ_fingers[2]* 1e-3,
            **qqq_params                         
        }),
    ],
    cpus=2,
)
# list comprehension doesnt work in console script
# mask.add_chip([
#     (ChipQQQv2, f"Q{s}", {
#         'Q_finger_width': QQQ_fingers[s]* 1e-3,
#         'Q_bridge_gap': 100 * 1e-3,
#         'Q_hook_thickness': 0.196,
#         'S_finger_width': 1.272,
#         'S_bridge_gap': 100 * 1e-3,
#         'S_hook_thickness': 2,
#     })
#     for s in range(3)
# ])

mask.add_chip([(ChipQQQv2PIDC, "IDC", {
        'Q_finger_width': QQQ_fingers[0]* 1e-3,
        **qqq_params                        
    }),
    (ChipQQQv2PISO, "ISO", {
        'Q_finger_width': QQQ_fingers[0]* 1e-3,
        **qqq_params                         
    })])
# need to fix hangers like in Bandpass purcell
# mask.add_chip([(NISTpart353, "PR", {
#     'bridge_gap': 0.100, 'finger_width': QQQ_fingers[0] * 1e-3,
#     'Q_hook_thickness': 0.196,}
#     )])


mask.add_chip([
    (ChipQQQv2Unpump, f"QU0", {
        'Q_finger_width': QQQ_fingers[0]* 1e-3,        
        **qqq_params,                   
        'S_finger_width': 0.954,
        
    }),
    (ChipQQQv2Unpump, f"QU1", {
        'Q_finger_width': QQQ_fingers[0]* 1e-3,
        **qqq_params,                   
        'S_finger_width': 0.954,      
    }),
    (ChipQQQv2Unpump, f"QU2", {
        'Q_finger_width': QQQ_fingers[2]* 1e-3,
        **qqq_params,                   
        'S_finger_width': 0.954,       
    }),
])

################
# QCC chip spread
################
# Single junction array
qccsingle_params = {
    'Q_bridge_gap': 100 * 1e-3,
    'Q_hook_thickness': 0.196,
    'S_finger_width': 1.272,
    'S_bridge_gap': 100 * 1e-3,
    'S_hook_thickness': 2,  
    'A_bridge_gap': 0.194,
    'A_gap_spacing': 0.8,
    'A_bridge_length': 3.5,
}

mask.add_chip([
    (ChipQCCv2Single, f"CS0", {
        'Q_finger_width': QCC_fingers[0]* 1e-3,        
        'A_junction_number': QCC_s_arrays[0],  
        ** qccsingle_params    
    }),
    (ChipQCCv2Single, f"CS1", {
        'Q_finger_width': QCC_fingers[1]* 1e-3,
        'A_junction_number': QCC_s_arrays[1],  
        ** qccsingle_params    
    }),
    (ChipQCCv2Single, f"CS2", {
        'Q_finger_width': QCC_fingers[2]* 1e-3,
        'A_junction_number': QCC_s_arrays[2],  
        ** qccsingle_params    
    }),
    (ChipQCCv2Single, f"CS3", {
        'Q_finger_width': QCC_fingers[3]* 1e-3,
        'A_junction_number': QCC_s_arrays[3],  
        ** qccsingle_params    
    }),
])

mask.add_chip([
    (ChipQCCv2SingleUnpump, f"CSU0", {
        'Q_finger_width': QCC_fingers[0]* 1e-3,        
        'A_junction_number': QCC_s_arrays[0],  
        ** qccsingle_params,
        'S_finger_width': 0.954,     
    }),
    (ChipQCCv2SingleUnpump, f"CSU1", {
        'Q_finger_width': QCC_fingers[1]* 1e-3,
        'A_junction_number': QCC_s_arrays[1],  
        ** qccsingle_params,
        'S_finger_width': 0.954, 
    }),
    (ChipQCCv2SingleUnpump, f"CSU2", {
        'Q_finger_width': QCC_fingers[2]* 1e-3,
        'A_junction_number': QCC_s_arrays[2],  
        ** qccsingle_params,
        'S_finger_width': 0.954, 
    }),
])

qccdouble_params = {
    'Q_bridge_gap': 100 * 1e-3,
    'Q_hook_thickness': 0.196,
    'S_finger_width': 1.272,
    'S_bridge_gap': 100 * 1e-3,
    'S_hook_thickness': 2,  
    'A_bridge_gap': 0.194,
    'A_gap_spacing': 0.8,
    'A_bridge_length': 3.5,
}
# Double junction array
mask.add_chip([
    (ChipQCCv2Double, f"CD0", {
        'Q_finger_width': QCC_fingers[0]* 1e-3,
        'A_junction_number': QCC_d_arrays[0],  
        **qccdouble_params,    
    }),
    (ChipQCCv2Double, f"CD1", {
        'Q_finger_width': QCC_fingers[1]* 1e-3,
        'A_junction_number': QCC_d_arrays[1],  
        **qccdouble_params,    
    }),
    (ChipQCCv2Double, f"CD2", {
        'Q_finger_width': QCC_fingers[2]* 1e-3,
        'A_junction_number': QCC_d_arrays[2],  
        **qccdouble_params,    
    }),
    (ChipQCCv2Double, f"CD3", {
        'Q_finger_width': QCC_fingers[3]* 1e-3,
        'A_junction_number': QCC_d_arrays[3],  
        **qccdouble_params,    
    }),
])

mask.build()
mask.export()
