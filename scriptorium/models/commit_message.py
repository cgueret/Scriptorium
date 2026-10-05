# models/commit_message.py
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
"""Model for storing information about manuscripts and their content."""

import logging

from gi.repository import GObject

logger = logging.getLogger(__name__)


class CommitMessage(GObject.Object):
    """A commit message is a message with a date."""

    def __init__(self, datetime, message):
        """Create a new message."""
        super().__init__()

        self._datetime = datetime
        self._message = message

    @GObject.Property(type=str)
    def datetime(self) -> str:
        return self._datetime

    @GObject.Property(type=str)
    def message(self) -> str:
        return self._message
