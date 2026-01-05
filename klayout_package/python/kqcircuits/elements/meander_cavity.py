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

from math import pi
from kqcircuits.pya_resolver import pya
from kqcircuits.elements.element import Element

from kqcircuits.util.parameters import Param, pdt, add_parameters_from, add_parameter
from kqcircuits.elements.launcher import Launcher
from kqcircuits.elements.waveguide_coplanar import WaveguideCoplanar
from kqcircuits.elements.waveguide_composite import WaveguideComposite, Node
from kqcircuits.elements.hanger_resonator import HangerResonator
from kqcircuits.elements.meander import Meander

from kqcircuits.util.refpoints import WaveguideToSimPort


@add_parameters_from(Element, b = 4, a = 8, margin=100)
class MeanderCavity(Element):
    length = Param(pdt.TypeDouble, "resonator length", 8000, unit="μm")

    def build(self):

        self.insert_cell(
            WaveguideComposite,
            nodes=[
                Node(pya.DPoint(-900, 0)),
                Node(pya.DPoint(-500, 0), ab_across=True),
                Node(
                    pya.DPoint(500, 0), 
                    length_before=self.length - 800,
                    ab_across=True,
                    # n_bridges = -1,
                    ),
                Node(pya.DPoint(900, 0)),
            ],
            term1 = 15,
            term2 = 15,
            r=50,
        )
