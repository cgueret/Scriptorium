# widgets/text_view.py
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
from gi.repository import Gtk, GObject, Pango, Gdk, Gio
from scriptorium.globals import BASE
from scriptorium.utils import html_to_buffer

import logging

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/views/publish/preview.ui")
class PublishPreview(Gtk.TextView):
    __gtype_name__ = "PublishPreview"

    css_provider = Gtk.CssProvider()
    buffer = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set the style for the editor
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Text formatting tags
        self.buffer.create_tag("em", style=Pango.Style.ITALIC)
        self.buffer.create_tag("strong", weight=Pango.Weight.BOLD)

    def load(self, html_content: str):
        # Clear the content of the text buffer
        self.buffer.begin_irreversible_action()
        start_iter, end_iter = self.buffer.get_bounds()
        self.buffer.delete(start_iter, end_iter)
        self.buffer.end_irreversible_action()

        html_to_buffer(html_content, self.buffer)

