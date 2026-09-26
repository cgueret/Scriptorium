# views/write/navigation_item.py
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
import enum
import logging

from gi.repository import Adw, Gdk, Gio, GObject, Gtk

from scriptorium.globals import BASE
from scriptorium.models import Manuscript, Chapter, Resource

logger = logging.getLogger(__name__)

DRAGGING_OPACITY = 0.4
BASE_MARGIN = 3
ANIMATION_SPEED = 200


class State(enum.IntEnum):
    NEUTRAL = 0
    PUSHED = 1


class SpecialItem(enum.IntEnum):
    MANUSCRIPT = 0
    DRAFTS = 1


@Gtk.Template(resource_path=f"{BASE}/views/write/navigation_item.ui")
class NavigationItem(Adw.Bin):
    __gtype_name__ = "NavigationItem"

    resource = GObject.Property(type=Resource)
    parent_model = GObject.Property(type=Gio.ListStore)
    is_dragged = GObject.Property(type=bool, default=False)
    is_animated = GObject.Property(type=bool, default=False)
    push_state = GObject.Property(type=int, default=State.NEUTRAL)
    hovering = GObject.Property(type=bool, default=False)

    content = Gtk.Template.Child()
    expander = Gtk.Template.Child()
    label = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.label_binding = None

        self.content.set_margin_top(BASE_MARGIN)
        self.content.set_margin_bottom(BASE_MARGIN)

        drag_source = Gtk.DragSource()
        drag_source.set_actions(Gdk.DragAction.MOVE)
        drag_source.connect("prepare", self.on_drag_prepare)
        drag_source.connect("drag-begin", self.on_drag_begin)
        drag_source.connect("drag-end", self.on_drag_end)
        self.add_controller(drag_source)

        drop_target = Gtk.DropTarget()
        drop_target.set_gtypes([NavigationItem])
        drop_target.set_actions(Gdk.DragAction.MOVE)
        drop_target.connect("drop", self.on_drop)
        drop_target.connect("enter", self.on_enter)
        drop_target.connect("leave", self.on_leave)
        self.add_controller(drop_target)

        gesture = Gtk.GestureClick.new()
        gesture.set_button(3)  # Right-click
        gesture.connect("pressed", self.on_right_click)
        self.add_controller(gesture)

        self.connect("notify::resource", self.on_resource_set)

    def on_drag_prepare(self, _source, _x, _y):
        """Prepare for a DnD event by attaching the element being grabbed."""
        # We cannot drag root nodes
        if isinstance(self.resource, Manuscript):
            return None

        # Attache ourselves to the drag event
        value = GObject.Value(value_type=NavigationItem, py_value=self)
        return Gdk.ContentProvider.new_for_value(value)

    def on_drag_begin(self, source, drag):
        """Attach a widget to the drag icon."""
        # If we are expanded collapse first
        list_row = self.expander.get_list_row()
        if list_row.is_expandable() and list_row.get_expanded():
            list_row.set_expanded(False)

        # Create a drag widget with just our label
        widget = Gtk.ListBox()
        widget.add_css_class("navigation-sidebar")
        entry = Gtk.Label(label=self.label.get_label())
        widget.append(entry)
        widget.select_row(widget.get_row_at_index(0))
        icon = Gtk.DragIcon.get_for_drag(drag)
        icon.set_child(widget)

        # Update the state of the widget to show it being dragged
        self.is_dragged = True
        self.set_opacity(DRAGGING_OPACITY)

    def on_drag_end(self, source, drag, _):
        """Return the widget to a normal state."""
        self.is_dragged = False
        self.set_opacity(1)

    def on_drop(self, _drop, item, _x, _y):
        """Drop item after ourselves."""

        # Remove the resource from its original location
        found_item, position_item = item.parent_model.find(item.resource)
        item.parent_model.remove(position_item)

        # Check if we are a container and currently expanded
        list_row = self.expander.get_list_row()
        if list_row.is_expandable() and list_row.get_expanded():
            # If we are an open container the user will see a space under the
            # expander and expect the item to land there, that is as the first
            # item of the list
            own_model = list_row.get_children()
            own_model.insert(0, item.resource)
        else:
            # Find our position in the parent model
            found_self, position_self = self.parent_model.find(self.resource)
            self.parent_model.insert(position_self + 1, item.resource)

    def on_leave(self, _source):
        self._animate(State.NEUTRAL, BASE_MARGIN)

    def on_enter(self, drop_target, motion_x, motion_y):
        # Ignore the visit if we are the line dragged
        if self.is_dragged:
            return Gdk.DragAction.MOVE

        # Don't do anything while moving or if we are already pushed
        if self.is_animated or self.push_state == State.PUSHED:
            return Gdk.DragAction.MOVE

        drag = drop_target.get_current_drop().get_drag()
        icon = Gtk.DragIcon.get_for_drag(drag)
        value = icon.get_child()
        if value:
            _got_bounds, _x, _y, _width, visitor_height = value.get_bounds()

            next_sibling = self.get_parent().get_next_sibling()
            if next_sibling and not next_sibling.get_first_child().is_dragged:
                self._animate(State.PUSHED, visitor_height)

        return Gdk.DragAction.MOVE

    def on_animate_step(self, value, target_state, offset):
        box = self.content

        if target_state == State.PUSHED:
            box.set_margin_bottom(int(value))
        elif target_state == State.NEUTRAL:
            if self.push_state == State.PUSHED:
                box.set_margin_bottom(BASE_MARGIN + offset - int(value))

    def on_animation_done(self, _animation, target_state, offset):
        self.push_state = target_state
        self.is_animated = False

    def _animate(self, target_state, offset):
        animation_target = Adw.CallbackAnimationTarget.new(
            self.on_animate_step, target_state, offset
        )
        animation = Adw.TimedAnimation.new(
            self.content, BASE_MARGIN, offset, ANIMATION_SPEED, animation_target
        )
        self.is_animated = True
        animation.play()
        animation.connect("done", self.on_animation_done, target_state, offset)

    def on_resource_set(self, _src, _value):
        """Update the entry according to the resource that has been set."""

        # Unbind previous label if there was a binding defined
        if self.label_binding is not None:
            self.label_binding.unbind()

        # Bind with the label of the resource, this is necessary in case the
        # user modifies the label from the details panel
        self.label_binding = self.resource.bind_property(
            "title",
            self.label,
            "label",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE,
        )

    def on_right_click(self, src, _n_press, _x, _y):
        """Show a popover menu for relevant actions."""

        # We will need the identifier of our resource
        id = self.resource.identifier

        # Define the menu, Chapters can offer to add Chapter or Scene as child
        # Both can propose to be deleted. Later on we will have more options
        # (move to draft, flag as need re-work, ...)
        menu = Gio.Menu()

        # Main menu to add new Chapter or Scene for container nodes
        if isinstance(self.resource, (Manuscript, Chapter)):
            menu.append(
                label="Add new child Chapter",
                detailed_action=f"editor.add_resource(('Chapter', '{id}'))",
            )
            menu.append(
                label="Add new child Scene",
                detailed_action=f"editor.add_resource(('Scene', '{id}'))",
            )

        # Add a menu to delete the resource, unless it's a root node
        if not isinstance(self.resource, Manuscript):
            dangerous_section = Gio.Menu()
            dangerous_section.append(
                label="Delete", detailed_action=f"editor.delete_resource('{id}')"
            )
            menu.append_section(label=None, section=dangerous_section)

        # Create the popover menu and make it pop up
        popover = Gtk.PopoverMenu.new_from_model(menu)
        popover.set_parent(self)
        popover.set_autohide(True)
        popover.set_position(Gtk.PositionType.RIGHT)
        popover.popup()
