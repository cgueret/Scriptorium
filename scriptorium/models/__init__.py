# models/__init__.py
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
"""Data models for all the custom objects managed by Scriptorium."""

from .annotation import Annotation
from .chapter import Chapter
from .commit_message import CommitMessage
from .entity import Entity
from .image import Image
from .library import Library
from .manuscript import Manuscript
from .project import Project
from .resource import Resource
from .scene import Scene

__all__ = [
    "Annotation",
    "Chapter",
    "CommitMessage",
    "Entity",
    "Image",
    "Library",
    "Manuscript",
    "Project",
    "Resource",
    "Scene",
]
