# models/manuscript.py
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
"""Model for storing information about manuscripts and their content."""

import logging

from gi.repository import GObject, Gio
from .chapter import Chapter
from .scene import Scene
from .resource import Resource
from .image import Image

logger = logging.getLogger(__name__)


class Manuscript(Resource):
    """A manuscript is a collection of scenes and chapters."""
    __gtype_name__ = "Manuscript"

    # Properties of the manuscript
    content = GObject.Property(type=Gio.ListStore)

    # The cover of the manuscript
    cover = GObject.Property(type=Image)

    # The language of the manuscript
    language = GObject.Property(type=str, default="en")

    def __init__(self, project, identifier):
        """Create a new manuscript."""
        super().__init__(project, identifier)

        # Create the containers for all the content of the manuscript
        self.content = Gio.ListStore(item_type=Resource)

    def add_resource(self, resource: Resource, position: int = None) -> bool:
        """Add an existing resource to the manuscript."""
        # We can only accept either a Chapter or a Scene
        if not isinstance(resource, (Chapter, Scene)):
            return False

        if position is not None and position >= 0:
            self.content.insert(position, resource)
        else:
            self.content.append(resource)

        return True

    def splice_chapters(self, source_chapter, target_chapter):
        """Move the source chapter to the position target chapter is at."""
        # Start by finding the positions of each chapter
        found_source, source_position = self.content.find(source_chapter)
        found_target, target_position = self.content.find(target_chapter)
        if not found_source or not found_target:
            raise KeyError("Could not find the chapters to swap")

        # Now move the source where the target used to be located
        self.content.remove(source_position)
        self.content.insert(target_position, source_chapter)


