# views/plan/editor_entity.py
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

from gi.repository import Adw, Gtk

from scriptorium.dialogs import ScrptAddDialog
from scriptorium.globals import BASE
from scriptorium.models import Entity
from scriptorium.widgets import EntityCard

from .editor_entities_details import ScrptEntitiesDetailsPanel

logger = logging.getLogger(__name__)

# TODO: When adding a new element offer to pick a template to pre-populate attrs


@Gtk.Template(resource_path=f"{BASE}/views/plan/editor_entities.ui")
class ScrptEntityPanel(Adw.NavigationPage):
    __gtype_name__ = "ScrptEntityPanel"
    __icon_name__ = "find-location-symbolic"

    __title__ = _("Story elements")
    __description__ = _("Set the key elements of the story")

    entities_list = Gtk.Template.Child()
    navigation = Gtk.Template.Child()

    def __init__(self, editor, **kwargs):
        """Create an instance of the panel."""
        super().__init__(**kwargs)
        self._editor = editor

        # Connect to the entities of the manuscript
        self.entities_list.bind_model(
            self._editor.project.entities,
            lambda entity: EntityCard(entity, can_activate=True)
        )

    @Gtk.Template.Callback()
    def on_add_entity_clicked(self, _button):
        """Handle a request to add a new entity."""
        def handle_response(dialog, task):
            response = dialog.choose_finish(task)
            if response == "add":
                logger.info(f"Add entity {dialog.title}: {dialog.synopsis}")
                self._editor.project.create_resource(
                    Entity, dialog.title, dialog.synopsis
                )

        dialog = ScrptAddDialog("story element")
        dialog.choose(self, None, handle_response)

    @Gtk.Template.Callback()
    def on_listbox_row_activated(self, _widget, selected_row):
        entity = selected_row.get_child().entity
        logger.info(f'Clicked on entity "{entity.title}"')
        details_panel = ScrptEntitiesDetailsPanel(entity)
        self.navigation.push(details_panel)

