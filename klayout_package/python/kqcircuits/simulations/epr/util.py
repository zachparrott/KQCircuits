# This code is part of KQCircuits
# Copyright (C) 2024 IQM Finland Oy
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

import logging
from typing import Callable
from kqcircuits.elements.element import Element
from kqcircuits.simulations.simulation import Simulation
from kqcircuits.simulations.partition_region import PartitionRegion
from kqcircuits.pya_resolver import pya


EPRTarget = Simulation | Element


def in_gui(element: EPRTarget) -> bool:
    """``partition_regions`` and ``correction_cuts`` can be called for elements
    when KLayout is in GUI mode, in which case element is not of type Simulation.
    This check can be used if ``partition_regions`` and ``correction_cuts``
    implementations use ``Simulation`` specific attributes and methods like
    ``box`` or ``face_stack``. If True is returned, some alternative
    attributes need to be used.
    """
    return not isinstance(element, Simulation)


def get_mer_z(element: EPRTarget, face_base: str) -> float:
    """Determines z position of a MER box postitioned at the base of the face
    given ``face_base`` as face id string."""
    if in_gui(element):
        return 0
    z_levels = element.face_z_levels()
    if face_base not in z_levels:
        logging.warning(
            f"Couldn't get z coordinate of face {face_base}, "
            "please check how 'face_stack' is defined. Defaulting to 0 for MER box."
        )
        return 0
    return z_levels[face_base][0]


def extract_child_simulation(
    simulation: EPRTarget,
    refpoint_prefix: str | None = None,
    parameter_remap_function: Callable[[EPRTarget, str], any] | None = None,
    needed_parameters: list[str] | None = None,
) -> Simulation:
    """Given a simulation object that builds multiple elements within it,
    extracts a "child simulation" which is a stub object that only contains
    minimal set of refpoints and parameters from which element specific
    parition regions and correction cuts can be derived.

    When defining parition regions and correction cuts for an element
    under ``kqcircuits.simulations.epr``, it is recommended to create
    a function that takes arguments ``(simulation, refpoint_prefix, parameter_remap_function)``
    that passes the arguments to ``extract_child_simulation`` and explicitly
    lists ``needed_parameters``. See ``kqcircuits.simulations.epr.example``.

    Args:
        simulation: Simulation object that contains needed child simulation
        refpoint_prefix: Child simulation refpoints usually have a common prefix
            in refpoint names, which identify that the refpoint belongs to that child.
        parameter_remap_function: If ``simulation`` defines parameters that overrides
            parameters of the needed child simulation, these parameters should be mapped
            for the partition region and correction cut extraction functions to work.
            For example, suppose the correction cut location of some qubit is defined
            relative to its ``a`` parameter. But when the ``simulation`` inserts
            the qubit, it overrides qubit's ``a`` parameter with ``simulation``s
            ``qubit_a`` parameter. ``parameter_remap_function`` should be such that
            ``parameter_remap_function(simulation, "a") = simulation.qubit_a``.
        needed_parameters: List of all parameters that are needed to derive
            parition regions and correction cuts for needed child simulation.

    Returns:
        A "simulation object" that only contains minimal set of refpoints and parameters
        from which element specific parition regions and correction cuts can be derived.
        The result is a stub simulation object, so it doesn't have well defined
        build function or any features that would be useful to export a simulation by itself.
    """
    child_simulation = Simulation(simulation.layout)
    child_simulation.refpoints = (
        {
            # Strip away prefix to make this refpoint your own
            ref_name[len(refpoint_prefix) :]: ref_point
            for ref_name, ref_point in simulation.refpoints.items()
            if ref_name.startswith(refpoint_prefix)
        }
        if refpoint_prefix
        else dict(simulation.refpoints)
    )
    # Add default simulation parameters that should always be included
    needed_parameters = set(
        needed_parameters
        + [
            "face_ids",
            "face_stack",
            "lower_box_height",
            "upper_box_height",
            "substrate_height",
            "metal_height",
            "dielectric_height",
            "chip_distance",
        ]
    )
    for parameter in needed_parameters:
        if parameter_remap_function:
            value = parameter_remap_function(simulation, parameter)
        else:
            value = getattr(simulation, parameter)
        setattr(child_simulation, parameter, value)
    return child_simulation


def create_bulk_and_mer_partition_regions(
    name: str = "part",
    face: str | None = None,
    metal_edge_dimensions: list[float | None] | float | None = None,
    region: pya.DBox | pya.DPolygon | list[pya.DBox] | list[pya.DPolygon] | pya.Region | None = None,
    vertical_dimensions: list[float | None] | float | None = None,
    visualise: bool = True,
    mer: bool = True,
    bulk: bool = True,
) -> list[PartitionRegion]:
    """
    Creates both bulk and mer partition regions for element.
    """
    result = []
    if mer:
        result.append(
            PartitionRegion(
                name=f"{name}mer",
                face=face,
                metal_edge_dimensions=metal_edge_dimensions,
                region=region,
                vertical_dimensions=vertical_dimensions,
                visualise=visualise,
            )
        )
    if bulk:
        result.append(
            PartitionRegion(
                name=f"{name}bulk",
                face=face,
                metal_edge_dimensions=None,
                region=region,
                vertical_dimensions=vertical_dimensions,
                visualise=visualise,
            )
        )
    return result
