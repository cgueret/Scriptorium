# widgets/cards_list.py
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
"""Widget to display a list of cards."""

from gi.repository import Gtk, GObject, Gdk, Gio, Adw
import logging

logger = logging.getLogger(__name__)

# TODO: Enhance the widget with a placeholder to show when list is empty

class CardDropZone(Gtk.Box):
    __gtype_name__ = "CardDropZone"

    def __init__(self, parent):
        """Create an instance of the drop zone."""
        super().__init__()
        self._parent = parent

        self.set_size_request(120, 120)
        if self._parent.get_orientation() == Gtk.Orientation.VERTICAL:
            self.set_hexpand(True)
            self.set_vexpand(False)
        else:
            self.set_hexpand(False)
            self.set_vexpand(True)

        motion_target = Gtk.DropTarget.new(
            self._parent.model.get_item_type(), Gdk.DragAction.MOVE
        )
        motion_target.connect("drop", self.on_drop)
        self.add_controller(motion_target)

        self.connect("state-flags-changed", self.on_state_flags_changed)

    def on_drop(self, _target, entry, _x, _y):
        logger.info(f"Drop {entry.title} onto drop zone")

        # Append the entry to the model
        self._parent.model.append(entry)

        return True

    def on_state_flags_changed(self, widget, _previous_flags):
        """Manually remove the highlight area."""
        sc = widget.get_style_context()
        current = sc.get_state()
        cleaned = current & ~Gtk.StateFlags.DROP_ACTIVE
        if cleaned != current:
            sc.set_state(cleaned)


class Card(Adw.Bin):
    __gtype_name__ = "Card"

    def __init__(self, parent, create_widget_func, entry):
        """Create an instance of the card."""
        super().__init__()
        self._parent = parent
        self._create_widget_func = create_widget_func
        self._entry = entry
        self._widget = create_widget_func(entry)

        self._moved_x = None
        self._moved_y = None

        # Adjust the base margins
        self.margin_bottom = 12

        self.box = Gtk.Box()
        self.box.set_hexpand(True)
        self.box.add_css_class("card")
        self.box.add_css_class("activatable")
        self.box.set_margin_top(0)
        self.box.set_margin_bottom(self.margin_bottom)
        self.box.append(self._widget)
        self.set_child(self.box)

        # Configure it as a drag source
        drag_source = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
        drag_source.connect("prepare", self.on_drag_prepare)
        drag_source.connect("drag-begin", self.on_drag_begin)
        drag_source.connect("drag-cancel", self.on_drag_cancel)
        drag_source.connect("drag-end", self.on_drag_end)
        self.add_controller(drag_source)

        motion_target = Gtk.DropTarget.new(
            self._parent.model.get_item_type(), Gdk.DragAction.MOVE
        )
        motion_target.connect("enter", self.on_enter)
        motion_target.connect("drop", self.on_drop)
        motion_target.connect("motion", self.on_motion)
        motion_target.connect("leave", self.on_leave)
        self.add_controller(motion_target)

        self.connect("state-flags-changed", self.on_state_flags_changed)

    @GObject.Property(type=Gtk.Widget)
    def widget(self):
        return self._widget

    def get_title(self):
        return self._entry.title

    def on_drag_prepare(self, _source, x, y):
        logger.info(f"Prepare {x} {y}")
        value = GObject.Value()
        value.init(type(self._entry))
        value.set_object(self._entry)
        self._moved_x = x
        self._moved_y = y

        return Gdk.ContentProvider.new_for_value(value)

    def on_drag_begin(self, _source, drag):
        # Create a new widget of the same size
        _got_bounds, _x, _y, width, height = self.get_bounds()
        box = Gtk.Box(hexpand=True)
        box.add_css_class("card")
        box.set_size_request(width, height)
        box.append(self._create_widget_func(self._entry))
        box.set_opacity(0.9)
        box.last_parent_list = self._parent

        # Set it as the icon
        icon = Gtk.DragIcon.get_for_drag(drag)
        icon.set_child(box)

        # Set the hotspot to be where we grabbed the card
        drag.set_hotspot(self._moved_x, self._moved_y)

        # Remove from the model the entry we just picked
        found, self._picked_from_index = self._parent.model.find(self._entry)
        if found:
            self._parent.model.remove(self._picked_from_index)

        self._parent.emit("start-drag")

        return True

    def on_drag_cancel(self, _source, drag, _reason):
        logger.info(f"Cancelled, return entry to {self._picked_from_index}")
        self._parent.model.insert(self._picked_from_index, self._entry)

        return True

    def on_drag_end(self, _source, _drag, _):
        self._parent.emit("stop-drag")
        return True

    def on_enter(self, source, enter_x, enter_y):
        logger.info(f"Enter {self._entry.title} ")
        self.set_margins(source, enter_y, force_top=True)
        return Gdk.DragAction.MOVE

    def on_motion(self, source, motion_x, motion_y):
        self.set_margins(source, motion_y)

        return Gdk.DragAction.MOVE

    def on_leave(self, _source):
        logger.info(f"Leave {self._entry.title}")
        self.box.set_margin_top(0)
        self.box.set_margin_bottom(self.margin_bottom)

    def on_drop(self, _target, entry, _x, y):
        logger.info(f"Drop {entry.title} onto {self._entry.title}")
        _got_bounds, _x, _y, width, height = self.box.get_bounds()

        # Find ourselves
        found, index = self._parent.model.find(self._entry)

        if y < height / 2:
            # Insert before
            self._parent.model.insert(index, entry)
        else:
            # Insert after
            self._parent.model.insert(index + 1, entry)

        self._parent.emit("stop-drag")

        return True

    def set_margins(self, source, y, force_top=False):
        drag = source.get_current_drop().get_drag()
        icon = Gtk.DragIcon.get_for_drag(drag)
        value = icon.get_child()
        _got_bounds, _x, _y, width, height = value.get_bounds()

        if y < height / 2 or force_top:
            self.box.set_margin_top(height)
            self.box.set_margin_bottom(self.margin_bottom)
        else:
            self.box.set_margin_top(0)
            self.box.set_margin_bottom(height + self.margin_bottom)

    def on_state_flags_changed(self, widget, _previous_flags):
        """Manually remove the highlight area."""
        sc = widget.get_style_context()
        current = sc.get_state()
        cleaned = current & ~Gtk.StateFlags.DROP_ACTIVE
        if cleaned != current:
            sc.set_state(cleaned)


class CardsList(Gtk.Box):
    """Widget to display a list of cards"""

    __gtype_name__ = "CardsList"

    __gsignals__ = {
            # signal_name: (flags, return_type, argument_types)
            "start-drag": (GObject.SignalFlags.RUN_FIRST, None, ()),
            "stop-drag": (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    def __init__(self):
        super().__init__()

        # By default the list is vertical
        self.set_orientation(Gtk.Orientation.VERTICAL)

    def bind_model(self, model, create_widget_func) -> None:
        """Connect the widget to a model."""

        # Keep track of the attributes
        self._model = model
        self._create_widget_func = create_widget_func

        # Connect the signal to refresh the widgets
        self._model.connect("items-changed", self.on_items_changed)

        # Initialise the content
        for entry in self._model:
            card = Card(self, self._create_widget_func, entry)
            self.append(card)

        # Add the dropzone
        self._drop_zone = CardDropZone(self)
        self.append(self._drop_zone)
        self._drop_zone.set_visible(self._model.get_n_items() == 0)

    @GObject.Property(type=Gio.ListStore)
    def model(self):
        return self._model

    def on_items_changed(self, _liststore, position, removed, added):
        """Handle a request to update the content of the list."""

        # Remove widgets for removed items
        for _ in range(removed):
            child = self.get_child_at(position)
            self.remove(child)

        # Add widgets for added items
        for i in range(added):
            entry = self._model.get_item(position + i)
            card = Card(self, self._create_widget_func, entry)
            child = self.get_child_at(position + i - 1)
            self.insert_child_after(card, child)

        # Set the visibility of the drop zone
        self._drop_zone.set_visible(self._model.get_n_items() == 0)

    def get_child_at(self, position):
        # In the special case we ask for -1 return None
        if position < 0:
            return None

        # Iterate until the desired position, or running out of children
        index = 0
        child = self.get_first_child()
        while index != position and child is not None:
            child = child.get_next_sibling()
            index += 1

        # We reached the end of the list, return the last child
        if child is None:
            return self.get_last_child()

        return child

