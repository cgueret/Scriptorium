# views/write/page.py
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
from gi.repository import Adw, Gtk, Gdk, GLib, Gio, GObject
from scriptorium.globals import BASE
from scriptorium.widgets import AnnotationCard
from scriptorium.models import Scene
from scriptorium.utils import switch_tag_for_selection
from scriptorium.utils import html_to_buffer
from scriptorium.utils import buffer_to_html

import logging
import threading

logger = logging.getLogger(__name__)

EDITOR_IDLE_TIMEOUT_TIME = 200

# make font selectable like in https://gitlab.gnome.org/GNOME/gnome-text-editor/-/blob/main/src/editor-preferences-dialog.c

#TODO: when editor is idle (500ms) by default, trigger buffer->html
#TODO: when it's autosave time (1s) by default, trigger html->disk

# Mutex to avoid having to matches callback edit the buffer at the same time
text_buffer_lock = threading.Lock()


@Gtk.Template(resource_path=f"{BASE}/views/write/page.ui")
class WritePage(Adw.Bin):
    __gtype_name__ = "WritePage"

    text_view = Gtk.Template.Child()
    label_words = Gtk.Template.Child()
    css_provider = Gtk.CssProvider()
    annotations_list = Gtk.Template.Child()
    show_annotations = Gtk.Template.Child()

    navigation = Gtk.Template.Child()
    edit_title = Gtk.Template.Child()
    edit_synopsis = Gtk.Template.Child()
    stack = Gtk.Template.Child()

    active_scene = GObject.Property(type=Scene)

    def __init__(self):
        """Create an instance of the editor."""
        super().__init__()
        # By default we have no active scene
        self.active_scene = None

        # Instantiated with a timeout to detect when the editor is idle
        self._idle_timeout_id = None

        # Instantiated with a list of annotations from the spellchecker
        self._annotations = None

        self.text_view.get_buffer().connect("changed", self.on_buffer_changed)

        # Create all the actions
        action_group = Gio.SimpleActionGroup()
        controller = Gtk.ShortcutController()

        action = Gio.SimpleAction.new("do_toggle_bold", None)
        action.connect("activate", self.do_toggle_bold)
        action_group.add_action(action)
        shortcut = Gtk.Shortcut.new(
            Gtk.ShortcutTrigger.parse_string("<Primary>b"),
            Gtk.NamedAction.new("custom.do_toggle_bold")
        )
        controller.add_shortcut(shortcut)

        action = Gio.SimpleAction.new("do_toggle_italics", None)
        action.connect("activate", self.do_toggle_italics)
        action_group.add_action(action)
        shortcut = Gtk.Shortcut.new(
            Gtk.ShortcutTrigger.parse_string("<Primary>i"),
            Gtk.NamedAction.new("custom.do_toggle_italics")
        )
        controller.add_shortcut(shortcut)

        self.text_view.insert_action_group("custom", action_group)
        self.text_view.add_controller(controller)

        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self.on_text_view_click)
        self.text_view.add_controller(gesture)

        self.anchor_overlay = Adw.Bin()
        self.popover_annotation = Gtk.Popover(autohide=False)
        self.popover_annotation.set_parent(self.anchor_overlay)
        self.text_view.add_overlay(child=self.anchor_overlay, xpos=0, ypos=0)

    def connect_to_project(self, project):
        self.project = project

        self.navigation.connect_to(project)

        # Connect to the navigation to see when a scene is selected
        navigation_model = self.navigation.list_view.get_model()
        navigation_model.connect("selection-changed", self.on_selection_changed)

    def unselect_on_delete(self, _src):
        """Handle case when a selected resource is deleted."""
        logger.info("Unselect on delete")

        # Get the navigation model of the tree
        navigation_model = self.navigation.list_view.get_model()

        # Emit the signal to inform that the selection has changed
        # TODO this should not be necessary, there must be a better approach
        navigation_model.emit("selection-changed", 0, 0)

    def on_selection_changed(self, selection, position, n_items):
        """Called when a scene is selected in the navigation."""
        # Get the selected scene
        selected_item = selection.get_selected_item()
        if selected_item is not None:
            scene = selected_item.get_item()
            logger.info(f"Selected scene {scene.title}")
            self.load_scene(scene)
            self.stack.set_visible_child_name("editor")
            scene.connect("deleted", self.unselect_on_delete)
        else:
            logger.info("Nothing selected")
            self.stack.set_visible_child_name("select_scene")

    def load_scene(self, scene: Scene):
        """Load a new scene into the text editor."""
        # Get the text buffer of the editor
        buffer = self.text_view.get_buffer()

        # If there is a scene loaded save the content and clear it
        if self.active_scene is not None:
            # Remove all the language check annotations
            self.clear_annotations()

            # Clear the annotations list box too
            self.annotations_list.remove_all()

            # Update the content of the scene and save it to disk
            self.active_scene.set_content(buffer_to_html(buffer))
            self.active_scene.save()

            # Clear the content of the text buffer
            buffer.begin_irreversible_action()
            start_iter, end_iter = buffer.get_bounds()
            buffer.delete(start_iter, end_iter)
            buffer.end_irreversible_action()

            # Unbind
            self.edit_title_binding.unbind()
            self.edit_synopsis_binding.unbind()

        # Load the scene into the buffer
        html_to_buffer(scene.get_content(), buffer)

        # Connect the information bar properties to the scene
        self.edit_title_binding = scene.bind_property(
            "title",
            self.edit_title,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )
        self.edit_synopsis_binding = scene.bind_property(
            "synopsis",
            self.edit_synopsis,
            "text",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )

        # Set the scene as active
        self.active_scene = scene

    def on_text_view_click(self, _gesture, n_press, x, y):
        # If we are on a suggestion, automatically select it.
        # This will trigger the selection changed
        #if self.popover:
        #    self.popover.popdown()
        self.popover_annotation.popdown()

        if isinstance(_gesture, Gtk.GestureClick) and n_press == 1:
            buff_x, buff_y = self.text_view.window_to_buffer_coords(
                Gtk.TextWindowType.WIDGET,
                x, y
            )
            found, click_iter = self.text_view.get_iter_at_location(
                buff_x, buff_y
            )
            if found and self._annotations is not None:
                offset = click_iter.get_offset()
                location = self.text_view.get_iter_location(click_iter)
                iter_x, iter_y = self.text_view.buffer_to_window_coords(
                    Gtk.TextWindowType.TEXT, location.x, location.y
                )
                for match in self._annotations:
                    if match.offset < offset < match.offset + match.length:
                        self.text_view.move_overlay(
                            child=self.anchor_overlay,
                            xpos=iter_x,
                            ypos=iter_y+(location.height / 2)+3
                        )
                        self.popover_annotation.set_pointing_to(
                            Gdk.Rectangle(
                                x=iter_x,
                                y=iter_y,
                                width=1,
                                height=location.height
                            )
                        )
                        self.popover_annotation.set_child(
                            AnnotationCard(self.text_view.get_buffer(), match)
                        )
                        self.popover_annotation.popup()

    @Gtk.Template.Callback()
    def do_toggle_bold(self, _src, _param = None):
        switch_tag_for_selection(self.text_view.get_buffer(), "strong")

    @Gtk.Template.Callback()
    def do_toggle_italics(self, _src, _param = None):
        switch_tag_for_selection(self.text_view.get_buffer(), "em")

    def on_received_annotations(self, annotations):
        # If there is another check queued forget that one
        if self._idle_timeout_id is not None:
            return

        self._annotations = annotations
        self.refresh_annotations_tags()

        # Clear the list box
        self.annotations_list.remove_all()

        # Then add the new card
        for annotation in annotations:
            card = AnnotationCard(self.text_view.get_buffer(), annotation)
            self.annotations_list.append(card)

    def on_editor_idle(self):
        """Called when the editor has been idle for some time."""

        # Get a pointer to the text buffer
        text_buffer = self.text_view.get_buffer()

        # Save the current content of the buffer
        self.active_scene.set_content(buffer_to_html(text_buffer))

        # Update the number of words
        start_iter, end_iter = text_buffer.get_bounds()
        content = text_buffer.get_text(start_iter, end_iter, False)
        words = len(content.split())
        self.label_words.set_label(str(words))

        # Call LanguageTool
        window = self.props.root
        application = window.props.application
        language_tool = application.language_tool

        # If language tool is not ready try again later
        if not language_tool.server_is_alive:
            self._idle_timeout_id = GLib.timeout_add(
                EDITOR_IDLE_TIMEOUT_TIME,
                self.on_editor_idle
            )
        else:
            language_tool.check(
                content,
                "en-GB",
                self.on_received_annotations
            )

        # Don't repeat that callback
        self._idle_timeout_id = None
        return False

    def clear_annotations(self):
        """Remove all the current annotations on the text."""
        text_buffer = self.text_view.get_buffer()
        start_iter, end_iter = text_buffer.get_bounds()
        text_buffer.remove_tag_by_name("error", start_iter, end_iter)
        text_buffer.remove_tag_by_name("warning", start_iter, end_iter)
        text_buffer.remove_tag_by_name("hint", start_iter, end_iter)

    def refresh_annotations_tags(self):
        # Start by removing all previous annotations
        self.clear_annotations()

        # Then add the new ones
        if self.show_annotations.get_active() and self._annotations:
            buffer = self.text_view.get_buffer()
            for annotation in self._annotations:
                start_iter = buffer.get_iter_at_offset(
                    annotation.offset
                )
                end_iter = buffer.get_iter_at_offset(
                    annotation.offset + annotation.length
                )
                buffer.apply_tag_by_name(
                    annotation.category, start_iter, end_iter
                )

    @Gtk.Template.Callback()
    def on_show_annotations_toggled(self, _toggle_button):
        self.refresh_annotations_tags()

    @Gtk.Template.Callback()
    def on_writer_unmap(self, _toggle_button):
        logger.info("Writer closed")
        if self.active_scene is not None:
            # Update the content of the scene and save it to disk
            self.active_scene.set_content(
                buffer_to_html(self.text_view.get_buffer())
            )
            self.active_scene.save()

    def on_buffer_changed(self, text_buffer):
        """Keep an eye on modifications of the buffer."""

        # If the popup was visible hide it
        self.popover_annotation.popdown()

        # If there was already a time out check cancel it
        if self._idle_timeout_id:
            GLib.source_remove(self._idle_timeout_id)

        # Schedule a new idle check in some time from now
        self._idle_timeout_id = GLib.timeout_add(
            EDITOR_IDLE_TIMEOUT_TIME,
            self.on_editor_idle
        )

