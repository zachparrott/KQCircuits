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

from kqcircuits.chips.BP_PurcellIDC import PurcellQubitsIDC
from kqcircuits.chips.hanger_cpw import HangerCPW
from kqcircuits.chips.NIST_PR_v3jj import NISTpart3jj

from kqcircuits.elements.markers.marker import Marker
from kqcircuits.elements.markers.mask_marker_nist import MaskMarkerNist
from kqcircuits.pya_resolver import pya

import numpy as np

mask = MaskSet(
    name="BPQ0326",
    version=1,
    # with_grid=False,
    with_grid=True,
    export_path=r"C:\Users\zlp\Documents\Simulation Projects\Main Projects\TWPAqubits\masks",
)

chip_layout = [["---" for _ in range(10)] for _ in range(10)]


full_list = ["C", "S", "L"]

row_widths = [6, 8, 8, 8, 8, 6, 4]

# Main tiling
for i in np.arange(2, 8 + 1):
    shuffled_indices = np.random.permutation(np.arange(row_widths[i - 2]))

    shift = (8 - row_widths[i - 2]) // 2  # Center the row within the 8 columns
    for j in np.arange(1, row_widths[i - 2] + 1):
        s = (i * (11 + 0) + j) % len(full_list)
        tempName = full_list[i % 3] + f"{shuffled_indices[j - 1] % 5}"
        chip_layout[i][shift + j] = tempName
        # chip_layout[i + 0][j + 0] = "C0"

for index, row in enumerate(chip_layout):
    print(index, row)

# Sprinkle in the rest
chip_layout[4][4] = "---"
chip_layout[6][2] = "---"
chip_layout[5][6] = "---"

chip_layout[7][5] = "JJ"

wf = mask.add_mask_layout(
    chip_layout, "1t1", mask_name_scale=0.5, mask_markers_dict={MaskMarkerNist: {}}
)


PR_tuples = [
    (
        "PR1",
        pya.DPoint(-7600, 100),
        pya.DTrans(1, False, 7600, 0),
        "C03",
    ),
    (
        "PR2",
        pya.DPoint(0 + 2 * 7600, 100 - 7600),
        pya.DTrans.R90,
        "D05",
    ),
    (
        "PR3",
        pya.DPoint(0 - 2 * 7600, 100 - 2 * 7600),
        pya.DTrans.R90,
        "E01",
    ),
]

for pr_tuple in PR_tuples:
    wf.extra_chips.append(pr_tuple)


qubit_finger_spread = [100, 120, 152, 180, 200]

################

jj_params = {
    "hook_thickness": 0.1,
    "hook_undercut": 0.5,
    "hook_lead_thickness": 0.2,
    "bridge_gap": 0.150,
    "junction_type": "Overlap2",
    "noSQUID": True,
}

res_lengths_params = {
    "center": [8670, 8580, 8490, 8400],
    "long": (1.01 * np.array([8670, 8580, 8490, 8400])).tolist(),
    "short": (0.99 * np.array([8670, 8580, 8490, 8400])).tolist(),
}
load_params = {
    "center": [501.90, 530.05, 559.87, 589.40],
    "long": (1.01 * np.array([501.90, 530.05, 559.87, 589.40])).tolist(),
    "short": (0.99 * np.array([501.90, 530.05, 559.87, 589.40])).tolist(),
}


# Center resonator dimensions
################
mask.add_chip(
    [
        (
            PurcellQubitsIDC,
            "C0",
            {
                "resonator_lengths": res_lengths_params["center"],
                "qubit_loading": load_params["center"],
                "finger_width": qubit_finger_spread[0] * 1e-3,
                "hanger_ground_width": 2,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "C1",
            {
                "resonator_lengths": res_lengths_params["center"],
                "qubit_loading": load_params["center"],
                "finger_width": qubit_finger_spread[1] * 1e-3,
                "hanger_ground_width": 2,
                "grid_margin": -1,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "C2",
            {
                "resonator_lengths": res_lengths_params["center"],
                "qubit_loading": load_params["center"],
                "finger_width": qubit_finger_spread[2] * 1e-3,
                "hanger_ground_width": 2,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "C3",
            {
                "resonator_lengths": res_lengths_params["center"],
                "qubit_loading": load_params["center"],
                "finger_width": qubit_finger_spread[3] * 1e-3,
                "hanger_ground_width": 2,
                "grid_margin": -1,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "C4",
            {
                "resonator_lengths": res_lengths_params["center"],
                "qubit_loading": load_params["center"],
                "finger_width": qubit_finger_spread[4] * 1e-3,
                "hanger_ground_width": 2,
                **jj_params,
            },
        ),
    ],
    cpus=4,
)
mask.add_chip(
    [
        (
            PurcellQubitsIDC,
            "S0",
            {
                "resonator_lengths": res_lengths_params["short"],
                "qubit_loading": load_params["short"],
                "finger_width": qubit_finger_spread[0] * 1e-3,
                "hanger_ground_width": 3,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "S1",
            {
                "resonator_lengths": res_lengths_params["short"],
                "qubit_loading": load_params["short"],
                "finger_width": qubit_finger_spread[1] * 1e-3,
                "hanger_ground_width": 3,
                "grid_margin": -1,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "S2",
            {
                "resonator_lengths": res_lengths_params["short"],
                "qubit_loading": load_params["short"],
                "finger_width": qubit_finger_spread[2] * 1e-3,
                "hanger_ground_width": 3,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "S3",
            {
                "resonator_lengths": res_lengths_params["short"],
                "qubit_loading": load_params["short"],
                "finger_width": qubit_finger_spread[3] * 1e-3,
                "hanger_ground_width": 3,
                "grid_margin": -1,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "S4",
            {
                "resonator_lengths": res_lengths_params["short"],
                "qubit_loading": load_params["short"],
                "finger_width": qubit_finger_spread[4] * 1e-3,
                "hanger_ground_width": 3,
                **jj_params,
            },
        ),
    ],
    cpus=4,
)
mask.add_chip(
    [
        (
            PurcellQubitsIDC,
            "L0",
            {
                "resonator_lengths": res_lengths_params["long"],
                "qubit_loading": load_params["long"],
                "finger_width": qubit_finger_spread[0] * 1e-3,
                "hanger_ground_width": 4,
                "grid_margin": -1,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "L1",
            {
                "resonator_lengths": res_lengths_params["long"],
                "qubit_loading": load_params["long"],
                "finger_width": qubit_finger_spread[1] * 1e-3,
                "hanger_ground_width": 4,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "L2",
            {
                "resonator_lengths": res_lengths_params["long"],
                "qubit_loading": load_params["long"],
                "finger_width": qubit_finger_spread[2] * 1e-3,
                "hanger_ground_width": 4,
                "grid_margin": -1,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "L3",
            {
                "resonator_lengths": res_lengths_params["long"],
                "qubit_loading": load_params["long"],
                "finger_width": qubit_finger_spread[3] * 1e-3,
                "hanger_ground_width": 4,
                **jj_params,
            },
        ),
        (
            PurcellQubitsIDC,
            "L4",
            {
                "resonator_lengths": res_lengths_params["long"],
                "qubit_loading": load_params["long"],
                "finger_width": qubit_finger_spread[4] * 1e-3,
                "hanger_ground_width": 4,
                "grid_margin": -1,
                **jj_params,
            },
        ),
    ],
    cpus=4,
)
mask.add_chip(
    [
        (
            NISTpart3jj,
            "PR1",
            {
                "finger_width": qubit_finger_spread[1] * 1e-3,
                **jj_params,
            },
        ),
        (
            NISTpart3jj,
            "PR3",
            {
                "finger_width": qubit_finger_spread[3] * 1e-3,
                **jj_params,
            },
        ),
        (
            NISTpart3jj,
            "PR2",
            {
                "finger_width": qubit_finger_spread[2] * 1e-3,
                **jj_params,
            },
        ),
        (
            HangerCPW,
            "JJ",
        ),
    ],
    cpus=4,
)

mask.build()
mask.export()
