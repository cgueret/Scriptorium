# dialogs/select_entities.py
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
"""Dialog to select scenes in Scriptorium."""

from gi.repository import Adw, Gtk
from scriptorium.globals import BASE

import logging

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/dialogs/select_entities.ui")
class ScrptSelectEntitiesDialog(Adw.AlertDialog):
    """Dialog to select story elements."""

    __gtype_name__ = "ScrptSelectEntitiesDialog"

    list_box = Gtk.Template.Child()

    def __init__(self, scene, entities):
        """Create a new instance of the class."""
        super().__init__()
        self._scene = scene

        # Only show unassigned elements
        self.list_box.set_filter_func(self._filter)

        # Add all the scenes
        for entity in entities:
            entry = Adw.ActionRow(title=entity.title, subtitle=entity.synopsis)
            entry.entity = entity
            self.list_box.append(entry)

    def _filter(self, row):
        """Return True if the element is not already associated to the scene"""
        show = row.entity not in self._scene.entities
        # If we have at least one scene available the user can add it
        if show and not self.get_response_enabled("done"):
            self.set_response_enabled("done", True)
        return show

    def get_selected_entity(self):
        return self.list_box.get_selected_row().entity
