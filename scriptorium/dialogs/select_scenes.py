# dialogs/select_scenes.py
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


@Gtk.Template(resource_path=f"{BASE}/dialogs/select_scenes.ui")
class ScrptSelectScenesDialog(Adw.AlertDialog):
    """Dialog to select scenes."""

    __gtype_name__ = "ScrptSelectScenesDialog"

    scenes_list = Gtk.Template.Child()

    def __init__(self, manuscript_scenes):
        """Create a new instance of the class."""
        super().__init__()

        # Only show unassigned scenes
        self.scenes_list.set_filter_func(self._filter_scenes)

        # Add all the scenes
        for scene in manuscript_scenes:
            entry = Adw.ActionRow(title=scene.title, subtitle=scene.synopsis)
            entry.scene = scene
            self.scenes_list.append(entry)

    def _filter_scenes(self, row):
        """Return True if the scene is not bound to a chapter yet"""
        show_scene = row.scene.chapter is None
        # If we have at least one scene available the user can add it
        if show_scene and not self.get_response_enabled("done"):
            self.set_response_enabled("done", True)
        return show_scene

    def get_selected_scene(self):
        return self.scenes_list.get_selected_row().scene
