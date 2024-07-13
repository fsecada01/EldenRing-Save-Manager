"""This file contains the functions used by the manager. All functions
contained within this file are utility functions that should be repeatedly
utilized across the whole application."""

import datetime
import lzma
import os
import re
import shutil
import traceback
from tkinter import END, Button, Entry, Label, Listbox, Tk, Toplevel
from tkinter import filedialog as fd
from types import FunctionType

import requests

from src import hexedit
from src.config import config, gamedir
from src.consts import BASE_DIR, cr_save_ent, lb, root
from src.os_layer import (
    copy_file,
    copy_folder,
    delete_folder,
    force_close_process,
    open_folder_standard_explorer,
    save_dir,
    v_num,
)


def popup(
    text: str,
    root_element: Tk,
    command: FunctionType | str | None = None,
    functions: tuple[FunctionType] | None = None,
    buttons: bool = False,
    button_names: tuple[str, str] = ("Yes", "No"),
    b_width: tuple[int] = (6, 6),
    title: str = "Manager",
    parent_window: Tk | Toplevel | None = None,
):
    """
    A function to create a TKEditor popup window.
    text: Message to display on the popup window.
    command: Simply run the windows CMD command if you press yes.
    functions: Pass in external functions to be executed for yes/no
    Args:
        text: str
        root_element: Tk
        command: str | None = None
        functions:
        buttons:
        button_names: tuple[str] = ('Yes', 'No')
        b_width: tuple[int] = (6, 6)
        title: str = 'Manager'
        parent_window: Tk | None = None

    Returns:

    """

    def run_cmd():
        cmd_out = run_command(command)
        pop_up_win.destroy()
        if cmd_out[0] == "error":
            pop_up_win.destroy()

    def do_not_run():
        pop_up_win.destroy()

    def run_func(arg):
        arg()
        pop_up_win.destroy()

    if parent_window is None:
        parent_window = root_element
    pop_up_win = Toplevel(parent_window)
    pop_up_win.title(title)

    lab = Label(pop_up_win, text=text)
    lab.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
    # Places popup window at center of the root window
    x = parent_window.winfo_x()
    y = parent_window.winfo_y()
    pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))

    # Runs for simple windows CMD execution
    if functions is False and buttons is True:
        but_yes = Button(  # noqa
            pop_up_win,
            text=button_names[0],
            borderwidth=5,
            width=b_width[0],
            command=run_cmd,
        ).grid(row=1, column=0, padx=(10, 0), pady=(0, 10))
        but_no = Button(  # noqa
            pop_up_win,
            text=button_names[1],
            borderwidth=5,
            width=b_width[1],
            command=do_not_run,
        ).grid(row=1, column=1, padx=(10, 10), pady=(0, 10))

    elif functions is not False and buttons is True:
        but_yes = Button(  # noqa
            pop_up_win,
            text=button_names[0],
            borderwidth=5,
            width=b_width[0],
            command=lambda: run_func(functions[0]),
        ).grid(row=1, column=0, padx=(10, 0), pady=(0, 10))
        but_no = Button(  # noqa
            pop_up_win,
            text=button_names[1],
            borderwidth=5,
            width=b_width[1],
            command=lambda: run_func(functions[1]),
        ).grid(row=1, column=1, padx=(10, 10), pady=(0, 10))
    # if text is the only argument passed in, it will simply be a popup
    # window to display text


def archive_file(file, name, metadata, names):
    # return
    try:
        name = name.replace(" ", "_")

        if not os.path.exists(
            file
        ):  # If you try to load a save from listbox, and it tries to archive
            # the file already present in the gamedir, but it doesn't exist,
            # then skip
            return

        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d__(%I.%M.%S)")
        name = f"{name}__{date}"
        os.makedirs(f"./data/archive/{name}")

        with (
            open(file, "rb") as fhi,
            lzma.open(f"./data/archive/{name}/ER0000.xz", "w") as fho,
        ):
            fho.write(fhi.read())
            names = [i for i in names if i is not None]
            formatted_names = ", ".join(names)
            meta = f"{metadata}\nCHARACTERS:\n {formatted_names}"

        meta_ls = [i for i in meta]
        try:
            _ = meta.encode(
                "ascii"
            )  # Will fail with UnicodeEncodeError if special characters exist
            with open(f"./data/archive/{name}/info.txt", "w") as f:
                f.write(meta)
        except Exception:
            traceback.print_exc()
            for ind, i in enumerate(meta):
                try:
                    _ = i.encode("ascii")
                    meta_ls[ind] = i
                except Exception:
                    meta_ls[ind] = "?"
            fixed_meta = ""
            for i in meta_ls:
                fixed_meta = fixed_meta + i

            with open(f"./data/archive/{name}/info.txt", "w") as f:
                f.write(fixed_meta)

    except Exception:
        traceback.print_exc()
        str_err = "".join(traceback.format_exc())
        popup(str_err)
        return


def unarchive_file(file):
    lzma.LZMACompressor()
    name = file.split("/")[-2]
    path = f"./data/recovered/{name}/"

    if not os.path.exists("./data/recovered/"):
        os.makedirs("./data/recovered/")
    if not os.path.exists(path):
        os.makedirs(path)

    with lzma.open(file, "rb") as f_in, open(f"{path}/{ext()}", "wb") as f_out:
        f_out.write(f_in.read())


def grab_metadata(file):
    """Used to grab metadata from archive info.txt"""
    with open(file.replace(" ", "__").replace(":", "."), "r") as f:
        meta = f.read()
        popup(meta.replace(",", "\n"))


def get_char_names_from_file(file_name: str):
    """wrapper for hexedit.get_names"""

    out = hexedit.get_names(file_name)
    if out is False:
        popup(
            f"Error: Unable to get character names.\nDoes the following path "
            f"exist?\n{file_name}"
        )
    else:
        return out


def finish_update(root_element: Tk):
    if os.path.exists(
        "./data/GameSaveDir.txt"
    ):  # Legacy file for pre v1.5 versions
        os.remove("./data/GameSaveDir.txt")

    if (
        config.post_update
    ):  # Will be run on first launch after running update.exe

        if not os.path.exists(
            "../data/save-files-pre-V1.5-BACKUP"
        ):  # NONE OF THIS WILL BE RUN ON v1.5+
            try:
                copy_folder(save_dir, "./data/save-files-pre-V1.5-BACKUP")
            except Exception:
                traceback.print_exc()
                str_err = "".join(traceback.format_exc())
                popup(str_err, root_element=root_element)

            for directory in os.listdir(
                save_dir
            ):  # Reconstruct save-file structure for pre v1.5 versions

                try:
                    id_str = re.findall(
                        r"\d{17}", str(os.listdir(f"{save_dir}{directory}/"))
                    )
                    if len(id_str) < 1:
                        continue

                    shutil.move(
                        f"{save_dir}{directory}/{id_str[0]}/{ext()}",
                        f"{save_dir}{directory}/{ext()}",
                    )
                    for i in [
                        "GraphicsConfig.xml",
                        "notes.txt",
                        "steam_autocloud.vdf",
                    ]:
                        if os.path.exists(f"{save_dir}{directory}/{i}"):
                            os.remove(f"{save_dir}{directory}/{i}")

                    delete_folder(f"{save_dir}{directory}/{id_str[0]}")
                except Exception:
                    traceback.print_exc()
                    str_err = "".join(traceback.format_exc())
                    popup(str_err, root_element=root_element)
                    continue


def ext():
    if config.cfg["seamless-coop"]:
        return "ER0000.co2"
    elif config.cfg["seamless-coop"] is False:
        return "ER0000.sl2"


def open_game_save_dir():
    if config.cfg["gamedir"] == "":
        popup("Please set your default game save directory first")
        return
    else:
        print(config.cfg["gamedir"])
        open_folder_standard_explorer(config.cfg["gamedir"])
        return


def open_folder():
    """Right-click open file location in listbox"""
    if len(lb.curselection()) < 1:
        popup("No listbox item selected.")
        return
    name = fetch_listbox_entry(lb)[0]

    def command():
        return open_folder_standard_explorer(
            f'{save_dir}{name.replace(" ", "-")}'
        )

    run_command(command)


def update_app(on_start=False):
    """Gets redirect URL of latest release, then pulls the version number
    from URL and makes a comparison"""

    try:
        version_url = (
            "https://github.com/Ariescyn/EldenRing-Save-Manager/releases/latest"
        )
        r = requests.get(version_url)  # Get redirect url
        ver = float(r.url.split("/")[-1].split("v")[1])
    except Exception:
        popup("Can not check for updates. Check your internet connection.")
        return
    if ver > v_num:
        popup(
            text=f" Release v{str(ver)} Available\nClose the program and run "
            f"the Updater.",
            buttons=True,
            functions=(root.quit, do_nothing),
            button_names=("Exit Now", "Cancel"),
        )

    if on_start is True:
        return
    else:
        popup("Current version up to date")
        return


def help_me():
    # out = run_command("notepad ./data/readme.txt")
    info = ""
    with open("../data/readme.txt", "r") as f:
        dat = f.readlines()
        for line in dat:
            info = info + line
    popup(info)


def load_listbox(listbox: Listbox):
    """LOAD current save files and insert them into listbox. This is Used to
    load the listbox on startup and also after deleting an item from the
    listbox to refresh the entries.
    """
    if os.path.isdir(save_dir) is True:
        for entry in os.listdir(save_dir):
            listbox.insert(END, "  " + entry.replace("-", " "))
            listbox.select_set(0)


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
        popup(text="Forbidden character used", root_element=root)

    if os.path.isdir(save_dir) is False:
        # subprocess.run("md .\\save-files", shell=True)
        cmd_out = run_command(lambda: os.makedirs(save_dir))
        if cmd_out[0] == "error":
            return

    # If new save name doesn't exist, insert it into the listbox, otherwise
    # duplicates will appear in listbox even though the copy command will
    # overwrite original save
    if len(name) > 0 and is_forbidden is False:

        path = f"{config.cfg["gamedir"]}/{ext()}"
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


def do_nothing():
    pass


def load_save_from_lb():
    """Fetches currently selected listbox item and copies files to game save
    dir."""

    if len(config.cfg["gamedir"]) < 2:
        popup("Set your Default Game Directory first")
        return

    def wrapper(command: FunctionType):
        """Archives savefile in game directory and runs command to overwrite.
        This function is then passed into popup function."""
        # path = f"{gamedir}/{user_steam_id}/ER0000.sl2"
        path = f"{config.cfg['gamedir']}/{ext()}"
        if not os.path.exists(path):
            run_command(command)
        else:
            nms = get_char_names_from_file(file_name=path)
            archive_file(
                path,
                "Loaded Save",
                "ACTION: Loaded save and overwrite current save file in "
                "EldenRing game directory",
                nms,
            )
            run_command(command)

    if len(lb.curselection()) < 1:
        popup("No listbox item selected.")
        return
    name = fetch_listbox_entry(lb)[0]
    src_dir = "".join((save_dir, name.replace(" ", "-"), "/"))

    if not os.path.isdir(f"{save_dir}{name}"):
        popup(
            "Save slot does not exist.\nDid you move or delete it from "
            "data/save-files?",
            root_element=root,
        )
        lb.delete(0, END)
        load_listbox(lb)
        return

    def command_func():
        return wrapper(copy_folder(src_dir, gamedir))

    popup(
        "Are you sure?",
        buttons=True,
        functions=(command_func, do_nothing),  # noqa
        root_element=root,
    )


def run_command(subprocess_command, optional_success_out="OK"):
    """Used throughout to run commands into subprocess and capture the
    output. Note that it is integrated with popup function for in-app error
    reporting."""
    try:
        subprocess_command()
    except Exception:
        traceback.print_exc()
        str_err = "".join(traceback.format_exc())
        popup(str_err, root_element=root)
        return "error", str_err
    return "Successfully completed operation", optional_success_out


def delete_save():
    """Removes entire directory in save-files dir"""
    name = fetch_listbox_entry(lb)[0]

    def yes():
        def command():
            return delete_folder(f"{save_dir}{name}")

        path = f"{save_dir}{name}/{ext()}"
        chars = get_char_names_from_file(file_name=path)
        archive_file(path, name, "ACTION: Delete save file in Manager", chars)
        run_command(command)
        lb.delete(0, END)
        load_listbox(lb)

    def no():
        return

    popup(
        f"Delete {fetch_listbox_entry(lb)[1]}?",
        root_element=root,
        functions=(yes, no),
        buttons=True,
    )


def fetch_listbox_entry(list_box):
    """Returns currently selected listbox entry.
    internal name is for use with save directories and within this script.
    Name is used for display within the listbox"""

    name = ""
    for i in list_box.curselection():
        name = name + list_box.get(i)
    internal_name = name.strip().replace(" ", "-")
    return internal_name, name


def rename_slot():
    """Renames the name in save file listbox"""

    def cancel():
        pop_up_win.destroy()

    def done():
        new_name = ent.get()
        if len(new_name) < 1:
            popup("No name entered.")
            return
        is_forbidden = False
        for char in new_name:
            if char in r"~'{};:./\,:*?<>|-!@#$%^&()+":
                is_forbidden = True
        if is_forbidden is True:
            popup("Forbidden character used")
            return
        elif is_forbidden is False:
            entries = []
            for entry in os.listdir(save_dir):
                entries.append(entry)
            if new_name in entries:
                popup("Name already exists")
                return

            else:
                new_file_name = new_name.replace(" ", "-")

                def command():
                    return os.rename(
                        f"{save_dir}{lst_box_choice}",
                        f"{save_dir}{new_file_name}",
                    )

                run_command(command)
                lb.delete(0, END)
                load_listbox(lb)
                pop_up_win.destroy()

    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.")
        return

    pop_up_win = Toplevel(root)
    pop_up_win.title("Rename")
    # pop_up_win.geometry("200x70")
    lab = Label(pop_up_win, text="Enter new Name:")
    lab.grid(row=0, column=0)
    ent = Entry(pop_up_win, borderwidth=5)
    ent.grid(row=1, column=0, padx=25, pady=10)
    x = root.winfo_x()
    y = root.winfo_y()
    pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))
    but_done = Button(
        pop_up_win, text="Done", borderwidth=5, width=6, command=done
    )
    but_done.grid(row=2, column=0, padx=(25, 65), pady=(0, 15), sticky="w")
    but_cancel = Button(
        pop_up_win, text="Cancel", borderwidth=5, width=6, command=cancel
    )
    but_cancel.grid(row=2, column=0, padx=(70, 0), pady=(0, 15))


def update_slot():
    """Update the selected savefile with the current elden ring savedata"""

    def do(file):
        names = get_char_names_from_file(file)
        archive_file(
            file,
            lst_box_choice,
            "ACTION: Clicked Update save-file in Manager",
            names,
        )

        copy_file(
            f"{config.cfg['gamedir']}/{ext()}", f"{save_dir}{lst_box_choice}"
        )

    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.")
        return
    path = f"{save_dir}{lst_box_choice}/{ext()}"

    popup(
        text="This will take your current save in-game\nand overwrite this "
        "save slot\nAre you sure?",
        buttons=True,
        command=lambda: do(path),
    )


def change_default_dir():
    """Opens file explorer for user to choose new default elden ring
    directory. Writes changes to GameSaveDir.txt"""

    newdir = fd.askdirectory()
    if len(newdir) < 1:  # User presses cancel
        return

    folder = newdir.split("/")[-1]
    f_id = re.findall(r"\d{17}", folder)

    if len(f_id) == 0:
        popup("Please select the directory named after your 17 digit SteamID")
        return

    else:

        config.set("gamedir", newdir)

        popup(f"Directory set to:\n {newdir}\n")


def rename_char(file, nw_nm, dest_slot):
    """Wrapper for hexedit.change_name for error handling"""
    try:
        x = hexedit.change_name(file, nw_nm, dest_slot)
        if x == "error":
            raise Exception
    except Exception:
        popup(
            "Error renaming character. This may happen\nwith short names like "
            "'4'."
        )
        raise


def changelog(run=False):
    info = ""
    change_log = BASE_DIR / "data" / "changelog.txt"
    with change_log.open() as f:
        dat = f.readlines()
        for line in dat:
            info = info + f"\n\u2022 {line}\n"
    if run:
        popup(info, title="Changelog", root_element=root)
        return
    if config.post_update:
        popup(info, title="Changelog", root_element=root)


def force_quit():
    comm = force_close_process("eldenring.exe")
    popup(text="Are you sure?", buttons=True, command=comm, root_element=root)


def create_notes(name: str, dir_name: str):
    """Create a notepad document in specified save slot."""

    name = name.replace(" ", "-")

    def command():
        return os.close(os.open(f"{dir_name}/{name}.txt", os.O_CREAT))

    run_command(command)
