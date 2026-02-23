# Copyright (C) 2026 Zachary Parrott
# Copyright (C) 2021 IQM Finland Oy
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see
# https://www.gnu.org/licenses/gpl-3.0.html.
#
# The software distribution should follow IQM trademark policy for open-source software
# (meetiqm.com/iqm-open-source-trademark-policy). IQM welcomes contributions to the code.
# Please see our contribution agreements for individuals (meetiqm.com/iqm-individual-contributor-license-agreement)
# and organizations (meetiqm.com/iqm-organization-contributor-license-agreement).
"""
Compute the corresponding effective grounded transmon cpacitance matrix from the floating transmon capacitance matrix.

This produces the "SPICE" matrix. No off diagonal contributions to the main elements.
"""

import os
from post_process_helpers import find_varied_parameters, tabulate_into_csv, load_json

def _effective_qubit_shunt_capacitance(cmatrix, mapping=None):
    """Compute the effective grounded transmon capacitance matrix from the floating transmon capacitance matrix.

    The signal nets are consistently the following mapping:
    Coupler: 2
    near pad: 1
    far pad: 3
    todo: optional override of this mapping   

    Args:
        cmatrix (dict): Dictionary containing the floating transmon capacitance matrix elements.
    Returns:
        dict: Dictionary containing the effective grounded transmon capacitance matrix elements.
    """
    if mapping is not None:
        raise NotImplementedError("Custom mapping is not implemented yet.") 
    else:
        C1g = cmatrix["C11"]
        C2g = cmatrix["C33"]
        Crg = cmatrix["C22"]
        C12 = cmatrix["C13"]
        C1r = cmatrix["C12"]
        C2r = cmatrix["C23"]

    Cq_eff = C12 + (C1g + C1r) * (C2g + C2r) / (C1g + C2g + C1r + C2r)
    Cqr = (C1r * C2g - C2r * C1g) / (C1g + C2g + C1r + C2r)
    Cr_eff = Crg + C1r + C2r - (C1r + C2r) ** 2 / (C1g + C2g + C1r + C2r)

    Ceffective = {
        "Cqq": Cq_eff - Cqr,
        "Cqr": Cqr,
        "Crr": Cr_eff - Cqr,
    }
    return Ceffective

# Find data files
path = os.path.curdir
result_files = [f for f in os.listdir(path) if f.endswith("_project_results.json")]
if result_files:
    # Find parameters that are swept
    definition_files = [
        f.replace("_project_results.json", ".json") for f in result_files
    ]
    parameters, parameter_values = find_varied_parameters(definition_files)

    # Load result data
    cmatrix = {}
    Ceffective_all = {}
    for key, result_file in zip(parameter_values.keys(), result_files):
        result = load_json(result_file)
        cdata = result.get("CMatrix") or result.get("Cs")
        if cdata is None:
            print(f"Neither 'CMatrix' nor 'Cs' found in the result file {result_file}")
            continue

        cmatrix[key] = {
            f"C{i + 1}{j + 1}": c
            for i, row in enumerate(cdata)
            for j, c in enumerate(row)
        }
        
        Ceffective_all[key] = _effective_qubit_shunt_capacitance(cmatrix[key])
        
    tabulate_into_csv(
        f"{os.path.basename(os.path.abspath(path))}_effectiveGrounded_results.csv",
        Ceffective_all,
        parameters,
        parameter_values,
    )
