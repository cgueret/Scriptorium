# writer_popover.py
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

# Code inspired from Eloquent:
# https://github.com/sonnyp/Eloquent/blob/main/src/widgets/SuggestionPopover.js

from gi.repository import Adw, Gtk, GObject
from scriptorium.globals import BASE
from scriptorium.models import Annotation

import logging

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/widgets/annotation.ui")
class AnnotationCard(Adw.Bin):
    __gtype_name__ = "AnnotationCard"

    annotation = GObject.Property(type=Annotation)
    title = GObject.Property(type=str)
    message = GObject.Property(type=str)
    icon = Gtk.Template.Child()
    suggestions = Gtk.Template.Child()

    def __init__(self, text_buffer, annotation: Annotation):
        super().__init__()
        self.annotation = annotation

        # Set basic attributes
        self.title = annotation.title
        self.message = annotation.message

        # Adjust the color of the header according to the type of annotation
        if annotation.category == "warning":
            self.icon.add_css_class("annotation-warning")
            self.icon.set_from_icon_name("dialog-warning-symbolic")
        elif annotation.category == "error":
            self.icon.add_css_class("annotation-error")
            self.icon.set_from_icon_name("dialog-error-symbolic")
        elif annotation.category == "hint":
            self.icon.add_css_class("annotation-hint")
            self.icon.set_from_icon_name("dialog-information-symbolic")

        # Add the suggestions (limit to top 10 if we have more)
        for suggestion in annotation.suggestions[:10]:
            button = Gtk.Button(label=suggestion.get_string())
            button.add_css_class("suggested-action")
            button.connect("clicked", self.on_suggestion_click, text_buffer)
            self.suggestions.append(button)

    def on_suggestion_click(self, button, text_buffer):
        start_iter = text_buffer.get_iter_at_offset(self.annotation.offset)
        end_iter = text_buffer.get_iter_at_offset(
            self.annotation.offset + self.annotation.length
        )
        text_buffer.delete(start_iter, end_iter)
        text_buffer.insert(start_iter, button.get_label())
