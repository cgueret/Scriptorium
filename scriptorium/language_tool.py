# language_tool.py
#
# Copyright 2025 Unknown
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
#
# Code inspired from https://github.com/sonnyp/Eloquent/blob/main/src/languagetool.js
from gi.repository import Gio, GObject, Soup, GLib
import json
import logging
from scriptorium.models import Annotation

logger = logging.getLogger(__name__)

SEND_PING_TIMEOUT_SECONDS = 1

# TODO Replace pings with a passive check, update alive everytime asked


class LanguageTool(GObject.Object):

    # This is True when we could connect to Language Tool, False otherwise
    server_is_alive = GObject.Property(type=bool, default=False)

    def __init__(self):
        super().__init__()

        # HTTP session to dialog with the server
        self._session = Soup.Session()

        # Used to connect to an internal instance when needed
        self._proc_language_tool = None

    def startup(self):
        """Startup the server."""
        if not self.server_is_alive:
            logger.info("Starting LanguageTool server")
            self._start_or_connect_to_server()

    def shutdown(self):
        """Shutdown the server."""
        # Only shut down the server if we manage the instance
        if self.server_is_alive and self._proc_language_tool:
            logger.info("Stopping internal LanguageTool server")
            self._proc_language_tool.force_exit()

        # The server is now offline
        self.server_is_alive = False

    def _start_or_connect_to_server(self):
        """
        Handle an attempt to either connect to an external instance of
        language tool or start an internal server.
        """

        # Send a ping to the port where LanguageTool is expected to be found
        message = Soup.Message.new("GET", "http://localhost:8081")
        self._session.send_and_read_async(
            message, GObject.PRIORITY_LOW, None, self._handle_ping_reply
        )

        # When called on a timeout, we don't want this to repeat
        return False

    def _handle_ping_reply(self, session, result):
        try:
            message = session.send_and_read_finish(result)
            if "LanguageTool API" in message.get_data().decode():
                logger.info("Connected to LanguageTool")
                self.server_is_alive = True
        except GLib.GError:
            # We could not connect
            self.server_is_alive = False

            # Let's try to start it
            logger.info("Starting internal LanguageTool server")

            # Start the subprocess
            if self._proc_language_tool is None:
                self._proc_language_tool = Gio.Subprocess.new(
                    [
                        "java",
                        "-cp",
                        "/app/LanguageTool/languagetool-server.jar",
                        "org.languagetool.server.HTTPServer",
                        "--allow-origin",
                        "--public",
                        "--port",
                        "8081",
                    ],
                    Gio.SubprocessFlags.INHERIT_FDS | Gio.SubprocessFlags.STDOUT_PIPE,
                )

            # Try to connect to it
            GLib.timeout_add_seconds(
                SEND_PING_TIMEOUT_SECONDS,
                self._start_or_connect_to_server
            )

    def languages(self, callback):
        """Get a list of supported languages."""

        # Send a request
        message = Soup.Message.new("GET", "http://localhost:8081/v2/languages")
        self._session.send_and_read_async(
            msg=message,
            io_priority=GObject.PRIORITY_LOW,
            cancellable=None,
            callback=self._handle_languages_reply,
            user_data=callback
        )

    def _handle_languages_reply(self, session, result, callback):
        try:
            message = session.send_and_read_finish(result)
            languages = json.loads(message.get_data().decode())
            callback(languages)
        except GLib.GError:
            logger.error("Error fetching languages")
            callback(None)

    def check(self, text: str, language: str, callback):
        """ Check a text. """

        # Return None if the server is not alive
        if not self.server_is_alive:
            return None

        encoded = Soup.form_encode_hash({
            "text": text,
            "language": language,
        })

        message = Soup.Message.new_from_encoded_form(
            method="POST",
            uri_string="http://localhost:8081/v2/check",
            encoded_form=encoded
        )

        self._session.send_and_read_async(
            msg=message,
            cancellable=None,
            io_priority=GObject.PRIORITY_LOW,
            callback=self._process_check_result,
            user_data=callback
        )

    def _process_check_result(self, session, result, callback):
        """Handle a response to a check request."""

        # Decode the response
        raw_data = session.send_and_read_finish(result)
        results = json.loads(raw_data.get_data().decode())

        # Prepare a list of annotations
        annotations = []
        for match in results['matches']:
            annotation = Annotation()

            # Set the message
            annotation.title = match["shortMessage"]
            if len(match["shortMessage"]) == 0:
                annotation.title = match["rule"]["category"]["name"]
            annotation.message = match["message"]

            # Set the boundaries
            annotation.offset = match["offset"]
            annotation.length = match["length"]

            # Set the category
            if match["type"]["typeName"] == "Hint":
                annotation.category = "hint"
            elif match["rule"]["issueType"] == "style":
                annotation.category = "hint"
            elif match["type"]["typeName"] == "Other":
                annotation.category = "warning"
            elif match["rule"]["issueType"] == "inconsistency":
                annotation.category = "warning"
            else:
                annotation.category = "error"

            # Add the suggestions
            for replacement in match["replacements"]:
                annotation.suggestions.append(replacement["value"])

            # Append the annotation
            annotations.append(annotation)

        # Call back with the annotations
        callback(annotations)


