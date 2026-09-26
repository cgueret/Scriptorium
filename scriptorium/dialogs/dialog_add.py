# dialog_add_scene.py
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
"""Dialog to add a new entity in Scriptorium."""

import logging

from gi.repository import Adw, GObject, Gtk

from scriptorium.globals import BASE

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/dialogs/dialog_add.ui")
class ScrptAddDialog(Adw.AlertDialog):
    """Dialog to add a new scene."""

    __gtype_name__ = "ScrptAddDialog"

    title = GObject.Property(type=str)
    synopsis = GObject.Property(type=str)

    def __init__(self, name, **kwargs):
        """Create a new instance of the class."""
        super().__init__(**kwargs)

        self.set_heading(f"Add a new {name}")

    @Gtk.Template.Callback()
    def on_title_changed(self, entry_row):
        """Check the length of the title."""
        new_title = entry_row.get_text()
        self.set_response_enabled("add", len(new_title) > 1)
