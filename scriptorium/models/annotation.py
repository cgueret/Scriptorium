# models/annotation.py
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
# TODO: Turn those into a Resource managed via the project to handle
# sharing annotation across authors

from gi.repository import GObject, Gtk
import logging

logger = logging.getLogger(__name__)


class Annotation(GObject.Object):
    """An annotation is a section of a text marked with some text."""

    __gtype_name__ = "Annotation"

    title = GObject.Property(type=str)
    message = GObject.Property(type=str)
    category = GObject.Property(type=str)
    offset = GObject.Property(type=int)
    length = GObject.Property(type=int)
    suggestions = GObject.Property(type=Gtk.StringList)

    def __init__(self):
        """Create a new instance of Chapter."""
        super().__init__()
        self.suggestions = Gtk.StringList()
