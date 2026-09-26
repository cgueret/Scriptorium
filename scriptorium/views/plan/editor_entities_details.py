# views/plan/editor_entities_details.py
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

from gi.repository import Adw, Gtk, GObject

from scriptorium.globals import BASE

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/views/plan/editor_entities_details.ui")
class ScrptEntitiesDetailsPanel(Adw.NavigationPage):
    __gtype_name__ = "ScrptEntitiesDetailsPanel"

    edit_title = Gtk.Template.Child()
    edit_synopsis = Gtk.Template.Child()

    def __init__(self, entity, **kwargs):
        """Create an instance of the panel."""
        super().__init__(**kwargs)

        self._entity = entity

        self.set_title(entity.title)

        # Bind the identifier, title and synopsis
        entity.bind_property(
            "title",
            self.edit_title,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        entity.bind_property(
            "synopsis",
            self.edit_synopsis,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )

    @Gtk.Template.Callback()
    def on_delete_entity_activated(self, _button):
        """Handle a request to delete the scene."""
        logger.info(f"Delete {self._entity.title}")
        dialog = Adw.AlertDialog(
            heading="Delete story element ?",
            body=f'This action can not be undone! Are you sure you want to delete "{self._entity.title}" ?',
            close_response="cancel",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("delete", "Delete")

        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)

        dialog.choose(self, None, self.on_delete_response_selected)

    def on_delete_response_selected(self, _dialog, task):
        """Handle the response to the confirmation dialog."""
        response = _dialog.choose_finish(task)
        if response == "delete":
            # Delete the chapter
            self._entity.project.delete_resource(self._entity)

            # Return to listing the entities
            self.get_parent().pop()
