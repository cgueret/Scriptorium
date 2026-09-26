# widgets/scene.py
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

from gi.repository import Adw, Gtk, GObject
from scriptorium.models import Scene
from scriptorium.utils import get_child_at
from scriptorium.globals import BASE

import logging

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/widgets/scene.ui")
class SceneCard(Adw.Bin):
    __gtype_name__ = "SceneCard"

    _scene = None
    title = GObject.Property(type=str)
    synopsis = GObject.Property(type=str)

    suffixes = Gtk.Template.Child()
    prefixes = Gtk.Template.Child()
    entities = Gtk.Template.Child()

    def __init__(
        self, scene: Scene, can_activate: bool = False, can_move: bool = False
    ):
        super().__init__()
        self._scene = scene

        # Configure the information for the scene
        self.set_property("title", scene.title)
        self.set_property("synopsis", scene.synopsis)
        self.bind_property("title", scene, "title", GObject.BindingFlags.BIDIRECTIONAL)
        self.bind_property(
            "synopsis", scene, "synopsis", GObject.BindingFlags.BIDIRECTIONAL
        )

        # Adjust the display of drag and activation extra
        self.prefixes.set_visible(can_move)
        self.suffixes.set_visible(can_activate)

        # Initialise the list of entities
        for entity in scene.entities:
            self.entities.append(self._get_avatar(entity))

        # Keep an eye on potential changes
        scene.entities.connect("items-changed", self.on_items_changed)

    @GObject.Property(type=Scene)
    def scene(self):
        return self._scene

    def _get_avatar(self, entity):
        avatar = Adw.Avatar(size=24, show_initials=True)
        avatar.set_text(entity.title)
        return avatar

    def on_items_changed(self, liststore, position, removed, added):
        """Handle a request to update the content of the entities list."""

        # Remove widgets for removed items
        for _ in range(removed):
            child = get_child_at(self.entities, position)
            self.entities.remove(child)

        # Add widgets for added items
        for i in range(added):
            entry = liststore.get_item(position + i)
            child = get_child_at(self.entities, position + i - 1)
            self.entities.insert_child_after(self._get_avatar(entry), child)
