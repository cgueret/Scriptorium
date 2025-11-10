# views/plan/page.py
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

from scriptorium.globals import BASE
from scriptorium.models import Project
from .editor_entities import ScrptEntityPanel
from .editor_scenes import ScrptScenesPanel
from .editor_manuscript import ScrptManuscriptPanel
from .editor_overview import ScrptOverviewPanel
from .editor_images import ScrptImagesPanel

import logging

logger = logging.getLogger(__name__)

PANELS = [
    # Manuscript
    ("header", _("Manuscript")),
    ("manuscript", ScrptManuscriptPanel),
    # Background research
    # Writing goals

    # Story elements
    ("header", _("Story line")),
    ("overview", ScrptOverviewPanel),
    ("scenes", ScrptScenesPanel),
    ("entities", ScrptEntityPanel),
    # Time line
    # Plot lines

    # Special pages
    ("header", _("Additional resources")),
    ("images", ScrptImagesPanel),
]

DEFAULT = "manuscript"


@Gtk.Template(resource_path=f"{BASE}/views/plan/page.ui")
class PlanPage(Adw.Bin):
    __gtype_name__ = "PlanPage"

    panels_list = Gtk.Template.Child()
    panels = Gtk.Template.Child()

    project = GObject.Property(type=Project)

    def __init__(self):
        """Create a new instance of the planning page."""
        super().__init__()

        # Setup all the panels
        self.initialise_panels()

        self.connect("map", self.on_map)

    def on_map(self, _):
        #Open the default panel
        row = None
        for index in range(len(PANELS)):
            if PANELS[index][0] == DEFAULT:
                row = self.panels_list.get_row_at_index(index)
                self.panels_list.select_row(row)

    def connect_to_project(self, project):
        logger.info("Project changed")
        self.project = project

    def initialise_panels(self):
        """Add all the panels to the menu."""

        for panel_id, panel in PANELS:
            # Create a menu entry
            box = Gtk.Box.new(spacing=12, orientation=Gtk.Orientation.HORIZONTAL)
            box.set_margin_start(6)
            box.set_margin_end(6)
            box.set_margin_top(12)

            if panel_id == "header":
                box.set_margin_bottom(6)
                label = Gtk.Label(label=panel)
                label.add_css_class("dim-label")
            else:
                box.set_margin_bottom(12)
                image = Gtk.Image.new_from_icon_name(icon_name=panel.__icon_name__)
                box.append(image)
                label = Gtk.Label.new(panel.__title__)

            box.append(label)

            self.panels_list.append(box)

            # Add the id and title to the box for easy retrieval later
            box.panel_id = panel_id

        # Deactivate all the headers
        index = 0
        row = self.panels_list.get_row_at_index(index)
        while row is not None:
            if row.get_child().panel_id == "header":
                row.set_activatable(False)
                row.set_selectable(False)
            index += 1
            row = self.panels_list.get_row_at_index(index)

    @Gtk.Template.Callback()
    def on_listbox_row_selected(self, _list_box, _selected_item):
        """Change the panel currently displayed."""
        selection = _selected_item.get_child()
        logger.info(f"Switching to panel {selection.panel_id}")

        p = None
        for panel_id, panel in PANELS:
            if panel_id == selection.panel_id:
                # Instantiate the panel
                p = panel(self)

        self.panels.replace([p])

