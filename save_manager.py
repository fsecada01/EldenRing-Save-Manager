import json
import re
import webbrowser
from tkinter import *
from tkinter import font as FNT

from PIL import Image, ImageTk

from src import itemdata
from src.consts import config, cr_save_ent, lb, root
from src.menu import (
    change_default_steamid_menu,
    char_manager_menu,
    god_mode_menu,
    import_save_menu,
    inventory_editor_menu,
    recovery_menu,
    rename_characters_menu,
    seamless_coop_menu,
    set_runes_menu,
    set_steam_id_menu,
    stat_editor_menu,
)
from src.os_layer import *
from src.utils import (
    archive_file,
    change_default_dir,
    changelog,
    create_save,
    delete_save,
    ext,
    fetch_listbox_entry,
    finish_update,
    force_quit,
    get_char_names_from_file,
    load_listbox,
    load_save_from_lb,
    open_folder,
    open_game_save_dir,
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


class Config:

    def __init__(self):
        if not os.path.exists(post_update_file):
            with open(post_update_file, "w") as ff:
                ff.write("True")

        with open(post_update_file, "r") as f:
            x = f.read()
            self.post_update = True if x == "True" else False

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                dat = json.load(f)

                if (
                    "custom_ids" not in dat.keys()
                ):  # custom_ids was an addition to v1.5, must create for
                    # current users with existing config.json from v1.5
                    dat["custom_ids"] = {}
                    self.cfg = dat

                    with open(config_path, "w") as f:
                        json.dump(self.cfg, f)

        if not os.path.exists(config_path):  # Build dictionary for first time
            dat = {
                "post_update": True,
                "gamedir": "",
                "steamid": "",
                "seamless-coop": False,
                "custom_ids": {},
            }

            self.cfg = dat
            with open(config_path, "w") as f:
                json.dump(self.cfg, f)
        else:
            with open(config_path, "r") as f:
                js = json.load(f)
                self.cfg = js

    def set_update(self, val):
        self.post_update = val
        with open(post_update_file, "w") as f:
            f.write("True" if val else "False")

    def set(self, k, v):
        self.cfg[k] = v
        with open(config_path, "w") as f:
            json.dump(self.cfg, f)

    def add_to(self, k, v):
        self.cfg[k].update(v)
        with open(config_path, "w") as f:
            json.dump(self.cfg, f)

    def delete_custom_id(self, k):
        self.cfg["custom_ids"].pop(k)
        with open(config_path, "w") as f:
            json.dump(self.cfg, f)


# ////// MENUS //////


# //// LEGACY FUNCTIONS (NO LONGER USED) ////


def quick_restore(user_steam_id=None):
    """Copies the selected save file in temp to selected listbox item"""
    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.")
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
        popup("Successfully restored backup.")


def quick_backup():
    """Creates a backup of selected listbox item to temp folder"""
    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.")
        return

    src = f"{save_dir}{lst_box_choice}"
    dest = f"./data/temp/{lst_box_choice}"
    x = run_command(lambda: copy_folder(src, dest))
    if x[0] != "error":
        popup("Successfully created backup.")


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
        popup("Backup saved successfully")


def load_backup():
    """Quickly load a backup of the current game save. Used from the menubar."""
    comm = copy_folder(backupdir, gamedir)
    if os.path.isdir(backupdir) is False:
        run_command(lambda: os.makedirs(backupdir))

    if len(re.findall(r"\d{17}", str(os.listdir(backupdir)))) < 1:
        popup("No backup found")

    else:
        popup("Overwrite existing save?", command=comm, buttons=True)


def about():
    popup(
        text="Author: Lance Fitz\nEmail: scyntacks94@gmail.com\nGithub: "
        "github.com/Ariescyn"
    )


def open_notes():
    name = fetch_listbox_entry(lb)[0]
    if len(name) < 1:
        popup("No listbox item selected.")
        return

    def command():
        return open_textfile_in_editor(f"{save_dir}{name}/notes.txt")

    run_command(command)


# ///// MAIN GUI CONTENT /////


root.resizable(width=False, height=False)
root.title("{} {}".format(app_title, version))

root.geometry("830x561")
try:
    root.iconbitmap(icon_file)
except Exception:
    print("Unix doesn't support .ico - setting the background as app icon")
    root.iconphoto(True, PhotoImage(background_img))

# FANCY STUFF
bg_img = ImageTk.PhotoImage(image=Image.open(background_img))
background = Label(root, image=bg_img)

background.place(x=bk_p[0], y=bk_p[1], relwidth=1, relheight=1)

# Images used on button widgets
done_img = ImageTk.PhotoImage(
    image=Image.open("./data/assets/but_done.png").resize((50, 30))
)
load_save_img = ImageTk.PhotoImage(
    image=Image.open("./data/assets/but_load_save.png").resize((85, 40))
)
delete_save_img = ImageTk.PhotoImage(
    image=Image.open("./data/assets/but_delete_save.png").resize((85, 40))
)

menubar = Menu(root)
root.config(menu=menubar)

# FILE MENU
filemenu = Menu(menubar, tearoff=0)
# filemenu.add_command(label="Save Backup", command=save_backup)
# filemenu.add_command(label="Restore Backup", command=load_backup)
filemenu.add_command(label="Import Save File", command=import_save_menu)
filemenu.add_command(label="seamless Co-op Mode", command=seamless_coop_menu)
filemenu.add_command(label="Force quit EldenRing", command=force_quit)
filemenu.add_command(
    label="Open Default Game Save Directory", command=open_game_save_dir
)
filemenu.add_separator()
filemenu.add_command(
    label="Donate",
    command=lambda: webbrowser.open_new_tab(
        "https://www.paypal.com/donate/?hosted_button_id=H2X24U55NUJJW"
    ),
)
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

# EDIT MENU
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(
    label="Change Default Directory", command=change_default_dir
)
# editmenu.add_command(label="Reset To Default Directory", command=reset_default_dir)
editmenu.add_command(
    label="Change Default SteamID", command=change_default_steamid_menu
)
editmenu.add_command(label="Check for updates", command=update_app)
menubar.add_cascade(label="Edit", menu=editmenu)

# TOOLS MENU
toolsmenu = Menu(menubar, tearoff=0)
toolsmenu.add_command(label="Character Manager", command=char_manager_menu)
toolsmenu.add_command(label="Stat Editor", command=stat_editor_menu)
toolsmenu.add_command(label="Inventory Editor", command=inventory_editor_menu)
toolsmenu.add_command(label="File Recovery", command=recovery_menu)
menubar.add_cascade(label="Tools", menu=toolsmenu)

# CHEAT MENU
cheatmenu = Menu(menubar, tearoff=0)
cheatmenu.add_command(label="God Mode", command=god_mode_menu)
cheatmenu.add_command(label="Set Runes", command=set_runes_menu)
menubar.add_cascade(label="Cheats", menu=cheatmenu)

# HELP MENU
helpmenu = Menu(menubar, tearoff=0)
# helpmenu.add_command(label="Readme", command=help_me)
# helpmenu.add_command(label="About", command=about)
helpmenu.add_command(
    label="Watch Video", command=lambda: webbrowser.open_new_tab(video_url)
)
helpmenu.add_command(label="Changelog", command=lambda: changelog(run=True))
helpmenu.add_command(
    label="Report Bug",
    command=lambda: popup(
        "Report bugs on Nexus, GitHub or email me at scyntacks94@gmail.com"
    ),
)
menubar.add_cascade(label="Help", menu=helpmenu)

create_save_lab = Label(root, text="Create Save:", font=("Impact", 15))
create_save_lab.config(fg="grey")
create_save_lab.grid(row=0, column=0, padx=(80, 10), pady=(0, 260))

cr_save_ent.grid(row=0, column=1, pady=(0, 260))

but_go = Button(
    root, text="Done", image=done_img, borderwidth=0, command=create_save
)
but_go.grid(row=0, column=2, padx=(10, 0), pady=(0, 260))

bolded = FNT.Font(weight="bold")  # will use the default font
lb.config(font=bolded)
lb.grid(row=0, column=3, padx=(110, 0), pady=(30, 0))


# -----------------------------------------------------------
# right click popup menu in listbox


def do_popup(event):
    try:
        rt_click_menu.tk_popup(
            event.x_root, event.y_root
        )  # Grab x,y position of mouse cursor
    finally:
        rt_click_menu.grab_release()


rt_click_menu = Menu(lb, tearoff=0)
# rt_click_menu.add_command(label="Edit Notes", command=open_notes)
rt_click_menu.add_command(label="Rename Save", command=rename_slot)
rt_click_menu.add_command(
    label="Rename Characters", command=rename_characters_menu
)
rt_click_menu.add_command(label="Update", command=update_slot)
# rt_click_menu.add_command(label="Quick Backup", command=quick_backup)
# rt_click_menu.add_command(label="Quick Restore", command=quick_restore)
# rt_click_menu.add_command(label="Set Starting Classes",
# command=set_starting_class_menu) #FULLY FUNCTIONAL, but it doesn't work
# because game restores playtime to original values after loading..... :(
rt_click_menu.add_command(label="Change SteamID", command=set_steam_id_menu)
rt_click_menu.add_command(label="Open File Location", command=open_folder)
lb.bind(
    "<Button-3>", do_popup
)  # button 3 is right click, so when right-clicking inside listbox, do_popup
# is executed at cursor position

load_listbox(lb)  # populates listbox with saves on runtime

but_load_save = Button(
    root,
    text="Load Save",
    image=load_save_img,
    borderwidth=0,
    command=load_save_from_lb,
)
but_delete_save = Button(
    root,
    text="Delete Save",
    image=delete_save_img,
    borderwidth=0,
    command=delete_save,
)

but_load_save.grid(row=3, column=3, pady=(12, 0))
but_delete_save.grid(row=3, column=3, padx=(215, 0), pady=(12, 0))

# INITIALIZE APP
itemdb = itemdata.Items()
if not os.path.exists("./data/save-files"):
    os.makedirs("./data/save-files")

update_app(True)

if len(config.cfg["steamid"]) != 17:
    popup("SteamID not set. Click edit > Change default SteamID to set.")


if __name__ == "__main__":
    changelog()
    finish_update()
    config.set_update(False)
    root.mainloop()
