# models/resource.py
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

from gi.repository import GObject, Gio

import logging

logger = logging.getLogger(__name__)


class Resource(GObject.Object):
    __gtype_name__ = "Resource"

    # The unique identifier of the resource
    identifier = GObject.Property(type=str)

    # The title of the resource
    title = GObject.Property(type=str)

    # The description of the resource
    synopsis = GObject.Property(type=str)

    # A signal to inform that the resource has been deleted
    deleted = GObject.Signal()

    def __init__(self, project, identifier: str):
        """Create a resource."""
        super().__init__()
        self.identifier = identifier
        self._project = project

    @property
    def project(self):
        # The project the resource is part of
        return self._project

    @property
    def data_files(self):
        # An eventual list of data files associated with the resource
        return []

    @property
    def references(self):
        """Provide a list of other resources referencing that one."""
        output: set[Resource] = set()

        all_resources = self._project.resources
        for other in all_resources:
            # We skip checking ourselves
            if other == self:
                continue

            for prop in GObject.list_properties(type(other)):
                if isinstance(prop, GObject.ParamSpecObject):
                    # Check if the use is a direct assignment
                    if prop.value_type == getattr(Resource, "__gtype__", None):
                        if other.get_property(prop.name) == self:
                            output.add(other)
                    # Or if it is found in a list
                    elif prop.value_type == getattr(Gio.ListStore, "__gtype__", None):
                        list_store = other.get_property(prop.name)
                        accepted_item_type = list_store.get_item_type()
                        resource_type = getattr(self, "__gtype__", None)
                        if resource_type and resource_type.is_a(accepted_item_type):
                            found, _ = list_store.find(self)
                            if found:
                                output.add(other)

        return output

    def process_deleted(self):
        """Handler used to perform actions needed post-deletion.

        By default only the signal "deleted" is emited but specific resources
        might want to perform additional actions (such as deleting files on
        disk)
        """

        # We emit the signal
        self.emit("deleted")
