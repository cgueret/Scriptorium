# views/write/navigation.py
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

from gi.repository import Gio, Graphene, Gtk, Adw

from scriptorium.globals import BASE
from scriptorium.models import Chapter, Manuscript, Scene

from .navigation_item import NavigationItem

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/views/write/navigation.ui")
class WriteNavigation(Adw.Bin):
    __gtype_name__ = "WriteNavigation"

    factory = Gtk.Template.Child()
    list_view = Gtk.Template.Child()

    add_menu = Gtk.Template.Child()

    drag_point = Graphene.Point()
    item_dragged = None
    accented_row = None
    place_holder = None

    def __init__(self):
        super().__init__(self)

    @Gtk.Template.Callback()
    def on_list_item_setup(self, _, list_item):
        list_item.set_child(NavigationItem())

    @Gtk.Template.Callback()
    def on_list_item_bind(self, _, list_item):
        """Bind an item to the navigation widget."""
        # The list row
        list_row = list_item.get_item()

        # The resource associated to the row
        resource = list_row.get_item()

        # The widget used to display this row
        widget = list_item.get_child()

        # Only scenes can be activated and selected
        list_item.set_activatable(isinstance(resource, Scene))
        list_item.set_selectable(isinstance(resource, Scene))

        # Set the content of the expander
        widget.expander.set_list_row(list_row)

        # Set the resource
        widget.resource = resource

        # Set the parent model
        widget.parent_model = list_row.get_parent().get_children() if list_row.get_parent() is not None else None

    def connect_to(self, project):
        """Connect the navigation to the project and its contents."""

        # Turn the content into a tree, instance of Chapter may have children
        roots = Gio.ListStore.new(Manuscript)
        roots.append(project.manuscript)

        # Create a tree list model which recurse into content as applicable
        tree_list_model = Gtk.TreeListModel.new(
            roots, False, True,
            lambda item: item.content if isinstance(item, (Manuscript, Chapter)) else None
        )
        tree_list_model.set_autoexpand(False)

        # Use this model to define a selection model that let users pick a scene
        # with none being selected by default
        selection_model = Gtk.SingleSelection(model=tree_list_model)
        selection_model.set_autoselect(False)
        selection_model.set_can_unselect(True)
        selection_model.set_selected(Gtk.INVALID_LIST_POSITION)

        # Assign this model to the navigation list view
        self.list_view.set_model(selection_model)

        # Set the menu for the split button. We will trigger all the actions to
        # append items at the end of the manuscript by default. Users who want
        # to position items directly can use the context actions instead
        manuscript_id = project.manuscript.identifier
        menu = Gio.Menu()
        menu.append(
            label=_("Add new Scene"),
            detailed_action=f"editor.add_resource(('Scene', '{manuscript_id}'))"
        )
        menu.append(
            label=_("Add new Chapter"),
            detailed_action=f"editor.add_resource(('Chapter', '{manuscript_id}'))"
        )
        self.add_menu.set_menu_model(menu)
        self.add_menu.set_detailed_action_name(
            f"editor.add_resource(('Scene', '{manuscript_id}'))"
        )

