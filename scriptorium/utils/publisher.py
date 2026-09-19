# utils/publisher.py
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
from gi.repository import Gio
from scriptorium.models import Resource, Manuscript, Chapter, Scene
from scriptorium.globals import BASE
from ebooklib import epub

import io

import logging
logger = logging.getLogger(__name__)

# Create instances of PublisherSection and return the toc. When asked to export
# the book call the rest of the epub lib functions
# Need a separate call to get the CSS to render in the app. Maybe wrap that into a separate styling object
class Publisher(object):
    """
    Publisher is a helper class to encapsulate the content of the manuscript
    as a set of HTML files. This content can be used as a view in the editor
    or exported to disk as an epub.
    """

    def __init__(self, manuscript: Manuscript):
        """Create a new instance of a Publisher."""

        # Keep a pointer to the manuscript
        self._manuscript = manuscript

        # The EBook built from the manuscript
        self._book = None


    @property
    def table_of_contents(self):
        if self._book is None:
            self._build()

        return self._book.toc

    def rebuild(self):
        self._build()

    def _get_chapter_content(self, resource: Resource):
        # Create the buffer if needed
        buffer = io.StringIO()

        # Recursively extract the content of the chapter/scenes tree
        self._extract_content(resource, 1, buffer)

        # Close and return the buffer
        content = buffer.getvalue()
        buffer.close()

        return content

    def _extract_content(self, resource: Resource, depth, buffer, previous_was_scene = False):
        # If we just have a resource return that as is
        if isinstance(resource, Scene):
            # If what we wrote before was a scene, add a scene separator
            if previous_was_scene:
                buffer.write('<p class="separator">&nbsp;</p>\n')
            buffer.write(resource.get_content())

        # If we are in a Chapter add the header and recurse into the content
        if isinstance(resource, Chapter):
            usable_depth = min(depth, 6)  # HTML goes down to h6 at most
            if usable_depth == 1:
                buffer.write(f'<h{usable_depth} class="chapter-title">')
            else:
                buffer.write(f'<h{usable_depth}>')
            buffer.write(f'{resource.title}</h{usable_depth}>\n')

            # We keep track of the content just before to place scene separators
            previous_entry = None
            for entry in resource.content:
                self._extract_content(
                    entry, depth+1, buffer,
                    isinstance(previous_entry, Scene)
                )
                previous_entry = entry

    def save(self, target_file: str):
        if self._book is None:
            self._build()

        epub.write_epub(target_file, self._book, {})

    def _build(self):
        """Build a EPUB from the content of the manuscript."""
        logger.info("Building book")

        # Initialise the book
        self._book = epub.EpubBook()
        self._book.set_identifier(self._manuscript.identifier)
        self._book.set_title(self._manuscript.title)
        self._book.set_language(self._manuscript.language)
        self._book.toc = ()

        # Set the cover
        cover_img = self._manuscript.cover
        if cover_img is not None:
            self._book.set_cover(
                cover_img.path.name,
                open(cover_img.path, 'rb').read()
            )

        # Add the content
        for entry in self._manuscript.content:
            epub_html = epub.EpubHtml(
                title=entry.title,
                file_name=f"{entry.identifier}.xhtml",
                lang=self._manuscript.language
            )
            epub_html.set_content(self._get_chapter_content(entry))
            self._book.add_item(epub_html)
            self._book.toc += (epub_html,)

        # Define the spine
        self._book.spine = []
        if cover_img is not None:
            self._book.spine.append("cover")
        self._book.spine.append("nav")
        for part in self._book.toc:
            self._book.spine.append(part)

        # add default NCX and Nav file
        self._book.add_item(epub.EpubNcx())
        self._book.add_item(epub.EpubNav())

        # define CSS style
        style = Gio.File.new_for_uri(
            f"resource:/{BASE}/utils/epub-novel.css"
        ).load_contents()[1].decode()
        style_css = epub.EpubItem(
            uid="style_novel",
            file_name="style/novel.css",
            media_type="text/css",
            content=style,
        )

        # Add the CSS file to the book
        self._book.add_item(style_css)

        # Connect it to all the parts
        for part in self._book.toc:
            part.add_item(style_css)

