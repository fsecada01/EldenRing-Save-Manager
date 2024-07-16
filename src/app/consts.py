import os
from tkinter import END, Entry, Listbox
from tkinter.ttk import Button

from src.app.views.root import root
from src.config import config
from src.os_layer import copy_file, save_dir
from src.utils import (
    archive_file,
    create_notes,
    do_nothing,
    ext,
    get_char_names_from_file,
    popup,
    run_command,
)

cr_save_ent = Entry(root, borderwidth=5)
lb = Listbox(root, borderwidth=3, width=25, height=16)

change_default_dir_button = Button(
    root, text="Change Default Directory", width=5, command=do_nothing
)


def create_save():
    """Takes user input from the created save entry box and copies files from
    game save dir to the save-files dir of app"""
    if len(config.cfg["gamedir"]) < 2:
        popup("Set your Default Game Directory first")
        return
    name = cr_save_ent.get().strip()
    new_dir = f"{save_dir}{name.replace(' ', '-')}"

    # Check the given name in the entry
    if len(name) < 1:
        popup("No name entered")

    is_forbidden = False
    for char in name:
        if char in r"~'{};:./\,:*?<>|-!@#$%^&()+":
            is_forbidden = True
    if is_forbidden is True:
        popup(text="Forbidden character.py used", root_element=root)

    if os.path.isdir(save_dir) is False:
        # subprocess.run("md .\\save-files", shell=True)
        cmd_out = run_command(lambda: os.makedirs(save_dir))
        if cmd_out[0] == "error":
            return

    # If new save name doesn't exist, insert it into the listbox, otherwise
    # duplicates will appear in listbox even though the copy command will
    # overwrite original save
    if len(name) > 0 and is_forbidden is False:
        path = f"{config.cfg['gamedir']}/{ext()}"
        nms = get_char_names_from_file(file_name=path)
        archive_file(path, name, "ACTION: Clicked Create Save", nms)

        def cp_to_saves_cmd():
            return copy_file(path, new_dir)

        # /E – Copy subdirectories, including any empty ones. /H - Copy files
        # with hidden and system file attributes. /C - Continue copying even
        # if an error occurs. /I - If in doubt, always assume the destination
        # is a folder. e.g. when the destination does not exist /Y -
        # Overwrite all without PROMPT (ex: yes no)
        if os.path.isdir(new_dir) is False:
            cmd_out = run_command(lambda: os.makedirs(new_dir))
            if cmd_out[0] == "error":
                return
            lb.insert(END, "  " + name)
            cmd_out = run_command(cp_to_saves_cmd)
            if cmd_out[0] == "error":
                return
            create_notes(name, new_dir)
        else:
            popup(
                "File already exists, OVERWRITE?",
                root_element=root,
                command=cp_to_saves_cmd,
                buttons=True,
            )
        # save_path = f"{new_dir}/{user_steam_id}/ER0000.sl2"
        # nms = get_char_names_from_file(save_path)
        # archive_file(save_path, f"ACTION: Create save\nCHARACTERS: {nms}")
