# models/scene.py
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

from pathlib import Path
from gi.repository import Gtk, GObject, Gio
from scriptorium.utils import html_to_buffer, buffer_to_html
from .commit_message import CommitMessage
from .entity import Entity
from .resource import Resource

import logging

logger = logging.getLogger(__name__)


class Scene(Resource):
    """A scene is a basic building block of manuscripts."""

    __gtype_name__ = "Scene"

    entities = GObject.Property(type=Gio.ListStore)

    def __init__(self, project, identifier: str):
        """Create a scene."""
        super().__init__(project, identifier)
        self._history = Gio.ListStore.new(item_type=CommitMessage)
        self.entities = Gio.ListStore.new(item_type=Entity)

        # The base directory for the data of the scene
        base_directory = project.base_directory / Path("scenes")
        if not base_directory.exists():
            base_directory.mkdir()

        # The content of the scene
        self._scene_content_path = base_directory / Path(f"{self.identifier}.html")
        if not self._scene_content_path.exists():
            self._scene_content_path.touch()

        # Lazy loaded later
        self._scene_content = None

        self._refresh_history()

    @property
    def data_files(self):
        # An eventual list of data files associated with the resource
        return [self._scene_content_path]

    @property
    def history(self):
        """Return the history of commits about that scene."""
        return self._history

    @GObject.Property(type=GObject.Object)
    def chapter(self):
        """Return the chapter the scene is associated to, if any."""
        for chapter in self.project.manuscript.chapters:
            found, _ = chapter.scenes.find(self)
            if found:
                return chapter
        return None

    def connect_to(self, entity):
        """Connect this scene to an entity."""
        if entity not in self.entities:
            self.entities.append(entity)

    def disconnect_from(self, entity):
        """Disconnect this scene from an entity."""
        found, position = self.entities.find(entity)
        if found:
            self.entities.remove(position)

    def load_into_buffer(self, buffer: Gtk.TextBuffer):
        """Load the content of a text buffer from disk."""
        logger.info(f"{self.title}: Loading info buffer")

        # Load the content of the file and push to the buffer
        html_to_buffer(self.to_html(), buffer)

    def save_from_buffer(self, buffer: Gtk.TextBuffer):
        """Save the content of a text buffer to disk."""
        logger.info(f"{self.title}: Saving from buffer")

        # Write the content of the buffer
        self._scene_content = buffer_to_html(buffer)
        self._scene_content_path.write_text(self._scene_content)

        # Check if the file has been changed
        repo = self.project.repo
        for d in repo.index.diff(None):
            if str(self._scene_content_path.resolve()).endswith(d.a_path):
                repo.index.add(self._scene_content_path)
                repo.index.commit(f'Modified scene "{self.identifier}"')
                # Trigger a refresh of the commit history
                self._refresh_history()

    def to_html(self):
        """Return the HTML payload for the scene."""
        # Check if we can do that
        if not self._scene_content_path.exists():
            raise FileNotFoundError(f"Could not open {self._scene_content_path}")

        # Load from disk if we need to
        if self._scene_content is None:
            logger.info(f"Loading raw HTML from {self._scene_content_path}")
            self._scene_content = Path(self._scene_content_path).read_text()

        return self._scene_content

    def _refresh_history(self):
        self._history.remove_all()
        commits = self.project.repo.iter_commits(
            all=True,
            paths=self._scene_content_path
        )
        for commit in commits:
            datetime = commit.committed_datetime
            message_datetime = datetime.strftime("%A %d %B %Y, %H:%M:%S")
            message = commit.message.strip()
            msg = CommitMessage(message_datetime, message)
            self._history.append(msg)


