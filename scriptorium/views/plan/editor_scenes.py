# views/plan/editor_scenes.py
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

from gi.repository import Adw, Gtk

from scriptorium.globals import BASE
from scriptorium.widgets import SceneCard
from scriptorium.dialogs import ScrptAddDialog
from scriptorium.models import Scene

from .editor_scenes_details import ScrptScenesDetailsPanel

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/views/plan/editor_scenes.ui")
class ScrptScenesPanel(Adw.NavigationPage):
    """Panel to list all the scenes and edit their content."""
    __gtype_name__ = "ScrptScenesPanel"
    __icon_name__ = "edit-symbolic"

    __title__ = _("Scenes list")
    __description__ = _("Edit the content of the scenes")

    scenes_list = Gtk.Template.Child()
    navigation: Adw.NavigationView = Gtk.Template.Child()

    def __init__(self, editor, **kwargs):
        """Create an instance of the panel."""
        super().__init__(**kwargs)
        self._editor = editor

        self.scenes_list.bind_model(
            self._editor.project.scenes,
            lambda scene: SceneCard(scene=scene, can_activate=True)
        )

    @Gtk.Template.Callback()
    def on_listbox_row_activated(self, _list_box, row):
        """Switch to the editing mode if a row is clicked."""
        scene = row.get_child().scene
        logger.info(f"Open editor for {scene.title}")

        details = ScrptScenesDetailsPanel(scene)
        self.navigation.push(details)

    @Gtk.Template.Callback()
    def on_add_scene_clicked(self, _button):
        logger.info("Open dialog to add scene")

        def handle_response(dialog, task):
            response = dialog.choose_finish(task)
            if response == "add":
                logger.info(f"Add scene {dialog.title}: {dialog.synopsis}")
                resource = self._editor.project.create_resource(
                    Scene, dialog.title, dialog.synopsis
                )
                self._editor.project.manuscript.add_resource(resource)

        dialog = ScrptAddDialog("scene")
        dialog.choose(self, None, handle_response)
