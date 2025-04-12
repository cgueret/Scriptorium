# plotting_entity.py
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

import logging
logger = logging.getLogger(__name__)


@Gtk.Template(resource_path="/com/github/cgueret/Scriptorium/ui/editor/plotting_entity.ui")
class PlottingEntityPanel(Adw.Bin):
    __gtype_name__ = "PlottingEntityPanel"

    def metadata(self):
        logger.info("Metadata")
        return {
            "icon_name": "system-users-symbolic",
            "title": "People",
            "description": "Blah"
        }

    def bind_to_manuscript(self, manuscript):
        logger.info('Bind')
        self._manuscript = manuscript
