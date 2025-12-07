# views/editor_formatting.py
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
from gi.repository import Adw, Gtk
from scriptorium.globals import BASE
from scriptorium.utils.publisher import Publisher

import logging
logger = logging.getLogger(__name__)


class NavigationRow(Gtk.Box):

    def __init__(self, part):
        super().__init__(margin_top=6)

        # Keep track of the book part
        self._part = part

        # Set the label
        label = Gtk.Label(label=part.title)
        self.append(label)

    @property
    def part(self):
        return self._part


@Gtk.Template(resource_path=f"{BASE}/views/publish/page.ui")
class PublishPage(Adw.Bin):

    __gtype_name__ = "PublishPage"
    __title__ = "Formatting"
    __icon_name__ = "open-book-symbolic"
    __description__ = "Preview and modify the formatting"

    preview = Gtk.Template.Child()
    toc = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.toc.connect(
             "row-selected",
             self.on_selected_item
        )

    def connect_to_project(self, project):
        logger.info("Project changed")
        self._project = project
        self._publisher = Publisher(project.manuscript)
        self.reload_book()

    @Gtk.Template.Callback()
    def on_publishpage_map(self, page):
        logger.info("Published opened")
        self.reload_book()

    def reload_book(self):
        # Remove all the previous content
        self.toc.remove_all()

        # Load the new ToC
        self._publisher.rebuild()
        book_parts = self._publisher.table_of_contents
        for book_part in book_parts:
            widget = NavigationRow(book_part)
            self.toc.append(widget)

        # Select the first item
        row = self.toc.get_row_at_index(0)
        self.toc.select_row(row)

    def on_selected_item(self, _src, _selected_item):
        selected_row = self.toc.get_selected_row()
        if selected_row is None:
            return

        widget = selected_row.get_child()
        logger.info(f"Chapter selected: {widget}")

        # Get all the HTML content from the model
        content = widget.part.get_content()
        if isinstance(content, bytes):
            content = content.decode()

        # Load that into the preview window
        self.preview.load(content)

    @Gtk.Template.Callback()
    def on_publish_clicked(self, _button):
        """Handle a click on the Publish button."""

        # Define a default file name based on the project name
        file_name = self._project.title + ".epub"

        # Call back to save the file and inform the user
        def save_path_selected(file_dialog, task, _):
            file_name = file_dialog.save_finish(task)
            self._publisher.save(file_name.get_path())
            self.props.root.inform("File saved!")

        # Create and present the dialog
        file_dialog = Gtk.FileDialog.new()
        file_dialog.set_initial_name(file_name)
        file_dialog.save(self.props.root, None, save_path_selected, None)

