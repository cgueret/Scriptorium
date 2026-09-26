# widgets/multiline_entry_row.py
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

import logging

from gi.repository import Adw, Gtk, GObject
from scriptorium.globals import BASE

logger = logging.getLogger(__name__)

# TODO: check SizeGroup to have the small and big labels overlap
# https://gnome-team.pages.debian.net/blueprint-compiler/examples.html#widget-specific-items


@Gtk.Template(resource_path=f"{BASE}/widgets/multiline_entry_row.ui")
class MultiLineEntryRow(Adw.PreferencesRow):
    __gtype_name__ = "MultiLineEntryRow"

    header = GObject.Property(type=str)
    text = GObject.Property(type=str)

    content = Gtk.Template.Child()
    edit_icon = Gtk.Template.Child()
    title = Gtk.Template.Child()

    def __init__(self, **kwargs):
        """Create an instance of the panel."""
        super().__init__(**kwargs)

        # Bind our text property to the matching one in TextView
        self.bind_property(
            "text",
            self.content.get_buffer(),
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )

    @Gtk.Template.Callback()
    def on_state_flags_changed(self, _content, _flags):
        """Set the entry as focused."""
        if self.content.is_focus():
            self.add_css_class("focused")
            self.edit_icon.hide()
        else:
            self.remove_css_class("focused")
            self.edit_icon.show()
