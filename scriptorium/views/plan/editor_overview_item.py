# views/plan/edit_overview_item.py
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

from scriptorium.globals import BASE
from scriptorium.models import Chapter, Manuscript, Resource

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/views/plan/editor_overview_item.ui")
class ScrptOverviewPanelItem(Adw.Bin):
    __gtype_name__ = "ScrptOverviewPanelItem"

    title = Gtk.Template.Child()
    synopsis = Gtk.Template.Child()
    content = Gtk.Template.Child()
    expander = Gtk.Template.Child()

    def bind_to_resource(self, resource: Resource):
        """Connect this item to an instance of Resource."""

        # Keep a pointer to the resource
        self._resource = resource

        # Set the title and synopsis
        self.title.set_label(self._resource.title)
        self.synopsis.set_label(self._resource.synopsis)

        # Remove the list if there was one
        self.expander.set_child(None)

        if isinstance(resource, (Manuscript)):
            self.remove_css_class("card")

        if isinstance(resource, (Manuscript, Chapter)):
            # Create a selection model for the content
            selection_model = Gtk.NoSelection(model=self._resource.content)

            # Connect the factory setup and bind
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self.on_signallistitemfactory_setup)
            factory.connect("bind", self.on_signallistitemfactory_bind)

            # Create the list view
            child_items = Gtk.ListView.new(selection_model, factory)
            self.expander.set_child(child_items)
            self.expander.set_visible(True)
            self.expander.set_expanded(True)
        else:
            self.expander.set_visible(False)

    def on_signallistitemfactory_setup(self, _, list_item):
        list_item.set_child(ScrptOverviewPanelItem())

    def on_signallistitemfactory_bind(self, _, list_item):
        resource = list_item.get_item()
        item_widget = list_item.get_child()
        item_widget.bind_to_resource(resource)
