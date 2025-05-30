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

from pathlib import Path
from gi.repository import GObject, Gio
from .chapter import Chapter
from .resource import Resource

logger = logging.getLogger(__name__)


class Manuscript(Resource):
    """A manuscript is a collection of scenes and chapters."""
    __gtype_name__ = "Manuscript"

    # Properties of the manuscript
    chapters = GObject.Property(type=Gio.ListStore)
    cover = GObject.Property(type=str)

    def __init__(self, project, identifier):
        """Create a new manuscript."""
        super().__init__(project, identifier)

        # Create the containers for all the main concepts
        self.chapters = Gio.ListStore(item_type=Chapter)

    def get_cover_path(self):
        if self.cover is None or self.cover == '':
            return None

        img_path = self._base_directory / Path("images") / Path(self.cover)
        return img_path.resolve()

    def add_chapter(self, chapter: Chapter, position: int = None):
        """Add an existing chapter to the manuscript."""
        if position is not None and position >= 0:
            self.chapters.insert(position, chapter)
        else:
            self.chapters.append(chapter)

    def splice_chapters(self, source_chapter, target_chapter):
        """Move the source chapter to the position target chapter is at."""
        # Start by finding the positions of each chapter
        found_source, source_position = self.chapters.find(source_chapter)
        found_target, target_position = self.chapters.find(target_chapter)
        if not found_source or not found_target:
            raise KeyError("Could not find the chapters to swap")

        # Now move the source where the target used to be located
        self.chapters.remove(source_position)
        self.chapters.insert(target_position, source_chapter)


