# views/plan/editor_manuscript.py
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
"""Editor panel to select and work on the scenes."""
from gettext import gettext as _

import logging

from gi.repository import Adw, Gtk, GObject, Gio, GLib

from scriptorium.globals import BASE


logger = logging.getLogger(__name__)


class KeyValuePair(GObject.Object):
    key = GObject.Property(
        type=str,
        flags=GObject.ParamFlags.READWRITE,
        default=""
    )
    value = GObject.Property(
        type=str,
        nick="Value",
        blurb="Value",
        flags=GObject.ParamFlags.READWRITE,
        default="",
    )


def find_in_model(input_list: Gio.ListModel, value: str, default: int) -> int:
    """Look for the index of a target string, return the default if not found."""
    position = 0
    while input_list.get_item(position) is not None:
        if input_list.get_item(position).key == value:
            return position
        position += 1
    return default


@Gtk.Template(resource_path=f"{BASE}/views/plan/editor_manuscript.ui")
class ScrptManuscriptPanel(Adw.NavigationPage):
    __gtype_name__ = "ScrptManuscriptPanel"
    __icon_name__ = "dictionary-symbolic"

    __title__ = _("Description")
    __description__ = _("Edit the information about the manuscript")

    identifier = Gtk.Template.Child()
    edit_title = Gtk.Template.Child()
    edit_synopsis = Gtk.Template.Child()
    cover_stack = Gtk.Template.Child()
    cover_picture = Gtk.Template.Child()
    cover_edit_button = Gtk.Template.Child()
    language_drop_down = Gtk.Template.Child()

    def __init__(self, editor, **kwargs):
        """Create an instance of the panel."""
        super().__init__(**kwargs)

        self._editor = editor
        self.set_title(self.__title__)

        # Bind the identifier, title and synopsis
        editor.project.manuscript.bind_property(
            "identifier",
            self.identifier,
            "subtitle",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        editor.project.manuscript.bind_property(
            "title",
            self.edit_title,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        editor.project.manuscript.bind_property(
            "synopsis",
            self.edit_synopsis,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )

        # Update the cover and keep an eye on further changes
        self.update_cover()
        editor.project.manuscript.connect(
            "notify::cover", lambda _src, _val: self.update_cover()
        )

        # Create the menu for changing the cover
        menu = Gio.Menu()
        menu.append(
            label=" Import a new cover",
            detailed_action="editor.import_cover"
        )
        menu.append(
            label="Remove cover",
            detailed_action="editor.set_cover('')"
        )
        self.cover_edit_button.set_menu_model(menu)

    @Gtk.Template.Callback()
    def on_scrptmanuscriptpanel_realize(self, _widget):
        """Perform final content initialization when the widget is ready."""

        # Send a request to get the list of supported languages
        self._ask_language_tool_for_languages()

    def _ask_language_tool_for_languages(self) -> bool:
        # Call LanguageTool to get the list of languages
        window = self.props.root
        application = window.props.application
        language_tool = application.language_tool
        language_tool.languages(self.on_language_list_received)

        # When called on a timeout, we don't want this to repeat
        return False

    def on_language_list_received(self, languages):
        """Process a reply from LanguageTool with a list of languages."""
        if not languages:
            logger.info("Will retry fetching languages in 2 second")
            GLib.timeout_add_seconds(
                2,
                self._ask_language_tool_for_languages
            )
        else:
            # Add the language options to the drop down
            logger.info(languages)
            model = Gio.ListStore(item_type=KeyValuePair)
            for language in languages:
                model.append(KeyValuePair(
                    key=language['longCode'], value=language['name']
                ))
            list_store_expression = Gtk.PropertyExpression.new(
                KeyValuePair,
                None,
                "value",
            )
            self.language_drop_down.set_expression(list_store_expression)
            self.language_drop_down.set_model(model)

            index_english = find_in_model(model, "English", 0)

            # Bind the language property to the drop down
            self._editor.project.manuscript.bind_property(
                source_property="language",
                target=self.language_drop_down,
                target_property="selected",
                flags=GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
                transform_from=lambda src, position:
                    self.language_drop_down.get_selected_item().key,
                transform_to=lambda src, string:
                    find_in_model(model, string, index_english)
            )

            # Select the current language
            logger.info(self._editor.project.manuscript.language)
            self.language_drop_down.set_selected(
                find_in_model(
                    model,
                    self._editor.project.manuscript.language,
                    index_english
                 )
            )

    def create_message_entry(self, message):
        """Add a message to the history."""
        message_entry = Adw.ActionRow()
        message_entry.add_css_class("property")
        message_entry.set_title(message.datetime)
        message_entry.set_subtitle(message.message)
        return message_entry

    def on_delete_response_selected(self, _dialog, task):
        """Handle the response to the confirmation dialog."""
        response = _dialog.choose_finish(task)
        if response == "delete":
            # Delete the manuscript
            library = self._editor.project.library
            library.delete_project(self._editor.project)

            # Pop the navigation
            self._editor.close_on_delete()

    def update_cover(self):
        """Update the display of the cover."""
        cover_image = self._editor.project.manuscript.cover
        logger.info(f"Update cover to {cover_image}")

        if cover_image is not None:
            self.cover_picture.set_paintable(cover_image.texture)
            self.cover_stack.set_visible_child_name("image_set")
        else:
            self.cover_picture.set_paintable(None)
            self.cover_stack.set_visible_child_name("no_image_set")

