# models/entity.py
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
"""An entity is a story element (person, place, prop, ...)"""

from gi.repository import GObject
from .resource import Resource

import logging

logger = logging.getLogger(__name__)


class Entity(Resource):
    """An entity is a story element (person, place, prop, ...)"""

    __gtype_name__ = "Entity"

    category = GObject.Property(type=str)

    _manuscript = None

    def __init__(self, project, identifier: str):
        """Create an entity."""
        super().__init__(project, identifier)

    @GObject.Property(type=GObject.Object)
    def manuscript(self):
        """Return the manuscript the entity is associated to."""
        return self._manuscript

    def delete(self):
        """Delete the entity."""
        found, position = self._manuscript.entities.find(self)
        if not found:
            raise ValueError("The entity is already deleted")

        # Remove the references to this entity from every scene
        for scene in self._manuscript.scenes:
            scene.disconnect_from(self)

        # Remove the entity from the manuscript
        self._manuscript.entities.remove(position)
