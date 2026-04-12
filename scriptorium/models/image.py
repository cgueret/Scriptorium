import logging
from gi.repository import GObject, Gio, Gdk
from .resource import Resource
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


class Image(Resource):

    __gtype_name__ = "Image"

    file_name = GObject.Property(type=str)

    def __init__(self, project, identifier: str):
        """Create an image instance."""
        super().__init__(project, identifier)

        # Base directory for all the images
        self.base_directory = project.base_directory / Path("images")
        if not self.base_directory.exists():
            self.base_directory.mkdir()

        self._texture = None

    @property
    def data_files(self):
        """Return the file path for the image if it has been set."""
        if self.file_name is not None and self.file_name != '':
            return [
                Path("images") / Path(self.file_name)
            ]
        else:
            return []

    @property
    def path(self):
        if len(self.data_files) > 0:
            return self.project.base_directory / self.data_files[0]
        return None

    @property
    def width(self):
        return self.texture.get_width()

    @property
    def height(self):
        return self.texture.get_height()

    def set_content_from_path(self, file_path: Path):
        """Set the content of the image from the file path indicated."""

        # Define the target file name
        file_extensions = ''.join(file_path.suffixes)
        self.file_name = self.identifier + file_extensions

        # Copy the content of the file
        target_path = self.base_directory / Path(self.file_name)
        shutil.copyfile(file_path, target_path)

        # Commit the change in content
        self.project.save_resource(self)

    @property
    def texture(self) -> Gdk.Texture:
        """A texture associated with the image."""
        # If texture does not exist load the image
        if self._texture is None:
            if len(self.data_files) > 0:
                self._texture = Gdk.Texture.new_from_file(
                    Gio.File.new_for_path(str(self.path).encode())
                )

        # Return the texture
        return self._texture


