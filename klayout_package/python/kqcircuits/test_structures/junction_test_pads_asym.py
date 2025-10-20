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


import numpy

from kqcircuits.qubits.qubit import Qubit
from kqcircuits.pya_resolver import pya
from kqcircuits.util.parameters import Param, pdt, add_parameters_from
from kqcircuits.test_structures.test_structure import TestStructure
from kqcircuits.defaults import default_junction_test_pads_type
from kqcircuits.test_structures.junction_test_pads import junction_test_pads_type_choices
from kqcircuits.junctions.manhattan import Manhattan
from kqcircuits.junctions.junction import Junction


@add_parameters_from(Manhattan)
@add_parameters_from(Qubit, "junction_type", "junction_width", "loop_area", "mirror_squid")

class JunctionTestPadsAsym(TestStructure):
    """Base class for junction test structures."""

    default_type = default_junction_test_pads_type

    pad_width = Param(pdt.TypeDouble, "Pad width", 500, unit="μm")
    area_height = Param(pdt.TypeDouble, "Area height", 1900, unit="μm")
    area_width = Param(pdt.TypeDouble, "Area width", 1300, unit="μm")
    
    pad_spacing_x = Param(pdt.TypeDouble, "Spacing between different pad pairs x", 100, unit="μm")
    pad_spacing_y = Param(pdt.TypeDouble, "Spacing between different pad pairs y", 200, unit="μm")
    only_pads = Param(pdt.TypeBoolean, "Only produce pads, no junctions", True)
    pad_configuration = Param(pdt.TypeString, "Pad configuration", "2-port", choices=["2-port", "4-port"])
    junction_width_steps = Param(pdt.TypeList, "Automatically generate junction widths [start, step]", [0, 0],
                                 unit="μm, μm")
    junction_widths = Param(pdt.TypeList, "Optional junction widths for individual junctions", [],
                            docstring="Override the junction widths with these values.")
    # junction_test_pads_asym_type = Param(pdt.TypeString, "Type of junction test pads", default_type,
    #                                 choices=junction_test_pads_type_choices)

    # junction_test_pads_asym_parameters = Param(pdt.TypeString, "Extra JunctionTestPads Parameters", "{}")
    # _junction_test_pads_asym_parameters = Param(pdt.TypeString, "Previous state of *_parameters", "{}", hidden=True)

    def build(self):
        self.junction_spacing = 0
        self._produce_impl()


    @classmethod
    def create(cls, layout, library=None, junction_test_pads_type=None, **parameters):
        """Create a JunctionTestPads cell in layout."""
        return cls.create_subtype(layout, library, junction_test_pads_type, **parameters)[0]

    # def coerce_parameters_impl(self):
    #     self.sync_parameters(Junction)
    #     self.sync_parameters(JunctionTestPadsAsym)

    def _produce_impl(self):
        if self.pad_configuration == "2-port":
            self._produce_two_port_junction_tests()

    def _next_junction_width(self, idx):
        """Get the next junction width

        Try first the `junction_widths` list, if available, if not then generate it based on `start`
        and `step`, unless `step` is 0, in this case just use the default `junction_width`.
        """
        start, step = [float(x) for x in self.junction_width_steps]
        if idx < len(self.junction_widths) and self.junction_widths[idx] != '':
            return float(self.junction_widths[idx])
        elif not (start == 0 and step == 0):
            return start + idx * step
        return self.junction_width

    def _produce_two_port_junction_tests(self):

        pads_region = pya.Region()
        pad_step_x = self.pad_spacing_x + self.pad_width
        pad_step_x2 = self.pad_spacing_x + self.pad_spacing_y + 2*self.pad_width
        pad_step_y = self.pad_spacing_y + self.pad_width
        arm_width = 8

        junction_idx = 0
        y_flip = -1 if self.face_ids[0] == '2b1' else 1
        
        # 
        # for x in numpy.arange(self.pad_spacing_x*1.5 + self.pad_width, self.area_width - pad_step_x, 2*pad_step_x,
        #                         dtype=numpy.double):
        for x in numpy.arange(self.pad_spacing_y*2.5 + self.pad_width, self.area_width - pad_step_y, pad_step_x2,
                                dtype=numpy.double):
            for y in numpy.arange(self.pad_spacing_y + self.pad_width*0.5, self.area_height - self.pad_width / 2,
                                    pad_step_y, dtype=numpy.double):
                self.produce_pad(x - pad_step_x / 2, y, pads_region, self.pad_width, self.pad_width)
                self.produce_pad(x + pad_step_x / 2, y, pads_region, self.pad_width, self.pad_width)
                self._next_width = self._next_junction_width(junction_idx)
                # self._produce_junctions(x, y, pads_region, arm_width, junction_idx)
                self.refpoints["probe_{}_l".format(junction_idx)] = pya.DPoint(x - pad_step_x * y_flip / 2, y)
                self.refpoints["probe_{}_r".format(junction_idx)] = pya.DPoint(x + pad_step_x * y_flip/ 2, y)
                junction_idx += 1

        self.produce_etched_region(pads_region, pya.DPoint(self.area_width / 2, self.area_height / 2), self.area_width,
                                   self.area_height)
