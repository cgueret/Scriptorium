# widgets/theme_selector.py
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

# Code adapted from libpanel:
# https://gitlab.gnome.org/GNOME/libpanel/-/blob/main/src/panel-theme-selector.c

import logging

from gi.repository import Adw, GLib, Gtk

from scriptorium.globals import BASE

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/widgets/theme_selector.ui")
class ThemeSelector(Adw.Bin):
    __gtype_name__ = "ThemeSelector"

    box = Gtk.Template.Child()
    dark = Gtk.Template.Child()
    light = Gtk.Template.Child()
    follow = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        style_manager = Adw.StyleManager.get_default()

        style_manager.connect(
            "notify::system-supports-color-schemes",
            self.on_notify_system_supports_color_schemes,
        )

        style_manager.connect("notify::dark", self.on_notify_dark)

        self.action_name = "app.style-variant"
        self.dark.set_action_target_value(GLib.Variant("s", "dark"))
        self.dark.set_action_name(self.action_name)
        self.light.set_action_target_value(GLib.Variant("s", "light"))
        self.light.set_action_name(self.action_name)
        self.follow.set_action_target_value(GLib.Variant("s", "default"))
        self.follow.set_action_name(self.action_name)

    def on_notify_system_supports_color_schemes(self, style_manager):
        visible = style_manager.get_system_supports_color_schemes()
        self.set_visible(visible)

    def on_notify_dark(self, style_manager, _value):
        if style_manager.get_dark():
            self.add_css_class("dark")
        else:
            self.remove_css_class("dark")
