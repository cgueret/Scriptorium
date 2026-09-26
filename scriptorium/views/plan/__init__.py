# views/plan/__init__.py
#
# Copyright 2025 Christophe Gueret
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
The plan view is used to managed different facets of a manuscript.

This is different from the writing and publishing views respectively focused
on the content and the styling+export of the manuscript.
"""

from .page import PlanPage
from .editor_entities import ScrptEntityPanel
from .editor_entities_details import ScrptEntitiesDetailsPanel

__all__ = [
    "PlanPage",
    "ScrptEntityPanel",
    "ScrptEntitiesDetailsPanel",
    "ScrptScenesPanel",
    "ScrptScenesDetailsPanel",
]
