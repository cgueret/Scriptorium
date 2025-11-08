# application.py
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
from scriptorium.dialogs import ScrptPreferencesDialog
from gi.repository import Gio, Adw, GLib, GObject
from .window import ScrptWindow
from .language_tool import LanguageTool
import logging

import gettext
gettext.bindtextdomain('scriptorium', '/usr/share/locale')
gettext.textdomain('scriptorium')
from gettext import gettext as _

logging.basicConfig(
    level=logging.INFO,
    format='%(name)-40s: %(levelname)-8s %(message)s'
)
logger = logging.getLogger(__name__)


class ScriptoriumApplication(Adw.Application):
    """The main application singleton class."""

    # The LanguageTool wrapper
    language_tool = GObject.Property(type=LanguageTool)

    def __init__(self):
        super().__init__(application_id='io.github.cgueret.Scriptorium',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        self.connect("startup", self.on_startup)
        self.connect("shutdown", self.on_shutdown)

    def change_color_scheme(self, _settings, value):
        """Handle a change in the select color scheme setting."""
        color_scheme = self.settings.get_string(value)

        style_manager = Adw.StyleManager.get_default()
        if color_scheme == 'dark':
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif color_scheme == 'light':
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif color_scheme == 'default':
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        window = self.props.active_window
        if not window:
            window = ScrptWindow(application=self)
        window.present()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(
            application_name='Scriptorium',
            application_icon='io.github.cgueret.Scriptorium',
            developer_name='Christophe Guéret',
            version='1.1.0',
            website='https://github.com/cgueret/Scriptorium',
            developers=[
                'Christophe Guéret <christophe.gueret@gmail.com>',
                'Diego C Sampaio https://github.com/kriptolix'
            ],
            copyright='© 2025 Christophe Guéret'
        )
        about.add_credit_section(
            _('Beta testing'),
            ['TheShadowOfHassen https://github.com/TheShadowOfHassen']
        )
        # Translators: Replace "translator-credits" with your name/username,
        # and optionally an email or URL.
        # about.set_translator_credits(_('translator-credits'))
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        logger.info('app.preferences action activated')
        preferences = ScrptPreferencesDialog()
        preferences.present(self.props.active_window)

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def on_startup(self, _application):
        """
        Handle the application startup.
        """
        # Create the basic application actions
        self.create_action('quit', lambda *_: self.quit())
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

        # Check which theme should be applies
        self.settings = Gio.Settings(
            schema_id="io.github.cgueret.Scriptorium"
        )
        style_variant_action = self.settings.create_action("style-variant")
        self.add_action(style_variant_action)
        self.settings.connect(
            "changed::style-variant",
            self.change_color_scheme
        )

        # Get the current color scheme
        current_value = self.settings.get_string("style-variant")
        style_variant_action.activate(GLib.Variant('s', current_value))

        # Instantiate our language tool interface
        self.language_tool = LanguageTool()

    def on_shutdown(self, _application):
        # Instantiate our language tool interface
        self.language_tool.shutdown()


