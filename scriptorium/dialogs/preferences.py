# dialogs/preferences.py
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
"""Dialog to select scenes in Scriptorium."""
from gi.repository import Adw, Gtk, Gio, Pango
from scriptorium.globals import BASE
from scriptorium.utils import html_to_buffer
from gettext import gettext as _

import logging

logger = logging.getLogger(__name__)

PLACEHOLDER_TEXT = _(
"<p>This is a <hint>placeholder text</hint> to <warning>select</warning>"
"the font of the scene editor.</p>"
"<p>You can also see how <error>annotations</error> are shown and how words"
"with an <em>emphasis</em> or noted as <strong>strong</strong> will appear.</p>"
)
UNDERLINE_OPTIONS = ["single", "double", "dashed"]


@Gtk.Template(resource_path=f"{BASE}/dialogs/preferences.ui")
class ScrptPreferencesDialog(Adw.PreferencesDialog):
    __gtype_name__ = "ScrptPreferencesDialog"

    open_last_project = Gtk.Template.Child()
    text_view = Gtk.Template.Child()
    font_dialog_button = Gtk.Template.Child()
    editor_line_height = Gtk.Template.Child()
    font_dialog_button = Gtk.Template.Child()
    editor_underline_style = Gtk.Template.Child()

    def __init__(self):
        """Create a new instance of the class."""
        super().__init__()

        # Bind settings
        settings = Gio.Settings(
            schema_id="io.github.cgueret.Scriptorium"
        )

        settings.bind(
            "open-last-project",
            self.open_last_project,
            "active",
            Gio.SettingsBindFlags.DEFAULT
        )

        settings.bind(
            "editor-line-height",
            self.editor_line_height,
            "value",
            Gio.SettingsBindFlags.DEFAULT
        )

        # Set the underline style combo to the current value
        underline_style = settings.get_string("editor-underline-style")
        index = UNDERLINE_OPTIONS.index(underline_style)
        self.editor_underline_style.set_selected(index)

        # Set the dialog to the current font in the settings
        font_desc_str = settings.get_string("editor-font-desc")
        font_desc = Pango.FontDescription.from_string(font_desc_str)
        self.font_dialog_button.set_font_desc(font_desc)

        # Load up the text for the font preview
        html_to_buffer(
            PLACEHOLDER_TEXT,
            self.text_view.get_buffer()
        )

    @Gtk.Template.Callback()
    def on_font_selected(self, _button, _value):
        """Handle the selection of a new font."""
        font_description = self.font_dialog_button.get_font_desc()

        settings = Gio.Settings(
            schema_id="io.github.cgueret.Scriptorium"
        )
        settings.set_string(
            "editor-font-desc",
            font_description.to_string()
        )

    @Gtk.Template.Callback()
    def on_underline_style_selected(self, _combo, _value):
        """Handle the selection of a new underline style."""
        selected_value = self.editor_underline_style.get_selected()

        settings = Gio.Settings(
            schema_id="io.github.cgueret.Scriptorium"
        )
        settings.set_string(
            "editor-underline-style",
            UNDERLINE_OPTIONS[selected_value]
        )

