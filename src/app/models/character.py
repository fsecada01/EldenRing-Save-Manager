from src import hexedit
from src.app.models.base import ObservableModel
from src.utils import archive_file, unarchive_file


class Character(ObservableModel):
    def __init__(self, file: str):
        super().__init__()
        self.file = file
        self.id = ""
        self.archived = False

    def archive_file(self, file, name: str, metadata, names):
        archive_file(file=file, name=name, metadata=metadata, names=names)
        self.archived = True
        return

    def unarchive_file(self, file):
        unarchive_file(file)
        self.archived = False
        return

    def grab_meta_data(self, file: str | None = None):
        """
        Utility function that grabs metadata from a save file. If the class
        object does not have a file assigned, the file attribute will be set
        by the file arg. If no file arg is provided, then the object's
        attached file attribute will be used instead. Args: file: str

        Returns:
            meta: str
        """
        if not self.file and not file:
            return ""
        elif file and not self.file:
            self.file = file
        elif self.file and not file:
            file = self.file

        archive_file_name = file.replace(" ", "__").replace(":", ".")
        with open(archive_file_name, "r") as f:
            meta = f.read()

        return meta

    def get_char_names_from_file(self, file: str):
        """
        This function gets the character names from the associated save file.
        Args:
            file: str

        Returns:

        """
        if not self.file and not file:
            return ""
        elif file and not self.file:
            self.file = file
        elif self.file and not file:
            file = self.file
        contents = hexedit.get_names(file)

        return contents
