from tkinter import Button, Label, Menu, PhotoImage, Tk
from tkinter import font as font_style

from src import itemdata
from src.app.consts import cr_save_ent, create_save, lb
from src.app.views import root
from src.app.views.menus.main import rt_click_menu
from src.config import config, gamedir
from src.menu import rename_characters_menu, set_steam_id_menu
from src.os_layer import (
    backupdir,
    copy_folder,
    done_img,
    is_windows,
    open_textfile_in_editor,
    os,
    save_dir,
)
from src.utils import (
    archive_file,
    changelog,
    delete_save,
    ext,
    fetch_listbox_entry,
    finish_update,
    get_char_names_from_file,
    load_listbox,
    load_save_from_lb,
    open_folder,
    popup,
    rename_slot,
    run_command,
    update_app,
    update_slot,
)

# Collapse all functions to navigate. In Atom editor: "Edit > Folding > Fold
# All"


# set always the working dir to the correct folder for unix env
if not is_windows:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


def do_popup(event):
    try:
        rt_click_menu.tk_popup(
            event.x_root, event.y_root
        )  # Grab x,y position of mouse cursor
    finally:
        rt_click_menu.grab_release()


# //// LEGACY FUNCTIONS (NO LONGER USED) ////


def quick_restore(user_steam_id=None):
    """Copies the selected save file in temp to selected listbox item"""
    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.", root_element=root)
        return
    src = f"./data/temp/{lst_box_choice}"
    dest = f"{save_dir}{lst_box_choice}"
    file = f"{dest}/{user_steam_id}/{ext()}"  # USER_STEAM_ID no longer used
    archive_file(
        file,
        lst_box_choice,
        "ACTION: Quick Restore",
        get_char_names_from_file(file_name=file),
    )
    x = run_command(lambda: copy_folder(src, dest))
    if x[0] != "error":
        popup("Successfully restored backup.", root_element=root)


def quick_backup():
    """Creates a backup of selected listbox item to temp folder"""
    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.", root_element=root)
        return

    src = f"{save_dir}{lst_box_choice}"
    dest = f"./data/temp/{lst_box_choice}"
    x = run_command(lambda: copy_folder(src, dest))
    if x[0] != "error":
        popup("Successfully created backup.", root_element=root)


def save_backup():
    """Quickly save a backup of the current game save. Used from the menubar."""
    comm = copy_folder(gamedir, backupdir)

    if os.path.isdir(backupdir) is False:
        cmd_out1 = run_command(lambda: os.makedirs(backupdir))
        if cmd_out1[0] == "error":
            return
    cmd_out2 = run_command(comm)
    if cmd_out2[0] == "error":
        return
    else:
        popup("Backup saved successfully", root_element=root)


def about():
    popup(
        text="Author: Lance Fitz\nEmail: scyntacks94@gmail.com\nGithub: "
        "github.com/Ariescyn",
        root_element=root,
    )


def open_notes():
    name = fetch_listbox_entry(lb)[0]
    if len(name) < 1:
        popup("No listbox item selected.", root_element=root)
        return

    def command():
        return open_textfile_in_editor(f"{save_dir}{name}/notes.txt")

    run_command(command)


# ///// MAIN GUI CONTENT /////


def initialize_main_gui(done_img: PhotoImage, root_element: Tk = root) -> Tk:
    """
    Creates the main GUI window and its contents. This is intended to be
    called by the main function and completes initialization at call time.
    This is wrapped in a function for sanity purposes.

    Args:
        done_img:
        root_element: Tk

    Returns: Tk

    """

    lb.bind("<Button-3", func=do_popup)
    load_listbox(listbox=lb)

    # -----------------------------------------------------------

    create_save_label(done_img, root_element)

    bolded = font_style.Font(weight="bold")  # will use the default font
    lb.config(font=bolded)
    lb.grid(row=0, column=3, padx=(110, 0), pady=(30, 0))

    # -----------------------------------------------------------
    # right click popup menu in listbox
    lb.bind(
        "<Button-3>", do_popup
    )  # button 3 is right click, so when right-clicking inside listbox,
    # do_popup
    # is executed at cursor position
    load_listbox(lb)  # populates listbox with saves on runtime
    but_load_save = Button(
        root_element,
        text="Load Save",
        image=load_save_img,  # noqa
        borderwidth=0,
        command=lambda: load_save_from_lb(list_box=lb),
    )
    but_delete_save = Button(
        root_element,
        text="Delete Save",
        image=delete_save_img,  # noqa
        borderwidth=0,
        command=lambda: delete_save(list_box=lb),
    )
    but_load_save.grid(row=3, column=3, pady=(12, 0))
    but_delete_save.grid(row=3, column=3, padx=(215, 0), pady=(12, 0))

    return root_element


def get_right_click_menu():
    rt_click_menu = Menu(lb, tearoff=0)
    # rt_click_menu.add_command(label="Edit Notes", command=open_notes)
    rt_click_menu.add_command(
        label="Rename Save", command=lambda: rename_slot(list_box=lb)
    )
    rt_click_menu.add_command(
        label="Rename Characters", command=rename_characters_menu
    )
    rt_click_menu.add_command(
        label="Update",
        command=lambda: update_slot(list_box=lb, root_element=root),
    )
    # rt_click_menu.add_command(label="Quick Backup", command=quick_backup)
    # rt_click_menu.add_command(label="Quick Restore", command=quick_restore)
    # rt_click_menu.add_command(label="Set Starting Classes",
    # command=set_starting_class_menu) #FULLY FUNCTIONAL, but it doesn't work
    # because game restores playtime to original values after loading..... :(
    rt_click_menu.add_command(label="Change SteamID", command=set_steam_id_menu)
    rt_click_menu.add_command(
        label="Open File Location",
        command=lambda: open_folder(list_box=lb, root_element=root),
    )

    return rt_click_menu


def create_save_label(done_img: PhotoImage, root_element: Tk):
    create_save_lab = Label(
        root_element, text="Create Save:", font=("Impact", 15)
    )
    create_save_lab.config(fg="grey")
    create_save_lab.grid(row=0, column=0, padx=(80, 10), pady=(0, 260))
    cr_save_ent.grid(row=0, column=1, pady=(0, 260))
    but_go = Button(
        root_element,
        text="Done",
        image=done_img,  # noqa
        borderwidth=0,
        command=create_save,
    )
    but_go.grid(row=0, column=2, padx=(10, 0), pady=(0, 260))

    return root_element


root = initialize_main_gui(
    done_img=PhotoImage(name=done_img), root_element=root
)

# INITIALIZE APP
itemdb = itemdata.Items()
if not os.path.exists("./data/save-files"):
    os.makedirs("./data/save-files")

update_app(True)

if len(config.cfg["steamid"]) != 17:
    popup(
        "SteamID not set. Click edit > Change default SteamID to set.",
        root_element=root,
    )

if __name__ == "__main__":
    changelog()
    finish_update(root_element=root)
    config.set_update(False)
    root.mainloop()
