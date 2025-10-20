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

from kqcircuits.chips.QQQv3_1 import ChipQQQv31
from kqcircuits.chips.QQQv3_1A import ChipQQQv31A
from kqcircuits.chips.QQQv3_2 import ChipQQQv32
from kqcircuits.chips.QQQv3_1_PIDC import ChipQQQv31IDC
from kqcircuits.chips.QQQv3_1_PISO import ChipQQQv31ISO

from kqcircuits.chips.AMPlogo import LogoNIST
from kqcircuits.chips.NIST_PR_v353 import NISTpart353

from kqcircuits.elements.markers.mask_marker_nist import MaskMarkerNist


mask = MaskSet(
    name="QQQ0925",
    version=3,
    with_grid=True,
    export_path=r"C:\Users\zlp\Documents\Simulation Projects\Main Projects\QQQ_v2\readout_v3\exportGDS",
)

# layout positioning of chips
chip_layout = [["---" for _ in range(15)] for _ in range(15)]

# Main tiling
for i in range(11):
    for j in range(11):
        diag = (i * 11 + j) % 3
        # sdiag = (j*11 - i) % 4
        tempName = f"Q{diag}S{i % 4}"

        # Make 25% of them be the v3.2 readout variant
        if (j + 11*i) % 4 == 0:
            tempName = f"R{diag}S{i % 4}"

        # squids in rows qubit JJs in columns
        # tempName = f"Q{j % 3}S{i % 4}"

        chip_layout[i + 2][j + 2] = tempName

# floating transmon fixed freq tests
chip_layout[7][8] = "PR"
chip_layout[10][12] = "PR"

# # Sprinkle in the Penguins test chips
chip_layout[4][5] = "PQ"
chip_layout[6][10] = "PQ"
chip_layout[8][3] = "PQ"
chip_layout[10][6] = "PQ"

# for other things take more from S0 or S3
# 31A, 32, 31IDC, 31ISO, 31unpump
chip_layout[3][5] = "A1S1"
chip_layout[10][10] = "A1S2"
chip_layout[6][4] = "U1S1"
chip_layout[4][9] = "U1S2"

# PIQUE WITH THE extra cavity
chip_layout[8][5] = "P1S1"
chip_layout[12][5] = "P1S1"
chip_layout[2][10] = "P0S0"
chip_layout[6][7] = "P0S0"
chip_layout[5][2] = "I1S1"
chip_layout[10][7] = "I0S0"

chip_layout[6][8] = "cu"

print(chip_layout)

mask.add_mask_layout(chip_layout, "1t1", mask_name_scale=0.5, mask_markers_dict={MaskMarkerNist: {}})

qubit_finger_spread = [132, 140, 148]
penguin_fingers = [[132, 140, 148][(j // 2) % 3] for i in range(4) for j in range(6)]

squid_finger_spread = [1520, 1880, 2280, 2896]
penguin_squid = [[1520, 1880, 2280, 2896][i] for i in range(4) for j in range(6)]

penguin_params = {
    "Q_bridge_gap": 100 * 1e-3,
    "Q_hook_thickness": 196 * 1e-3,
    "Q_finger_widths": penguin_fingers,
    "S_finger_widths": penguin_squid,
    "S_bridge_gap": 100 * 1e-3,
    "S_taper": 3.5,
}

mask.add_chip([(LogoNIST, "cu")])

# test junctions Penguin
mask.add_chip(
    [
        (JunctionTestQQQ, "PQ", penguin_params),
    ]
)


################

qqq_params = {
    "Q_bridge_gap": 100 * 1e-3,
    "Q_hook_thickness": 0.196,
    "S_bridge_gap": 100 * 1e-3,
    "S_taper": 3.5,
}

# QQQ chip spread
################
mask.add_chip(
    [
        (
            ChipQQQv31,
            "Q0S0",
            {
                "Q_finger_width": qubit_finger_spread[0] * 1e-3,
                "S_finger_width": squid_finger_spread[0] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q0S1",
            {
                "Q_finger_width": qubit_finger_spread[0] * 1e-3,
                "S_finger_width": squid_finger_spread[1] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q0S2",
            {
                "Q_finger_width": qubit_finger_spread[0] * 1e-3,
                "S_finger_width": squid_finger_spread[2] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q0S3",
            {
                "Q_finger_width": qubit_finger_spread[0] * 1e-3,
                "S_finger_width": squid_finger_spread[3] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q1S0",
            {
                "Q_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[0] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q1S1",
            {
                "Q_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[1] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q1S2",
            {
                "Q_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[2] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q1S3",
            {
                "Q_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[3] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q2S0",
            {
                "Q_finger_width": qubit_finger_spread[2] * 1e-3,
                "S_finger_width": squid_finger_spread[0] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q2S1",
            {
                "Q_finger_width": qubit_finger_spread[2] * 1e-3,
                "S_finger_width": squid_finger_spread[1] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q2S2",
            {
                "Q_finger_width": qubit_finger_spread[2] * 1e-3,
                "S_finger_width": squid_finger_spread[2] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "Q2S3",
            {
                "Q_finger_width": qubit_finger_spread[2] * 1e-3,
                "S_finger_width": squid_finger_spread[3] * 1e-3,
                **qqq_params,
            },
        ),
    ]
)

# QQQ32 alt readout
mask.add_chip(
    [
        (
            ChipQQQv32,
            "R0S0",
            {
                "R_finger_width": qubit_finger_spread[0] * 1e-3,
                "S_finger_width": squid_finger_spread[0] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R0S1",
            {
                "R_finger_width": qubit_finger_spread[0] * 1e-3,
                "S_finger_width": squid_finger_spread[1] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R0S2",
            {
                "R_finger_width": qubit_finger_spread[0] * 1e-3,
                "S_finger_width": squid_finger_spread[2] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R0S3",
            {
                "R_finger_width": qubit_finger_spread[0] * 1e-3,
                "S_finger_width": squid_finger_spread[3] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R1S0",
            {
                "R_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[0] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R1S1",
            {
                "R_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[1] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R1S2",
            {
                "R_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[2] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R1S3",
            {
                "R_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[3] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R2S0",
            {
                "R_finger_width": qubit_finger_spread[2] * 1e-3,
                "S_finger_width": squid_finger_spread[0] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R2S1",
            {
                "R_finger_width": qubit_finger_spread[2] * 1e-3,
                "S_finger_width": squid_finger_spread[1] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R2S2",
            {
                "R_finger_width": qubit_finger_spread[2] * 1e-3,
                "S_finger_width": squid_finger_spread[2] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv32,
            "R2S3",
            {
                "R_finger_width": qubit_finger_spread[2] * 1e-3,
                "S_finger_width": squid_finger_spread[3] * 1e-3,
                **qqq_params,
            },
        ),
    ]
)

# PIQUE CHIPS
mask.add_chip(
    [
        (
            ChipQQQv31IDC,
            "P0S0",
            {
                "Q_finger_width": qubit_finger_spread[0] * 1e-3,
                "S_finger_width": squid_finger_spread[0] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31IDC,
            "P1S1",
            {
                "Q_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[1] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31ISO,
            "I0S0",
            {
                "Q_finger_width": qubit_finger_spread[0] * 1e-3,
                "S_finger_width": squid_finger_spread[0] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31ISO,
            "I1S1",
            {
                "Q_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[1] * 1e-3,
                **qqq_params,
            },
        ),
    ]
)

# A qubit only and unpumped
mask.add_chip(
    [
        (
            ChipQQQv31A,
            "A1S1",
            {
                "Q_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[1] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31A,
            "A1S2",
            {
                "Q_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[2] * 1e-3,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "U1S1",
            {
                "Q_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[1] * 1e-3,
                "unpump": True,
                **qqq_params,
            },
        ),
        (
            ChipQQQv31,
            "U1S2",
            {
                "Q_finger_width": qubit_finger_spread[1] * 1e-3,
                "S_finger_width": squid_finger_spread[2] * 1e-3,
                "unpump": True,
                **qqq_params,
            },
        ),
    ]
)

# floating PR hero chips
mask.add_chip(
    [
        (
            NISTpart353,
            "PR",
            {
                "bridge_gap": 0.100,
                "finger_width": qubit_finger_spread[1] * 1e-3,
                "Q_hook_thickness": 0.196,
            },
        )
    ]
)

mask.build()
mask.export()
