# widgets/entity_card.py
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
from scriptorium.models import Entity
from scriptorium.globals import BASE

import logging

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/widgets/entity_card.ui")
class EntityCard(Adw.Bin):
    __gtype_name__ = "EntityCard"

    _entity = None
    title = GObject.Property(type=str)
    synopsis = GObject.Property(type=str)

    suffixes = Gtk.Template.Child()
    prefixes = Gtk.Template.Child()
    avatar = Gtk.Template.Child()

    def __init__(
        self, entity: Entity, can_activate: bool = False, can_move: bool = False
    ):
        super().__init__()
        self._entity = entity

        # Configure the information for the entity
        entity.bind_property(
            "title",
            self,
            "title",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        entity.bind_property(
            "synopsis",
            self,
            "synopsis",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )

        # Connect the title to the avatar
        entity.bind_property(
            "title", self.avatar, "text", GObject.BindingFlags.SYNC_CREATE
        )

        # Adjust the display of drag and activation extra
        self.prefixes.set_visible(can_move)
        self.suffixes.set_visible(can_activate)

    @GObject.Property(type=Entity)
    def entity(self):
        return self._entity
