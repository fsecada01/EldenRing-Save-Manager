import os
import re

from save_manager import root
from src.config import gamedir
from src.os_layer import backupdir, copy_folder
from src.utils import popup, run_command


def load_backup():
    """Quickly load a backup of the current game save. Used from the menubar."""
    comm = copy_folder(backupdir, gamedir)
    if os.path.isdir(backupdir) is False:
        run_command(lambda: os.makedirs(backupdir))

    if len(re.findall(r"\d{17}", str(os.listdir(backupdir)))) < 1:
        popup("No backup found", root_element=root)

    else:
        popup(
            "Overwrite existing save?",
            command=comm,
            buttons=True,
            root_element=root,
        )
