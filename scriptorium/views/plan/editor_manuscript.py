# views/plan/editor_manuscript.py
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
"""Editor panel to select and work on the scenes."""

import logging

from gi.repository import Adw, Gtk, GObject, Gio

from scriptorium.globals import BASE


logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/views/plan/editor_manuscript.ui")
class ScrptManuscriptPanel(Adw.NavigationPage):
    __gtype_name__ = "ScrptManuscriptPanel"
    __icon_name__ = "dictionary-symbolic"

    __title__ = _("Description")
    __description__ = _("Edit the information about the manuscript")

    identifier = Gtk.Template.Child()
    edit_title = Gtk.Template.Child()
    edit_synopsis = Gtk.Template.Child()
    cover_stack = Gtk.Template.Child()
    cover_picture = Gtk.Template.Child()
    cover_edit_button = Gtk.Template.Child()

    def __init__(self, editor, **kwargs):
        """Create an instance of the panel."""
        super().__init__(**kwargs)

        self._editor = editor
        self.set_title(self.__title__)

        # Bind the identifier, title and synopsis
        editor.project.manuscript.bind_property(
            "identifier",
            self.identifier,
            "subtitle",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        editor.project.manuscript.bind_property(
            "title",
            self.edit_title,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        editor.project.manuscript.bind_property(
            "synopsis",
            self.edit_synopsis,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )

        # Update the cover and keep an eye on further changes
        self.update_cover()
        editor.project.manuscript.connect(
            "notify::cover", lambda _src, _val: self.update_cover()
        )

        menu = Gio.Menu()
        menu.append(
            label = "Import a new cover",
            detailed_action = "editor.import_cover"
        )
        menu.append(
            label = "Remove cover",
            detailed_action = "editor.set_cover('')"
        )
        self.cover_edit_button.set_menu_model(menu)

    def create_message_entry(self, message):
        """Add a message to the history."""
        message_entry = Adw.ActionRow()
        message_entry.add_css_class("property")
        message_entry.set_title(message.datetime)
        message_entry.set_subtitle(message.message)
        return message_entry

    def on_delete_response_selected(self, _dialog, task):
        """Handle the response to the confirmation dialog."""
        response = _dialog.choose_finish(task)
        if response == "delete":
            # Delete the manuscript
            library = self._editor.project.library
            library.delete_project(self._editor.project)

            # Pop the navigation
            self._editor.close_on_delete()

    def update_cover(self):
        """Update the display of the cover."""
        cover_image = self._editor.project.manuscript.cover
        logger.info(f"Update cover to {cover_image}")

        if cover_image is not None:
            self.cover_picture.set_paintable(cover_image.texture)
            self.cover_stack.set_visible_child_name("image_set")
        else:
            self.cover_picture.set_paintable(None)
            self.cover_stack.set_visible_child_name("no_image_set")

