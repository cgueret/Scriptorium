# main.py
#
# Copyright 2025 Christophe Guéret
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
# Set the target version of the libraries
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("WebKit", "6.0")
gi.require_version("Soup", "3.0")
import sys

from .application import ScriptoriumApplication
import logging

logging.basicConfig(
    level=logging.INFO, format="%(name)-40s: %(levelname)-8s %(message)s"
)
logger = logging.getLogger(__name__)


def main(version):
    """The application's entry point."""
    logger.info(f"Starting Scriptorium {version}")
    app = ScriptoriumApplication()
    return app.run(sys.argv)
