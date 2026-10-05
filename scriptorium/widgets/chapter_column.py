# chapter_column.py
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
import logging

from gi.repository import Adw, Gdk, GObject, Gtk

from scriptorium.globals import BASE
from scriptorium.models import Chapter

from .scene import SceneCard

logger = logging.getLogger(__name__)


@Gtk.Template(resource_path=f"{BASE}/widgets/chapter_column.ui")
class ChapterColumn(Adw.Bin):
    __gtype_name__ = "ChapterColumn"

    scenes_list = Gtk.Template.Child()
    column = Gtk.Template.Child()
    _chapter = None

    def __init__(self, **kwargs):
        """Create a new instance of the class."""
        super().__init__(**kwargs)

        # We also configure a chapter as a drop source to move them
        drag_source = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
        drag_source.connect("prepare", self.on_prepare_chapter)
        drag_source.connect("drag-begin", self.on_drag_begin_chapter)
        self.column.add_controller(drag_source)

        # Configure a chapter as drop target for a scene
        drop_target = Gtk.DropTarget.new(Chapter, Gdk.DragAction.MOVE)
        drop_target.connect("drop", self.on_drop_chapter_into_chapter)
        self.column.add_controller(drop_target)

    def connect_to_chapter(self, chapter: Chapter):
        """Connect the column to a chapter."""
        self._chapter = chapter

        # Set the title of the column
        self.column.set_title(chapter.title)

        # Set the column header text
        text = chapter.synopsis
        if len(chapter.synopsis) > 128:
            text = chapter.synopsis[:128] + "..."
        self.column.set_description(text)

        # Connect the model for the scenes
        self.scenes_list.bind_model(chapter.scenes, self.bind_card)

    def bind_card(self, scene):
        """Bind a scene card to a scene."""
        scene_card = SceneCard(scene)
        return scene_card

    def on_prepare_chapter(self, _source, _x, _y):
        """Prepare for a DnD by attaching the scene card to the event."""
        logger.info("Prepare chapter")
        # Set our chapter as the data being moved
        value = GObject.Value()
        value.init(Chapter)
        value.set_object(self._chapter)
        return Gdk.ContentProvider.new_for_value(value)

    def on_drag_begin_chapter(self, _source, drag):
        """Handle the chapter starts being dragged around."""
        logger.debug("Drag chapter")
        # Take a snaphot of the card and set it as icon
        snapshot = Gtk.WidgetPaintable.new(self)
        icon = Gtk.DragIcon.get_for_drag(drag)
        icon.set_child(Gtk.Picture.new_for_paintable(snapshot))

    def on_drop_chapter_into_chapter(self, _drop, chapter, _x, _y):
        """Drop a chapter where another chapter is located."""
        # Move the chapter
        logger.info(f"Move {chapter.title} where {self._chapter.title} is")
        chapter.project.manuscript.splice_chapters(chapter, self._chapter)
