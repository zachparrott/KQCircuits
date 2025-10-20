# This code is part of KQCircuits
# Copyright (C) 2023 IQM Finland Oy
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

from kqcircuits.elements.capacitive_x_coupler import CapacitiveXCoupler
from kqcircuits.pya_resolver import pya


def test_can_create(get_simulation):
    get_simulation(CapacitiveXCoupler, box=pya.DBox(pya.DPoint(-250, -250), pya.DPoint(250, 250)))


# TODO: refactor so box doesn't need to be specified.
def test_ansys_export_produces_output_files(perform_test_ansys_export_produces_output_files):
    perform_test_ansys_export_produces_output_files(
        CapacitiveXCoupler, box=pya.DBox(pya.DPoint(-250, -250), pya.DPoint(250, 250))
    )


def test_sonnet_export_produces_output_files(perform_test_sonnet_export_produces_output_files):
    perform_test_sonnet_export_produces_output_files(
        CapacitiveXCoupler, box=pya.DBox(pya.DPoint(-250, -250), pya.DPoint(250, 250))
    )
