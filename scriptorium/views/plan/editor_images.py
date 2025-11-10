# views/plan/editor_images.py
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
from .editor_images_item import ImageItem

import logging

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/views/plan/editor_images.ui")
class ScrptImagesPanel(Adw.NavigationPage):
    __gtype_name__ = "ScrptImagesPanel"
    __icon_name__ = "image-x-generic-symbolic"
    __description__ = _("Gallery of images used in the project")
    __title__ = _("Gallery")

    images_box = Gtk.Template.Child()

    def __init__(self, editor, **kwargs):
        """Create an instance of the panel."""
        super().__init__(**kwargs)

        self._editor = editor

        # Connect the model of the flow box
        self.images_box.bind_model(editor.project.images, ImageItem)


