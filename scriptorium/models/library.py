# models/library.py
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
"""A Library is a collection of manuscripts."""

from pathlib import Path
from gi.repository import GObject, Gio
import logging
import uuid
import shutil

from .project import Project
from .manuscript import Manuscript

logger = logging.getLogger(__name__)


class Library(GObject.Object):
    """The library is the collection of projects."""

    projects: GObject.Property = GObject.Property(type=Gio.ListStore)

    def __init__(
        self,
    ):
        """Create an instance of the library for the target folder."""
        super().__init__()

        # List of manuscripts
        self.projects = Gio.ListStore(item_type=Project)

    def open_folder(self, base_directory: str):
        # Keep track of attributes
        self._base_directory = Path(base_directory)

        # Create one manuscript entry per directory
        logger.info(f"Scanning content of {self._base_directory}")
        self.projects.remove_all()
        for directory in self._base_directory.iterdir():
            if not directory.is_dir():
                continue
            try:
                project = Project(directory)
                self.projects.append(project)
                logger.info(f"Added project {directory.name}")
            except Exception:
                logger.warning("Ignoring %s", directory.name, exc_info=True)

    @property
    def base_directory(self) -> Path:
        """The base directory where all the manuscripts are located."""
        return self._base_directory

    def create_project(self, title: str, synopsis: str = None):
        """Create a new project with a manuscript in it."""
        logger.info("Create project")

        # Create a new identifier, we use a UUID so that several manuscripts
        # may share the same name
        identifier = str(uuid.uuid4())

        # Create the manuscript
        path = self.base_directory / Path(identifier)

        # Create the project
        project = Project(path)

        # Set the title of the project to the indicated title
        project.title = title

        # Add a manuscript to the project (that will trigger a save)
        project.create_resource(Manuscript, title, synopsis)

        # Add it to the list
        self.projects.append(project)

    def delete_project(self, project):
        """Delete the project from disk."""

        found, position = self.projects.find(project)
        if found:
            # Remove from the library
            self.projects.remove(position)

            # Delete all the content on disk
            path = self.base_directory / Path(project.identifier)
            shutil.rmtree(path)

    def get_project(self, identifier):
        """Return a project based on a requested identifier."""

        # Iterate until we find the correct project
        for project in self.projects:
            if project.identifier == identifier:
                return project

        # That does not seem to be here
        logger.warning(f"Project not found: {identifier}")
        return None
