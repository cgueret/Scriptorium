# views/plan/editor_scenes_details.py
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
from scriptorium.dialogs import ScrptSelectEntitiesDialog
from scriptorium.widgets import EntityCard

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/views/plan/editor_scenes_details.ui")
class ScrptScenesDetailsPanel(Adw.NavigationPage):
    __gtype_name__ = "ScrptScenesDetailsPanel"

    edit_title = Gtk.Template.Child()
    edit_synopsis = Gtk.Template.Child()
    identifier = Gtk.Template.Child()
    history_list = Gtk.Template.Child()
    entities_list = Gtk.Template.Child()
    assign_remove_stack = Gtk.Template.Child()

    def __init__(self, scene):
        """Create an instance of the panel."""
        super().__init__()

        self._scene = scene
        self.set_title(scene.title)

        # Bind the identifier, title and synopsis
        scene.bind_property(
            "identifier",
            self.identifier,
            "subtitle",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        scene.bind_property(
            "title",
            self.edit_title,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        scene.bind_property(
            "synopsis",
            self.edit_synopsis,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )

        self.history_list.bind_model(scene.history, self.create_message_entry)
        self.entities_list.bind_model(
            scene.entities, lambda entity: EntityCard(entity, can_move=True)
        )

        self.entities_list.connect(
            "start-drag",
            lambda x: self.assign_remove_stack.set_visible_child_name("remove"),
        )
        self.entities_list.connect(
            "stop-drag",
            lambda x: self.assign_remove_stack.set_visible_child_name("assign"),
        )

    @Gtk.Template.Callback()
    def on_droptarget_drop(self, _target, _entity, _x, _y):
        # We do not need to do anything special, just accept the drop
        return True

    def create_message_entry(self, message):
        """Bind a scene card to a scene."""
        message_entry = Adw.ActionRow()
        message_entry.add_css_class("property")
        message_entry.set_title(message.datetime)
        message_entry.set_subtitle(message.message)
        return message_entry

    @Gtk.Template.Callback()
    def on_delete_scene_activated(self, _button):
        """Handle a request to delete the scene."""
        logger.info(f"Delete {self._scene.title}")
        dialog = Adw.AlertDialog(
            heading="Delete scene?",
            body=f'This action can not be undone. Are you sure you want to delete the scene "{self._scene.title}"',
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
            # Delete the scene
            self._scene.project.delete_resource(self._scene)

            # Return to listing the scenes
            self.get_parent().pop()

    @Gtk.Template.Callback()
    def on_connect_element_clicked(self, _button):
        logger.info("Connect story elements")

        def handle_response(dialog, task):
            response = dialog.choose_finish(task)
            if response == "done":
                entity = dialog.get_selected_entity()
                logger.info(f"Connectiong {entity.title}")
                self._scene.connect_to(entity)

        dialog = ScrptSelectEntitiesDialog(self._scene, self._scene.project.entities)
        dialog.choose(self, None, handle_response)
