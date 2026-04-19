# window.py
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

import logging
from gi.repository import Gtk, Adw, GObject, Gdk, Gio, GLib
from pathlib import Path

# Needed here for some weird reason, Builder does not find it otherwise
# TODO: idea: maybe instantiate the libraryview and reset it on folder change
from scriptorium.views import ScrptLibraryView

from scriptorium.models import Project
from scriptorium.globals import BASE

logger = logging.getLogger(__name__)

# Design choice: we create and add the navigation panels for the editor as
# they are activated and push. Later on we will be able to easily spawn them
# as separate window instead if this is what the user would prefer

@Gtk.Template(resource_path=f'{BASE}/window.ui')
class ScrptWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ScrptWindow'

    navigation = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()

    # This is a pointer to the currently open project, defaults to None
    #project = GObject.Property(
    #    type=Project,
    #    default=None
    #)

    # The base path of all the manuscripts
    manuscripts_folder = GObject.Property(
        type=str,
        default=None
    )

    # This is the identifier of the manuscript that was last opened
    last_manuscript_name = GObject.Property(
        type=str,
        default=None
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load custom CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_file(
            Gio.File.new_for_uri(f"resource:/{BASE}/style.css")
        )
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Load custom icons
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        theme.add_resource_path(f"{BASE}/icons")

        # Load the settings up
        self.settings = Gio.Settings(schema_id="io.github.cgueret.Scriptorium")

        # Bind the settings related to the window
        self.settings.bind(
            "window-width", self, "default-width",
            Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "window-height", self, "default-height",
            Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "window-maximized", self, "maximized",
            Gio.SettingsBindFlags.DEFAULT
        )

        # Bindings related to projects management
        self.settings.bind(
            "last-manuscript-name", self, "last-manuscript-name",
            Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "manuscripts-folder", self, "manuscripts-folder",
            Gio.SettingsBindFlags.DEFAULT
        )

        # Create a property for last open project and connect that to a setting
        # Notify for changes here; check if correct version before pushing
        # if all fine push to editor
        # If notify indicate the current project is None push library view

        # When editor is closed it sets the open project to None

        # When an item is clicked in the library the project is set to the value

        # self._open_library()

        # The library is where a project is selected by the user. We keep an
        # eye on actions there
        #self.connect(
        #    'notify::project',
        #    self.on_project_changed
        #)

        # Open the default data directory
        # (TODO Implement the setting for data folder)
        #projects_path = Path(self.manuscripts_folder) / Path('manuscripts')
        #if not projects_path.exists():
        #    projects_path.mkdir()
        #self.projects_base_path = projects_path.resolve()

    @Gtk.Template.Callback()
    def on_scrptwindow_realize(self, window):
        """Called with the window is created."""

        # See if we have a manuscript folder path set
        # If not, use the app base directory
        if not self.manuscripts_folder or self.manuscripts_folder == "":
            folder = Path(GLib.get_user_data_dir()) / "manuscripts"
            folder.mkdir(exist_ok=True)
            self.manuscripts_folder = folder

        # Inform the user of the data folder
        logger.info(f'Data location: {self.manuscripts_folder}')

        # Open the library at this location
        self._open_library()

    @Gtk.Template.Callback()
    def on_close_request(self, event):
        logger.info("Window close requested")
        # Save the name of the last edited project

    def _open_library(self):
        """Create a library panel and add it to the navigation."""

        # Create a library panel
        library_panel = ScrptLibraryView(self.manuscripts_folder)

        # Add it to the navigation
        self.navigation.push(library_panel)

    def close_editor(self, editor_view):
        self.navigation.pop()

    def inform(self, message: str):
        toast = Adw.Toast.new(title=message)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)
