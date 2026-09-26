# views/plan/editor_images_item.py
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

import logging

logger = logging.getLogger(__name__)


ANIMATION_DURATION = 100


def animate_opacity(widget, from_value, to_value):
    animation_target = Adw.PropertyAnimationTarget.new(widget, "opacity")
    animation = Adw.TimedAnimation.new(
        widget, from_value, to_value, ANIMATION_DURATION, animation_target
    )
    animation.play()


@Gtk.Template(resource_path=f"{BASE}/views/plan/editor_images_item.ui")
class ImageItem(Gtk.Overlay):
    __gtype_name__ = "ImageItem"

    picture = Gtk.Template.Child()
    remove_image_button = Gtk.Template.Child()
    set_as_cover_button = Gtk.Template.Child()

    def __init__(self, image):
        super().__init__()

        # Add the picture
        self.picture.set_paintable(image.texture)

        # Connect to action to delete the image
        self.remove_image_button.set_detailed_action_name(
            f"editor.delete_resource('{image.identifier}')"
        )

    @Gtk.Template.Callback()
    def on_eventcontrollermotion_enter(self, _src, _x, _y):
        animate_opacity(self.remove_image_button, 0.0, 1.0)

    @Gtk.Template.Callback()
    def on_eventcontrollermotion_leave(self, _src):
        animate_opacity(self.remove_image_button, 1.0, 0.0)
