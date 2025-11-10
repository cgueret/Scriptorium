import os
import gettext
from .editor import ScrptEditorView
from .library import ScrptLibraryView

# Initialise gettext globally

if os.path.exists(os.path.join(os.path.dirname(__file__), "../po")):
    # Running from source tree (uninstalled)
    LOCALE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../po"))
else:
    # Installed system-wide
    LOCALE_DIR = os.path.join("/usr/share/locale")

gettext.bindtextdomain("scriptorium", LOCALE_DIR)
gettext.textdomain("scriptorium")
_ = gettext.gettext

__all__ = ["ScrptEditorView", "ScrptLibraryView"]
