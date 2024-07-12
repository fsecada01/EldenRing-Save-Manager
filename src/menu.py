import os
import re
import shutil
import tkinter as TKIN
import webbrowser
from collections import Counter
from pathlib import Path as PATH
from tkinter import (
    DISABLED,
    END,
    Button,
    Entry,
    Label,
    Listbox,
    Menu,
    N,
    OptionMenu,
    S,
    Scrollbar,
    StringVar,
    Text,
    Toplevel,
    W,
)
from tkinter import filedialog as fd
from tkinter import font as FNT

from save_manager import bolded
from src import hexedit, itemdata
from src.consts import config, lb, root
from src.os_layer import (
    copy_file,
    custom_search_tutorial_url,
    delete_folder,
    save_dir,
    temp_dir,
    video_url,
)
from src.utils import (
    archive_file,
    create_notes,
    do_nothing,
    ext,
    fetch_listbox_entry,
    get_char_names_from_file,
    grab_metadata,
    load_listbox,
    popup,
    rename_char,
    run_command,
    unarchive_file,
)


def get_char_names(list_box, drop, v):
    """Populates dropdown menu containing the name of characters in a
    save file"""
    v.set("Character")
    name = fetch_listbox_entry(list_box)[0]
    if len(name) < 1:
        return
    file = f"{save_dir}{name}/{ext()}"
    names = get_char_names_from_file(file)

    if names is False:
        popup(
            root_element=root,
            text="FileNotFoundError: This is a known issue.\nPlease try "
            "re-importing your save file.",
        )

    drop["menu"].delete(0, "end")  # remove full list

    index = 1
    for ind, opt in enumerate(names):
        opt = f"{index}. {opt}" if opt else f"{ind + 1}. "
        opt = f"{index}. {opt}"
        drop["menu"].add_command(label=opt, command=TKIN._setit(v, opt))
        index += 1


def char_manager_menu():
    """Entire character manager window for copying characters between save
    files"""

    def readme():
        info = ""
        with open("../data/copy-readme.txt", "r") as f:
            dat = f.readlines()
            for line in dat:
                info = info + line
        popup(info)
        # run_command("notepad ./data/copy-readme.txt")

    def open_video():
        webbrowser.open_new_tab(video_url)

    def do_copy():
        def pop_up(txt, bold=True):
            """Basic popup window used only for parent function"""
            win = Toplevel(pop_up_win)
            win.title("Manager")
            lab = Label(win, text=txt)
            if bold is True:
                lab.config(font=bolded)
            lab.grid(row=0, column=0, padx=15, pady=15, columnspan=2)
            x = pop_up_win.winfo_x()
            y = pop_up_win.winfo_y()
            win.geometry("+%d+%d" % (x + 200, y + 200))

        src_char = vars1.get()  # "1. charname"
        dest_char = vars2.get()
        if src_char == "Character" or dest_char == "Character":
            pop_up("Select a character first")
            return

        if src_char.split(".")[1] == " " or dest_char.split(".")[1] == " ":
            pop_up(
                "Can't write to empty slot.\nGo in-game and create a "
                "character to overwrite."
            )
            return

        name1 = fetch_listbox_entry(lb1)[0]  # Save file name. EX: main
        name2 = fetch_listbox_entry(lb2)[0]

        if len(name1) < 1 or len(name2) < 1:
            pop_up(txt="Slot not selected")
            return
        if src_char == "Character" or dest_char == "Character":
            pop_up(txt="Character not selected")
            return

        src_file = f"{save_dir}{name1}/{ext()}"
        dest_file = f"{save_dir}{name2}/{ext()}"

        src_ind = int(src_char.split(".")[0])
        dest_ind = int(dest_char.split(".")[0])

        # Duplicate names check
        src_char_real = src_char.split(". ")[1]
        dest_names = get_char_names_from_file(dest_file)
        nms = [i for i in dest_names]  # For archive_file only
        src_names = get_char_names_from_file(src_file)

        # If there are two or more of the name in a destination file, quits
        rmv_none = [i for i in dest_names if i is not None]
        if max(Counter(rmv_none).values()) > 1:
            pop_up(
                """Sorry, Can't handle writing to a DESTINATION file with
                duplicate character names!\n\n You can work around this
                limitation by using the save file with duplicate character
                names as the SOURCE file:\n 1. Select the save file with
                duplicate character names as the SOURCE file.\n 2. Select a
                different save file as the DESTINATION (can be anything).\n
                3. Copy the first character with duplicate names to
                DESTINATION file\n 4. Rename the character in the DESTINATION
                file to something different.\n 5. Copy the second character
                with duplicate names to the DESTINATION file.\n\n Why do you
                have to do this? Because character names vary greatly in
                frequency and location\n within the save file, so this tool
                must replace ALL occurences of a given name.""",
                bold=False,
            )
            return

        src_names.pop(src_ind - 1)
        dest_names.pop(dest_ind - 1)
        backup_path = r"./data/temp/{}".format(ext())

        # If performing operations on the same file. Changes name to random,
        # copies character to specified slot, then rewrites the name and
        # re-populates the dropdown entries
        if src_file == dest_file:
            archive_file(dest_file, name2, "ACTION: Copy Character", nms)

            def command():
                return copy_file(src_file, backup_path)

            run_command(command)
            rand_name = hexedit.random_str()
            rename_char(
                backup_path, rand_name, src_ind
            )  # Change backup to random name
            hexedit.copy_save(backup_path, src_file, src_ind, dest_ind)
            rename_char(src_file, rand_name, dest_ind)
            get_char_names(lb1, dropdown1, vars1)
            get_char_names(lb2, dropdown2, vars2)
            vars1.set("Character")
            vars2.set("Character")
            pop_up(
                txt="Success!\nDuplicate names not supported\nGenerated a new "
                "random name",
                bold=False,
            )
            return

        # If source name in destination file, copies source file to temp
        # folder, changes the name of copied save to random, then copies
        # source character of copied file to destination save file,
        # and rewrites names on destination file
        elif src_char_real in dest_names:
            archive_file(dest_file, name2, "ACTION: Copy character", nms)

            def command():
                return copy_file(src_file, backup_path)

            run_command(command)
            rand_name = hexedit.random_str()
            rename_char(backup_path, rand_name, src_ind)

            hexedit.copy_save(backup_path, dest_file, src_ind, dest_ind)
            rename_char(dest_file, rand_name, dest_ind)

            get_char_names(lb1, dropdown1, vars1)
            get_char_names(lb2, dropdown2, vars2)
            vars1.set("Character")
            vars2.set("Character")
            pop_up(
                txt="Duplicate names not supported\nGenerated a new random name",
                bold=False,
            )
            return

        archive_file(dest_file, name2, "ACTION: Copy character", nms)
        hexedit.copy_save(src_file, dest_file, src_ind, dest_ind)
        rename_char(dest_file, src_char_real, dest_ind)

        get_char_names(lb1, dropdown1, vars1)
        get_char_names(lb2, dropdown2, vars2)

        vars1.set("Character")
        vars2.set("Character")

        pop_up(txt="Success!")

    def cancel():
        pop_up_win.destroy()

    # Main GUI content
    pop_up_win = Toplevel(root)
    pop_up_win.title("Character Manager")
    pop_up_win.resizable(width=True, height=True)
    pop_up_win.geometry("620x500")

    bolded = FNT.Font(weight="bold")  # will use the default font

    x = root.winfo_x()
    y = root.winfo_y()
    pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))

    menubar = Menu(pop_up_win)
    pop_up_win.config(
        menu=menubar
    )  # menu is a parameter that lets you set a menubar for any given window

    helpmen = Menu(menubar, tearoff=0)
    helpmen.add_command(label="Readme", command=readme)
    helpmen.add_command(label="Watch Video", command=open_video)
    menubar.add_cascade(label="Help", menu=helpmen)

    srclab = Label(pop_up_win, text="Source File")
    srclab.config(font=bolded)
    srclab.grid(row=0, column=0, padx=(70, 0), pady=(20, 0))

    lb1 = Listbox(
        pop_up_win, borderwidth=3, width=15, height=10, exportselection=0
    )
    lb1.config(font=bolded)
    lb1.grid(row=1, column=0, padx=(70, 0), pady=(0, 0))
    load_listbox(lb1)

    destlab = Label(pop_up_win, text="Destination File")
    destlab.config(font=bolded)
    destlab.grid(row=0, column=1, padx=(175, 0), pady=(20, 0))

    lb2 = Listbox(
        pop_up_win, borderwidth=3, width=15, height=10, exportselection=0
    )
    lb2.config(font=bolded)
    lb2.grid(row=1, column=1, padx=(175, 0), pady=(0, 0))
    load_listbox(lb2)

    opts = [""]
    opts2 = [""]
    vars1 = StringVar(pop_up_win)
    vars1.set("Character")

    vars2 = StringVar(pop_up_win)
    vars2.set("Character")

    dropdown1 = OptionMenu(pop_up_win, vars1, *opts)
    dropdown1.grid(row=4, column=0, padx=(70, 0), pady=(20, 0))

    dropdown2 = OptionMenu(pop_up_win, vars2, *opts2)
    dropdown2.grid(row=4, column=1, padx=(175, 0), pady=(20, 0))

    but_select1 = Button(
        pop_up_win,
        text="Select",
        command=lambda: get_char_names(lb1, dropdown1, vars1),
    )
    but_select1.grid(row=3, column=0, padx=(70, 0), pady=(10, 0))

    but_select2 = Button(
        pop_up_win,
        text="Select",
        command=lambda: get_char_names(lb2, dropdown2, vars2),
    )
    but_select2.grid(row=3, column=1, padx=(175, 0), pady=(10, 0))

    but_copy = Button(pop_up_win, text="Copy", command=do_copy)
    but_copy.config(font=bolded)
    but_copy.grid(row=5, column=1, padx=(175, 0), pady=(50, 0))

    but_cancel = Button(pop_up_win, text="Cancel", command=cancel)
    but_cancel.config(font=bolded)
    but_cancel.grid(row=5, column=0, padx=(70, 0), pady=(50, 0))

    # mainloop()


def rename_characters_menu():
    """Opens popup window and renames character of selected listbox item"""

    def do():
        choice = vars.get()
        choice_real = choice.split(". ")[1]
        slot_ind = int(choice.split(".")[0])
        new_name = name_ent.get()
        if len(new_name) > 16:
            popup("Name too long. Maximum of 16 characters")
            return
        if len(new_name) < 1:
            popup("Enter a name first")
            return
        if len(new_name) < 3:
            popup("Minimum 3 characters")
            return

        # Duplicate names check
        dest_names = [i for i in names]
        dest_names.pop(slot_ind - 1)

        if new_name in dest_names:
            popup("Save can not have duplicate names")
            return

        archive_file(path, choice_real, "ACTION: Rename Character", names)
        rename_char(path, new_name, slot_ind)
        popup("Successfully Renamed Character")
        drop["menu"].delete(0, "end")
        rwin.destroy()

    name = fetch_listbox_entry(lb)[0]
    if name == "":
        popup("No listbox item selected.")
        return
    path = f"{save_dir}{name}/{ext()}"
    names = get_char_names_from_file(path)
    if names is False:
        popup(
            "FileNotFoundError: This is a known issue.\nPlease try "
            "re-importing your save file."
        )

    chars = []
    for ind, i in enumerate(names):
        if i is not None:
            chars.append(f"{ind + 1}. {i}")

    rwin = Toplevel(root)
    rwin.title("Rename Character")
    rwin.resizable(width=True, height=True)
    rwin.geometry("300x200")

    FNT.Font(weight="bold")  # will use the default font
    x = root.winfo_x()
    y = root.winfo_y()
    rwin.geometry("+%d+%d" % (x + 200, y + 200))

    opts = chars
    vars = StringVar(rwin)
    vars.set("Character")

    info_lab = Label(
        rwin,
        text="Note: If you have more than one character\nwith the same name,"
        "\nthis will rename BOTH characters.\n\n",
    )
    info_lab.pack()

    drop = OptionMenu(rwin, vars, *opts)
    drop.pack()
    #    drop.grid(row=0, column=0, padx=(35, 0), pady=(10, 0))

    name_ent = Entry(rwin, borderwidth=5)
    name_ent.pack()
    #    name_ent.grid(row=1, column=0, padx=(35, 0), pady=(10, 0))

    but_go = Button(rwin, text="Rename", borderwidth=5, command=do)
    but_go.pack()


def stat_editor_menu():
    def recalc_lvl():
        # entries = [vig_ent, min_ent, end_ent, str_ent, dex_ent, int_ent,
        # fai_ent, arc_ent]
        lvl = 0
        try:
            for ent in entries:
                lvl += int(ent.get())
            lvl_var.set(f"Level: {lvl - 79}")
        except Exception:
            return

    def set_stats():
        stats = []
        try:
            for ent in entries:
                stats.append(int(ent.get()))
        except Exception as e:
            pop_up(f"Error: Make sure all fields are completed.\n{e}")
            return
        if sum(stats) - 79 < 5:
            pop_up("Character level too low.")
            return

        vig = stats[0]
        min_val = stats[1]
        env_val = stats[2]

        vars.get().split(". ")[1]
        char_slot = int(vars.get().split(".")[0])
        name = fetch_listbox_entry(lb1)[0]
        file = f"{save_dir}{name}/{ext()}"
        try:
            nms = get_char_names_from_file(file)
            archive_file(file, name, "ACTION: Edit stats", nms)
            hexedit.set_stats(file, char_slot, stats)
            hexedit.set_attributes(file, char_slot, [vig, min_val, env_val])
            pop_up("Success!")
        except Exception as e:
            pop_up(f"Something went wrong!: {e}", bold=False)
            return

    def pop_up(txt, bold=True):
        """Basic popup window used only for parent function"""
        win = Toplevel(pop_up_win)
        win.title("Manager")
        lab = Label(win, text=txt)
        if bold is True:
            lab.config(font=bolded)
        lab.grid(row=0, column=0, padx=15, pady=15, columnspan=2)
        x = pop_up_win.winfo_x()
        y = pop_up_win.winfo_y()
        win.geometry("+%d+%d" % (x + 200, y + 200))

    def validate(P):
        if len(P) == 0:
            return True
        elif len(P) < 3 and P.isdigit() and int(P) > 0:
            return True
        else:
            # Anything else, reject it
            return False

    def get_char_stats():
        char = vars.get()

        if char == "Character":
            pop_up("Select a Character first")
            return

        char = vars.get().split(". ")[1]
        char_slot = int(vars.get().split(".")[0])
        name = fetch_listbox_entry(lb1)[0]
        file = f"{save_dir}{name}/{ext()}"

        try:
            stats = hexedit.get_stats(file, char_slot)[0]
        except Exception:
            # pop_up("Can't get stats, go in-game and\nload into the
            # character first or try leveling up once.")
            popup(
                "Unable to aquire stats/level.\nYour character level may be "
                "incorrect.\nFix now?",
                functions=(
                    lambda: fix_stats_menu(file, char_slot),
                    lambda: pop_up_win.destroy(),
                ),
                buttons=True,
                button_names=("Yes", "No"),
                parent_window=pop_up_win,
            )
            return

        # entries = [vig_ent, min_ent, end_ent, str_ent, dex_ent, int_ent,
        # fai_ent, arc_ent]
        if 0 in stats:
            pop_up(
                "Can't get stats, go in-game and\nload into the character "
                "first or try leveling up once."
            )
            return

        for stat, entry in list(zip(stats, entries)):
            entry.delete(0, END)
            entry.insert(1, stat)
        lvl = sum(stats) - 79
        lvl_var.set(f"Level: {lvl}")

    # Main GUI content STAT
    pop_up_win = Toplevel(root)
    pop_up_win.title("Stat Editor")
    pop_up_win.resizable(width=True, height=True)
    pop_up_win.geometry("580x550")
    vcmd = (pop_up_win.register(validate), "%P")
    bolded = FNT.Font(weight="bold")  # will use the default font
    x = root.winfo_x()
    y = root.winfo_y()
    pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))

    menubar = Menu(pop_up_win)
    pop_up_win.config(menu=menubar)
    helpmenu = Menu(menubar, tearoff=0)
    # helpmenu.add_command(label="Important Info", command=lambda: pop_up(
    # "\u2022 Offline use only! Using this feature may get you banned."))
    # helpmenu.add_command(label="Watch Video", command=lambda:
    # webbrowser.open_new_tab(stat_edit_video))
    menubar.add_cascade(label="MAY BE UNSAFE ONLINE!", menu=helpmenu)

    # MAIN SAVE FILE LISTBOX
    lb1 = Listbox(
        pop_up_win, borderwidth=3, width=15, height=10, exportselection=0
    )
    lb1.config(font=bolded)
    lb1.grid(row=0, column=0, padx=(55, 0), pady=(35, 295), sticky="n")
    load_listbox(lb1)

    # SELECT LISTBOX ITEM BUTTON
    but_select1 = Button(
        pop_up_win,
        text="Select",
        command=lambda: get_char_names(lb1, dropdown1, vars),
    )
    but_select1.grid(row=0, column=0, padx=(55, 0), pady=(50, 0))

    # DROPDOWN MENU STUFF
    opts = [""]
    vars = StringVar(pop_up_win)
    vars.set("Character")
    dropdown1 = OptionMenu(pop_up_win, vars, *opts)
    dropdown1.grid(row=0, column=0, padx=(55, 0), pady=(120, 0))

    # GET STATS BUTTON
    but_getstats = Button(pop_up_win, text="Get Stats", command=get_char_stats)
    but_getstats.grid(row=0, column=0, padx=(55, 0), pady=(210, 0))

    # VIGOR
    vig_lab = Label(pop_up_win, text="VIGOR:")
    vig_lab.config(font=bolded)
    vig_lab.grid(row=0, column=1, padx=(60, 0), pady=(35, 0), sticky="n")

    vig_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    vig_ent.grid(row=0, column=1, padx=(160, 0), pady=(35, 0), sticky="n")

    # MIND
    min_lab = Label(pop_up_win, text="MIND:")
    min_lab.config(font=bolded)
    min_lab.grid(row=0, column=1, padx=(60, 0), pady=(75, 0), sticky="n")

    min_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    min_ent.grid(row=0, column=1, padx=(160, 0), pady=(75, 0), sticky="n")

    # ENDURANCE
    end_lab = Label(pop_up_win, text="END:")
    end_lab.config(font=bolded)
    end_lab.grid(row=0, column=1, padx=(60, 0), pady=(115, 0), sticky="n")

    end_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    end_ent.grid(row=0, column=1, padx=(160, 0), pady=(115, 0), sticky="n")

    # STRENGTH
    str_lab = Label(pop_up_win, text="STR:")
    str_lab.config(font=bolded)
    str_lab.grid(row=0, column=1, padx=(60, 0), pady=(155, 0), sticky="n")

    str_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    str_ent.grid(row=0, column=1, padx=(160, 0), pady=(155, 0), sticky="n")

    # DEXTERITY
    dex_lab = Label(pop_up_win, text="DEX:")
    dex_lab.config(font=bolded)
    dex_lab.grid(row=0, column=1, padx=(60, 0), pady=(195, 0), sticky="n")

    dex_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    dex_ent.grid(row=0, column=1, padx=(160, 0), pady=(195, 0), sticky="n")

    # INTELLIGENCE
    int_lab = Label(pop_up_win, text="INT:")
    int_lab.config(font=bolded)
    int_lab.grid(row=0, column=1, padx=(60, 0), pady=(235, 0), sticky="n")

    int_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    int_ent.grid(row=0, column=1, padx=(160, 0), pady=(235, 0), sticky="n")

    # FAITH
    fai_lab = Label(pop_up_win, text="FAITH:")
    fai_lab.config(font=bolded)
    fai_lab.grid(row=0, column=1, padx=(60, 0), pady=(275, 0), sticky="n")

    fai_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    fai_ent.grid(row=0, column=1, padx=(160, 0), pady=(275, 0), sticky="n")

    # ARCANE
    arc_lab = Label(pop_up_win, text="ARC:")
    arc_lab.config(font=bolded)
    arc_lab.grid(row=0, column=1, padx=(60, 0), pady=(315, 0), sticky="n")

    arc_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    arc_ent.grid(row=0, column=1, padx=(160, 0), pady=(315, 0), sticky="n")

    # lIST OF ALL ENTRIES
    entries = [
        vig_ent,
        min_ent,
        end_ent,
        str_ent,
        dex_ent,
        int_ent,
        fai_ent,
        arc_ent,
    ]

    # BOX THAT SHOWS CHAR LEVEL
    lvl_var = StringVar()
    lvl_var.set("Level: ")
    lvl_box = Entry(
        pop_up_win,
        borderwidth=2,
        width=10,
        textvariable=lvl_var,
        state=DISABLED,
    )
    lvl_box.config(font=bolded)
    lvl_box.grid(row=0, column=1, padx=(70, 0), pady=(355, 0), sticky="n")

    # RECALCULATE LVL BUTTON
    but_recalc_lvl = Button(pop_up_win, text="Recalc", command=recalc_lvl)
    but_recalc_lvl.grid(
        row=0, column=1, padx=(220, 0), pady=(355, 0), sticky="n"
    )

    # SET STATS BUTTON
    but_set_stats = Button(pop_up_win, text="Set Stats", command=set_stats)
    but_set_stats.config(font=bolded)
    but_set_stats.grid(
        row=0, column=1, padx=(0, 135), pady=(450, 0), sticky="n"
    )


def set_steam_id_menu():
    def done():

        file = f"{save_dir}{name}/{ext()}"
        id = ent.get()
        x = re.findall(r"\d{17}", str(id))
        if len(x) < 1:
            popup("Your id should be a 17 digit number.")
            return
        nms = get_char_names_from_file(file_name=file)
        archive_file(file, name, "ACTION: Changed SteamID", nms)
        out = hexedit.replace_id(file, int(x[0]))
        if out is False:
            popup("Unable to find SteamID, SaveData may be corrupt.")
            return
        popup("Successfully changed SteamID")
        pop_up_win.destroy()

    def cancel():
        pop_up_win.destroy()

    def validate(P):
        if len(P) == 0:
            return True
        elif len(P) < 18 and P.isdigit():
            return True
        else:
            # Anything else, reject it
            return False

    name = fetch_listbox_entry(lb)[0]
    pop_up_win = Toplevel(root)
    if name == "":
        popup("No listbox item selected.")
        pop_up_win.destroy()
    cur_id = hexedit.get_id(f"{save_dir}{name}/{ext()}")

    pop_up_win.title("Set SteamID")
    vcmd = (pop_up_win.register(validate), "%P")
    # pop_up_win.geometry("200x70")
    id_lab = Label(pop_up_win, text=f"Current ID: {cur_id}")
    id_lab.grid(row=0, column=0)
    lab = Label(pop_up_win, text="Enter new ID:")
    lab.grid(row=1, column=0)

    ent = Entry(pop_up_win, borderwidth=5, validate="key", validatecommand=vcmd)
    ent.grid(row=2, column=0, padx=25, pady=10)
    x = root.winfo_x()
    y = root.winfo_y()
    pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))
    but_done = Button(
        pop_up_win, text="Done", borderwidth=5, width=6, command=done
    )
    but_done.grid(row=3, column=0, padx=(25, 65), pady=(0, 15), sticky="w")
    but_cancel = Button(
        pop_up_win, text="Cancel", borderwidth=5, width=6, command=cancel
    )
    but_cancel.grid(row=3, column=0, padx=(70, 0), pady=(0, 15))


def inventory_editor_menu():
    def pop_up(txt, bold=True):
        text.delete("1.0", END)
        text.insert(END, txt)
        pop_up_win.update()
        return

        def close(event):
            win.destroy()

        """Basic popup window used only for parent function"""
        win = Toplevel(pop_up_win)
        win.title("Manager")
        lab = Label(win, text=txt)
        if bold is True:
            lab.config(font=bolded)
        lab.grid(row=0, column=0, padx=15, pady=15, columnspan=2)
        x = pop_up_win.winfo_x()
        y = pop_up_win.winfo_y()
        win.geometry("+%d+%d" % (x + 200, y + 200))
        win.bind("<Return>", close)
        win.focus_force()

    def validate(P):
        if len(P) == 0:
            return True
        elif len(P) < 4 and P.isdigit() and int(P) > 0:
            return True
        else:
            # Anything else, reject it
            return False

    def add():
        pop_up("Processing...")

        char = c_vars.get()  # "1. charname"
        if char == "Character" or char == "":
            pop_up("Character not selected")
            return

        item = i_vars.get()
        print(item)
        if item == "Items" or item == "":
            pop_up("Select an item first.")
            return

        if char.split(".")[1] == " ":
            pop_up(
                "Can't write to empty slot.\nGo in-game and create a "
                "character to overwrite."
            )
            return

        name = fetch_listbox_entry(lb1)[0]  # Save file name. EX: main
        if len(name) < 1:
            pop_up(txt="Slot not selected")
            return

        dest_file = f"{save_dir}{name}/{ext()}"
        char_ind = int(char.split(".")[0])

        qty = qty_ent.get()
        if qty == "":
            pop_up("Set a quantity first.")
            return
        else:
            qty = int(qty)
        cat_key = cat_vars.get()
        print(cat_key)
        itemid = itemdb.db.get(cat_key).get(item)
        print(itemid)
        print(dest_file)
        archive_file(
            dest_file,
            name,
            "ACTION: Add inventory items",
            get_char_names_from_file(dest_file),
        )
        variable_to_set = hexedit.additem(dest_file, char_ind, itemid, qty)
        if variable_to_set is None:
            pop_up("Failed to edit item count")
        else:
            pop_up("Successfully added items")
        return

    def add_bulk():
        pop_up("Processing...")

        char = c_vars.get()  # "1. charname"
        if char == "Character" or char == "":
            pop_up("Character not selected")
            return

        if char.split(".")[1] == " ":
            pop_up(
                "Can't write to empty slot.\nGo in-game and create a "
                "character to overwrite."
            )
            return

        name = fetch_listbox_entry(lb1)[0]  # Save file name. EX: main
        if len(name) < 1:
            pop_up(txt="Slot not selected")
            return

        dest_file = f"{save_dir}{name}/{ext()}"
        char_ind = int(char.split(".")[0])

        qty = qty_ent.get()
        if qty == "":
            pop_up("Set a quantity first.")
            return
        else:
            qty = int(qty)

        category_items = itemdb.db[cat_vars.get()]

        archive_file(
            dest_file,
            name,
            "ACTION: Add inventory items",
            get_char_names_from_file(dest_file),
        )
        failed = []
        for itemname, itemid in category_items.items():
            x = hexedit.additem(dest_file, char_ind, itemid, qty)
            if x is None:
                failed.append(itemname)

        if not failed:
            pop_up("Successfully added items")
        else:
            msg = "Failed:\n" + "\n".join(failed)
            pop_up(msg)
        return

    def add_b(event):
        add()

    def populate_items(*args):
        global itemdb
        """Populates the item dropdown by getting category"""

        cat = cat_vars.get()
        itemdb = itemdata.Items()
        items = itemdb.get_item_ls(cat)

        dropdown3["menu"].delete(0, "end")  # remove full list
        for i in items:
            if len(i) > 1:
                dropdown3["menu"].add_command(
                    label=i, command=TKIN._setit(i_vars, i)
                )
        i_vars.set("Items")  # default value set

    def manual_search():
        try:
            delete_folder(f"{temp_dir}1")
            delete_folder(f"{temp_dir}2")
            delete_folder(f"{temp_dir}3")
        except Exception:
            pass
        pop_up_win.destroy()
        find_itemid()

    def add_custom_id():
        def done():
            name = name_ent.get()
            ids = [id_ent1.get(), id_ent2.get()]
            if len(ids[0]) < 1 or len(ids[1]) < 1:
                return
            id = [int(ids[0]), int(ids[1])]
            try:
                config.add_to("custom_ids", {name: id})
            except Exception as e:
                popup(f"Error:\n\n{repr(e)}")
                return

            idwin.destroy()
            pop_up_win.destroy()
            inventory_editor_menu()

        def validate_id(P):
            if len(P) > 0 and len(P) < 4 and P.isdigit():
                return True
            else:
                return False

        def validate_name(P):
            if len(P) > 0 and len(P) < 29 and P.isdigit() is False:
                return True
            else:
                return False

        idwin = Toplevel(root)
        idwin.title("Add Custom ID")
        vcmd_id = (idwin.register(validate_id), "%P")
        vcmd_name = (idwin.register(validate_name), "%P")
        # pop_up_win.geometry("200x70")

        x = root.winfo_x()
        y = root.winfo_y()
        idwin.geometry("+%d+%d" % (x + 200, y + 200))

        name_lab = Label(idwin, text="Item Name: ")
        name_lab.grid(row=0, column=0, padx=(0, 0), pady=(10, 0))
        name_ent = Entry(
            idwin,
            borderwidth=5,
            width=25,
            validate="key",
            validatecommand=vcmd_name,
        )
        name_ent.grid(row=1, column=0, padx=(20, 20), pady=(10, 0))

        id_lab = Label(idwin, text="ID: ")
        id_lab.grid(row=2, column=0, padx=(20, 0), pady=(15, 15), sticky="w")

        id_ent1 = Entry(
            idwin,
            borderwidth=5,
            width=3,
            validate="key",
            validatecommand=vcmd_id,
        )
        id_ent1.grid(row=2, column=0, padx=(50, 0), pady=(15, 15), sticky="w")

        id_ent2 = Entry(
            idwin,
            borderwidth=5,
            width=3,
            validate="key",
            validatecommand=vcmd_id,
        )
        id_ent2.grid(row=2, column=0, padx=(80, 0), pady=(15, 15), sticky="w")

        but_done = Button(
            idwin, text="Add", borderwidth=5, width=6, command=done
        )
        but_done.grid(row=2, column=0, sticky="w", padx=(120, 0), pady=(15, 15))

    def find_itemid():

        def validate(P):
            if len(P) == 0:
                return True
            elif len(P) < 4 and P.isdigit() and int(P) > 0:
                return True
            else:
                return False

        def load_temp_save(pos):
            if config.cfg["gamedir"] == "" or len(config.cfg["gamedir"]) < 2:
                popup("Please set your Default Game Directory first")
                return
            if os.path.isdir(temp_dir) is False:
                cmd_out = run_command(lambda: os.makedirs(temp_dir))
                if cmd_out[0] == "error":
                    popup("Error! unable to make temp directory.")
                    return

            if os.path.isdir(f"{temp_dir}1") is False:
                cmd_out = run_command(lambda: os.makedirs(f"{temp_dir}1"))
                if cmd_out[0] == "error":
                    popup("Error! unable to make temp directory.")
                    return

            if os.path.isdir(f"{temp_dir}2") is False:
                cmd_out = run_command(lambda: os.makedirs(f"{temp_dir}2"))
                if cmd_out[0] == "error":
                    popup("Error! unable to make temp directory.")
                    return

            if os.path.isdir(f"{temp_dir}3") is False:
                cmd_out = run_command(lambda: os.makedirs(f"{temp_dir}3"))
                if cmd_out[0] == "error":
                    popup("Error! unable to make temp directory.")
                    return

            if pos == 1:
                copy_file(
                    f"{config.cfg['gamedir']}/{ext()}", f"{temp_dir}/1/{ext()}"
                )
                file_paths[0] = f"{temp_dir}/1/{ext()}"

            if pos == 2:
                copy_file(
                    f"{config.cfg['gamedir']}/{ext()}", f"{temp_dir}/2/{ext()}"
                )
                file_paths[1] = f"{temp_dir}/2/{ext()}"

            if pos == 3:
                copy_file(
                    f"{config.cfg['gamedir']}/{ext()}", f"{temp_dir}/3/{ext()}"
                )
                file_paths[2] = f"{temp_dir}/3/{ext()}"

            window.lift()

        def name_id_popup(id):
            def add_custom_id(id):
                name = name_ent.get()
                if len(name) > 16:
                    popup("Name too long", parent_window=window)
                    return

                try:

                    config.add_to("custom_ids", {name: id})
                    window.destroy()
                    inventory_editor_menu()

                except Exception as e:
                    popup(
                        f"Something went wrong.\nvalues: {name, id}\nError: {e}"
                    )
                    return
                pop_up_win.destroy()

            pop_up_win = Toplevel(window)
            pop_up_win.title("Add Item ID")
            (pop_up_win.register(validate), "%P")
            # pop_up_win.geometry("200x70")

            lab = Label(pop_up_win, text=f"Item ID: {id}\nEnter item name:")
            lab.grid(row=0, column=0)
            name_ent = Entry(pop_up_win, borderwidth=5)
            name_ent.grid(row=1, column=0, padx=25, pady=10)
            x = window.winfo_x()
            y = window.winfo_y()
            pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))
            but_done = Button(
                pop_up_win,
                text="Add",
                borderwidth=5,
                width=6,
                command=lambda: add_custom_id(id),
            )
            but_done.grid(
                row=2, column=0, padx=(25, 65), pady=(0, 15), sticky="w"
            )
            but_cancel = Button(
                pop_up_win,
                text="Cancel",
                borderwidth=5,
                width=6,
                command=lambda: pop_up_win.destroy(),
            )
            but_cancel.grid(row=2, column=0, padx=(70, 0), pady=(0, 15))

        def multi_item_select(indexes):
            def grab_id(listbox):
                ind = fetch_listbox_entry(listbox)[0].split(":")[0]

                if ind == "":
                    popup("No value selected!")
                    return
                else:
                    pop_up_win.destroy()
                    name_id_popup(indexes[int(ind)])

            pop_up_win = Toplevel(window)
            pop_up_win.title("Add Item ID")
            (pop_up_win.register(validate), "%P")
            x = window.winfo_x()
            y = window.winfo_y()
            pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))
            lab = Label(
                pop_up_win,
                text="Multiple locations found! Select an address.\nLower "
                "addresses have a higher chance of success.",
            )
            lab.grid(row=0, column=0, padx=(5, 5))

            lb1 = Listbox(
                pop_up_win,
                borderwidth=3,
                width=19,
                height=10,
                exportselection=0,
            )
            lb1.config(font=bolded)
            lb1.grid(row=1, column=0)

            but_select = Button(
                pop_up_win,
                text="Select",
                borderwidth=5,
                width=6,
                command=lambda: grab_id(lb1),
            )
            but_select.grid(
                row=2, column=0, padx=(50, 65), pady=(5, 15), sticky="w"
            )
            but_cancel = Button(
                pop_up_win,
                text="Cancel",
                borderwidth=5,
                width=6,
                command=lambda: pop_up_win.destroy(),
            )
            but_cancel.grid(row=2, column=0, padx=(85, 0), pady=(5, 15))
            # Insert itemids alongside addresses so users can see if ids are
            # like [0,0] and thus wrong
            for k, v in indexes.items():
                if v == [0, 0]:  # Obviously not an item ID
                    continue
                lb1.insert(END, "  " + f"{k}: {v}")

        def search():

            valid = True
            # VALIDATE USER INPUTS

            if len([i for i in file_paths if not i == 0]) < 3:
                popup(
                    "Not all save files selected.",
                    root_element=root,
                    parent_window=window,
                )
                return

            if (
                len(q1_ent.get()) < 1
                or len(q2_ent.get()) < 1
                or len(q3_ent.get()) < 1
            ):
                popup(
                    "Enter a quantity for all save files.",
                    root_element=root,
                    parent_window=window,
                )
                return

            for p in file_paths:
                if not os.path.exists(p):
                    valid = False
            if not valid:
                popup("Invalid paths")
                return

            item_id = hexedit.search_itemid(
                file_paths[0],
                file_paths[1],
                file_paths[2],
                q1_ent.get(),
                q2_ent.get(),
                q3_ent.get(),
            )
            if item_id is None:
                popup("Unable to find item ID")
                return
            if item_id[0] == "match":
                name_id_popup(item_id[1])

            if item_id[0] == "multi-match":
                multi_item_select(item_id[1])

            delete_folder(f"{temp_dir}1")
            delete_folder(f"{temp_dir}2")
            delete_folder(f"{temp_dir}3")

        def callback(url):
            webbrowser.open_new(url)

        file_paths = [0, 0, 0]

        window = Toplevel(root)
        window.title("Inventory Editor")
        window.resizable(width=True, height=True)
        window.geometry("530x560")

        vcmd = (window.register(validate), "%P")

        bolded = FNT.Font(weight="bold")  # will use the default font

        x = root.winfo_x()
        y = root.winfo_y()
        window.geometry("+%d+%d" % (x + 200, y + 200))

        menubar = Menu(window)
        window.config(menu=menubar)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Search", command=find_itemid)
        # menubar.add_cascade(label="Manually add item", menu=helpmenu)
        padding_lab1 = Label(window, text=" ")
        padding_lab1.pack()

        but_open1 = Button(
            window, text="Grab Data 1", command=lambda: load_temp_save(1)
        )
        but_open1.pack()
        s1_label = Label(window, text="Quantity:")
        s1_label.pack()
        q1_ent = Entry(
            window, borderwidth=5, width=3, validate="key", validatecommand=vcmd
        )
        q1_ent.pack()

        but_open2 = Button(
            window, text="Grab Data 2", command=lambda: load_temp_save(2)
        )
        but_open2.pack()
        s2_label = Label(window, text="Quantity:")
        s2_label.pack()
        q2_ent = Entry(
            window, borderwidth=5, width=3, validate="key", validatecommand=vcmd
        )
        q2_ent.pack()

        but_open3 = Button(
            window, text="Grab Data 3", command=lambda: load_temp_save(3)
        )
        but_open3.pack()
        s3_label = Label(window, text="Quantity:")
        s3_label.pack()
        q3_ent = Entry(
            window, borderwidth=5, width=3, validate="key", validatecommand=vcmd
        )
        q3_ent.pack()

        padding_lab2 = Label(window, text=" ")
        padding_lab2.pack()

        but_search = Button(window, text="Search", command=search)
        but_search.pack()

        help_text = (
            "\n\n----- HOW TO -----\n\n1. Go in-game and note the "
            "quantity of the item you are trying to find. \n2. Exit "
            "to main menu and enter the quantity in the Manager.\n3. "
            "Click grab data 1.\n4. Go back in-game and load into "
            "the save file.\n5. Drop some of the items so the "
            "quantity is different from the original.\n6. Exit to "
            "main menu again.\n7. Enter the new quantity and click "
            "grab data 2.\n8. Repeat the process for #3.\n9. Click "
            "Search.\n\nNOTE: You must be using the first character "
            "in your save file!\n"
        )
        help_lab = Label(window, text=help_text)
        help_lab.pack()

        post_but = Button(
            window,
            text="Watch Video",
            command=lambda: callback(custom_search_tutorial_url),
        )
        post_but.pack()

    def remove_id():

        def done():
            name = fetch_listbox_entry(lb1)[1].strip()
            if len(name) < 1:
                return
            try:
                config.delete_custom_id(name)
            except Exception as e:
                popup(f"Error: Unable to delete Item\n\n{repr(e)}")
            idwin.destroy()
            pop_up_win.destroy()
            inventory_editor_menu()

        idwin = Toplevel(root)
        idwin.title("Remove Custom ID")
        # pop_up_win.geometry("200x70")

        x = root.winfo_x()
        y = root.winfo_y()
        idwin.geometry("+%d+%d" % (x + 200, y + 200))

        lb1 = Listbox(
            idwin, borderwidth=3, width=15, height=10, exportselection=0
        )
        lb1.config(font=bolded)
        lb1.grid(row=0, column=0, padx=(0, 0), pady=(20, 20))
        for i in config.cfg["custom_ids"]:
            lb1.insert(END, "  " + i)

        but_done = Button(
            idwin, text="Delete", borderwidth=5, width=6, command=done
        )
        but_done.grid(row=1, column=0, sticky="w", padx=(100, 0), pady=(0, 15))
        but_cancel = Button(
            idwin,
            text="Cancel",
            borderwidth=5,
            width=6,
            command=lambda: idwin.destroy(),
        )
        but_cancel.grid(
            row=1, column=0, sticky="w", padx=(200, 100), pady=(0, 15)
        )

    def replace_menu():
        def populate_items(*args):
            global itemdb

            cat = cat_vars.get()
            itemdb = itemdata.Items()
            items = itemdb.get_item_ls(cat)

            dropdown3["menu"].delete(0, "end")  # remove full list
            for i in items:
                if len(i) > 1:
                    dropdown3["menu"].add_command(
                        label=i, command=TKIN._setit(i_vars, i)
                    )
            i_vars.set("Items")  # default value set
            c_vars.get()

        def populate_inventory():
            inv_lb.delete(0, END)
            char = c_vars.get()  # "1. charname"
            if char == "Character" or char == "":
                popup("Character not selected", parent_window=win)
                return

            if char.split(".")[1] == " ":
                popup(
                    "Can't write to empty slot.\nGo in-game and create a "
                    "character to overwrite.",
                    parent_window=win,
                )
                return

            name = fetch_listbox_entry(lb1)[0]  # Save file name. EX: main
            if len(name) < 1:
                popup(txt="Slot not selected", parent_window=win)
                return

            dest_file = f"{save_dir}{name}/{ext()}"
            char_ind = int(char.split(".")[0])

            try:
                inventory_items = hexedit.get_inventory(dest_file, char_ind)
            except:
                popup(
                    "Unable to load inventory! Do you have Tarnished's "
                    "Wizened Finger?",
                    parent_window=win,
                )
                return
            for item in inventory_items:
                inv_lb.insert(END, "  " + item["name"])

            # Main GUI content STAT

        def replace_item():

            item = i_vars.get()
            if item == "Items" or item == "":
                popup("Select an item first.", parent_window=win)
                return

            char = c_vars.get()  # "1. charname"
            if char == "Character" or char == "":
                popup("Character not selected", parent_window=win)
                return

            if char.split(".")[1] == " ":
                popup(
                    "Can't write to empty slot.\nGo in-game and create a "
                    "character to overwrite.",
                    parent_window=win,
                )
                return

            item_to_replace = fetch_listbox_entry(inv_lb)[1].lstrip()
            if item_to_replace == "":
                popup("Select an item to replace!", parent_window=win)
                return

            name = fetch_listbox_entry(lb1)[
                1
            ].strip()  # Save file name. EX: main
            if len(name) < 1:
                popup(txt="Slot not selected", parent_window=win)
                return

            dest_file = f"{save_dir}{name}/{ext()}"
            char_ind = int(char.split(".")[0])
            archive_file(
                dest_file,
                name,
                f"ACTION: Replaced {item_to_replace}",
                get_char_names_from_file(dest_file),
            )

            inventory_entries = hexedit.get_inventory(dest_file, char_ind)

            itemid = itemdb.db[cat_vars.get()].get(item)

            for entry in inventory_entries:
                if entry["name"] == item_to_replace:
                    hexedit.overwrite_item(dest_file, char_ind, entry, itemid)
                    popup(
                        f"Successfully replaced {item_to_replace}",
                        parent_window=win,
                    )
                    inv_lb.delete(0, END)
                    return

        def replace_item_b():
            replace_item()

        pop_up_win.destroy()
        win = Toplevel(root)
        win.title("Replace Items")
        win.resizable(width=True, height=True)
        win.geometry("610x540")
        x = root.winfo_x()
        y = root.winfo_y()
        win.geometry("+%d+%d" % (x + 200, y + 200))

        menubar = Menu(win)
        win.config(menu=menubar)
        helpmenu = Menu(menubar, tearoff=0)
        message = (
            "This feature is experimental and may not work for "
            "everything!\n\n-Weapons/Armor is unsupported\n\n-You "
            "should try to replace an item with another of the same "
            "category ex: crafting materials\n\n-Try not to replace an "
            "item you already have, or you will get two stacks of the "
            "same item\n\n-Not all items will appear in the inventory "
            "box, only detected items that can be overwritten\n\nYou "
            "must have Tarnished's Wizened Finger in your inventory ("
            "First item you pickup)\n"
        )
        helpmenu.add_command(
            label="Readme", command=lambda: popup(message, parent_window=win)
        )
        menubar.add_cascade(label="Help", menu=helpmenu)

        # MAIN SAVE FILE LISTBOX
        lb1 = Listbox(
            win, borderwidth=3, width=15, height=10, exportselection=0
        )
        lb1.config(font=bolded, width=20)
        lb1.grid(row=1, column=0, padx=(10, 0), pady=(10, 10))
        load_listbox(lb1)

        # SELECT LISTBOX ITEM BUTTON
        but_select1 = Button(
            win,
            text="Select",
            command=lambda: get_char_names(lb1, dropdown1, c_vars),
        )
        # but_select1.config(bg='grey', fg='white')
        but_select1.grid(row=2, column=0, padx=(10, 0), pady=(0, 0))

        # CHARACTER DROPDOWN MENU
        opts = [""]
        c_vars = StringVar(win)
        c_vars.set("Character")
        dropdown1 = OptionMenu(win, c_vars, *opts)
        dropdown1.grid(row=3, column=0, padx=(10, 0), pady=(0, 0))
        get_char_names(lb1, dropdown1, c_vars)
        charname = dropdown1["menu"].entrycget(0, "label")
        c_vars.set(charname)

        # LABEL REPLACE WITH
        repl_lab = Label(win, text="Replace with:")
        repl_lab.grid(row=4, column=1)

        # CATEGORY DROPDOWN
        opts1 = itemdb.categories
        cat_vars = StringVar(win)
        cat_vars.set("Category")
        dropdown2 = OptionMenu(win, cat_vars, *opts1)
        dropdown2.config(width=15)

        cat_vars.trace("w", populate_items)
        dropdown2.grid(row=5, column=1, padx=(10, 0), pady=(0, 0))

        # ITEM DROPDOWN
        opts2 = [""]
        i_vars = StringVar(win)
        i_vars.set("Items")
        dropdown3 = OptionMenu(win, i_vars, *opts2)
        dropdown3.config(width=15)
        dropdown3.grid(row=6, column=1, padx=(10, 0), pady=(0, 0))

        but_replace = Button(win, text="Replace", command=replace_item)
        but_replace.grid(row=7, column=1, padx=(10, 0), pady=(50, 10))

        # inventory items listbox
        inv_lb = Listbox(
            win, borderwidth=3, width=15, height=10, exportselection=0
        )
        inv_lb.config(font=bolded, width=25)
        inv_lb.grid(row=1, column=2, padx=(10, 10), pady=(10, 10))

        # get inventory button
        but_get_inv = Button(
            win, text="Get Inventory", command=populate_inventory
        )
        but_get_inv.grid(row=2, column=2, padx=(10, 0), pady=(10, 10))
        populate_inventory()

        win.bind("<Return>", replace_item_b)

    # Main GUI content STAT
    pop_up_win = Toplevel(root)
    pop_up_win.title("Inventory Editor")
    pop_up_win.resizable(width=True, height=True)
    pop_up_win.geometry("530x640")

    vcmd = (pop_up_win.register(validate), "%P")

    bolded = FNT.Font(weight="bold")  # will use the default font

    x = root.winfo_x()
    y = root.winfo_y()
    pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))

    menubar = Menu(pop_up_win)
    pop_up_win.config(menu=menubar)
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Replace item", command=replace_menu)
    helpmenu.add_command(label="Search", command=manual_search)
    helpmenu.add_command(label="Add item by ID", command=add_custom_id)
    helpmenu.add_command(label="Remove Custom Item", command=remove_id)
    helpmenu.add_command(
        label="View Master Spreadsheet",
        command=lambda: webbrowser.open_new_tab(
            "https://github.com/Ariescyn/EldenRing-Save-Manager/blob/main"
            "/ALL_ITEM_IDS.md"
        ),
    )
    menubar.add_cascade(label="Actions", menu=helpmenu)

    # MAIN SAVE FILE LISTBOX
    lb1 = Listbox(
        pop_up_win, borderwidth=3, width=15, height=3, exportselection=0
    )
    lb1.config(font=bolded)
    lb1.grid(row=1, column=0)
    load_listbox(lb1)

    # SELECT LISTBOX ITEM BUTTON
    but_select1 = Button(
        pop_up_win,
        text="Select",
        command=lambda: get_char_names(lb1, dropdown1, c_vars),
    )
    # but_select1.config(bg='grey', fg='white')
    but_select1.grid(row=2, column=0)

    # CHARACTER DROPDOWN MENU
    opts = [""]
    c_vars = StringVar(pop_up_win)
    c_vars.set("Character")
    dropdown1 = OptionMenu(pop_up_win, c_vars, *opts)
    dropdown1.grid(row=3, column=0)
    get_char_names(lb1, dropdown1, c_vars)
    charname = dropdown1["menu"].entrycget(0, "label")
    c_vars.set(charname)

    # CATEGORY DROPDOWN
    opts1 = itemdb.categories
    cat_vars = StringVar(pop_up_win)
    cat_vars.set("Category")
    dropdown2 = OptionMenu(pop_up_win, cat_vars, *opts1)

    cat_vars.trace("w", populate_items)
    dropdown2.grid(row=1, column=1)

    # ITEM DROPDOWN
    opts2 = [""]
    i_vars = StringVar(pop_up_win)
    i_vars.set("Items")
    dropdown3 = OptionMenu(pop_up_win, i_vars, *opts2)
    dropdown3.grid(row=2, column=1)

    qty_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    qty_ent.grid(row=3, column=1)

    # ADD ITEM BUTTON
    but_set = Button(pop_up_win, text="Set", command=add)
    but_set.config(font=bolded)
    but_set.grid(row=4, column=1)
    pop_up_win.bind("<Return>", add_b)

    # ADD BULK ITEM BUTTON
    but_set = Button(pop_up_win, text="Set bulk", command=add_bulk)
    but_set.config(font=bolded)
    but_set.grid(row=5, column=1)

    scroll = Scrollbar(pop_up_win, orient="vertical")
    text = Text(pop_up_win, height=24, width=40, yscrollcommand=scroll.set)
    scroll.config(command=text.yview)
    text.grid(row=6, column=0, columnspan=2)
    scroll.grid(row=6, column=1, columnspan=2, sticky=N + S + W)


def recovery_menu():
    def do_popup(event):
        try:
            rt_click_menu.tk_popup(
                event.x_root, event.y_root
            )  # Grab x,y position of mouse cursor
        finally:
            rt_click_menu.grab_release()

    def recover():
        name = (
            fetch_listbox_entry(lb1)[1]
            .strip()
            .replace(" ", "__")
            .replace(":", ".")
        )
        if len(name) < 1:
            popup("\nNothing selected!\n")
            return
        path = f"./data/archive/{name}/ER0000.xz"
        folder_path = f"./data/recovered/{name}/"

        try:
            unarchive_file(path)
            popup(
                "Succesfully recovered save file.\nImport now?",
                functions=(
                    lambda: import_save_menu(directory=folder_path + ext()),
                    do_nothing,
                ),
                buttons=True,
                button_names=("Yes", "No"),
                root_element=root,
            )
        except FileNotFoundError as e:
            popup(e)

    def pop_up(txt, bold=True):
        """Basic popup window used only for parent function"""
        pwin = Toplevel(win)
        pwin.title("Manager")
        lab = Label(pwin, text=txt)
        if bold is True:
            lab.config(font=bolded)
        lab.grid(row=0, column=0, padx=15, pady=15, columnspan=2)
        x = win.winfo_x()
        y = win.winfo_y()
        pwin.geometry("+%d+%d" % (x + 200, y + 200))

    def delete_entry(directory):

        def delete(directory):
            delete_folder(directory)
            selected_index = lb1.curselection()
            if selected_index:
                lb1.delete(selected_index)
            win.update()

        def dont_delete():
            pass

        popup(
            "Are you sure?",
            parent_window=win,
            functions=(lambda: delete(directory), dont_delete),
            buttons=True,
            root_element=root,
        )

    def delete_all():
        folder_path = "./data/archive/"
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)
        lb1.delete(0, END)

    win = Toplevel(root)
    win.title("Recovery")
    win.resizable(width=True, height=True)
    win.geometry("530x640")

    # bolded = FNT.Font(weight="bold")  # will use the default font

    x = root.winfo_x()
    y = root.winfo_y()
    win.geometry("+%d+%d" % (x + 200, y + 200))

    menubar = Menu(win)
    win.config(menu=menubar)
    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(
        label="Readme",
        command=lambda: pop_up(
            """\u2022 This tool recovers save files in case of user error.\n
            \u2022 Every time you modify/create/delete a save file, before
            the action is performed, a copy is created, compressed and stored
            in data/archive.\n \u2022 The original file size of 28mb is
            compressed to 2mb. To recover a file, simply select a file and
            click Restore.\n \u2022 Restored save files are in the
            data/recovered directory.\n \u2022 Right-click on a save in the
            listbox to get additional file info."""
        ),
    )
    help_menu.add_command(
        label="Delete All",
        command=lambda: popup(
            text="Are you sure?",
            buttons=True,
            functions=(delete_all, do_nothing),
            root_element=root,
        ),
    )
    menubar.add_cascade(label="File", menu=help_menu)

    # LISTBOX
    lb1 = Listbox(win, borderwidth=3, width=32, height=25, exportselection=0)
    lb1.config(font=bolded)
    lb1.grid(row=1, column=0, padx=(120, 0), pady=(35, 15))
    if os.path.isdir("./data/archive/") is True:
        lb1.delete(0, END)
        entries = sorted(
            PATH("./data/archive/").iterdir(), key=os.path.getmtime
        )

        for entry in reversed(entries):
            lb1.insert(
                END,
                "  "
                + str(entry)
                .replace("\\", "/")
                .split("archive/")[1]
                .replace("__", " ")
                .replace(".", ":"),
            )

    rt_click_menu = Menu(lb1, tearoff=0)
    rt_click_menu.add_command(
        label="Get Info",
        command=lambda: grab_metadata(
            f"./data/archive/{fetch_listbox_entry(lb1)[1].strip()}/info.txt"
        ),
    )

    sub_dir = (
        fetch_listbox_entry(lb1)[1].strip().replace(" ", "__").replace(":", ".")
    )

    directory = f"./data/archive/{sub_dir}/"

    rt_click_menu.add_command(
        label="Delete",
        command=lambda: delete_entry(directory),
    )
    lb1.bind("<Button-3>", do_popup)

    # SELECT LISTBOX ITEM BUTTON
    but_select1 = Button(win, text="Recover", command=recover)
    but_select1.grid(row=2, column=0, padx=(120, 0), pady=(0, 10))


def seamless_coop_menu():
    def x():
        return "Enabled" if config.cfg["seamless-coop"] else "Disabled"

    popup(
        f"Enable this option to support the seamless Co-op mod .co2 "
        f"extension\nIt's recommended to use a separate copy of the Manager "
        f"just for seamless co-op.\n\nCurrent State: {x()}",
        buttons=True,
        button_names=("Enable", "Disable"),
        functions=(
            lambda: config.set("seamless-coop", True),
            lambda: config.set("seamless-coop", False),
        ),
    )


def set_playtimes_menu():
    # This function is unused. The game will overwrite modified playtime
    # value on reload with original value.
    def set():
        choice = vars.get()
        try:
            choice_real = choice.split(". ")[1]
        except IndexError:
            popup("Select a character!")
            return
        slot_ind = int(choice.split(".")[0])
        if (
            len(hr_ent.get()) < 1
            or len(min_ent.get()) < 1
            or len(sec_ent.get()) < 1
        ):
            popup("Set a value for hr/min/sec")
            return
        time = [hr_ent.get(), min_ent.get(), sec_ent.get()]
        archive_file(path, choice_real, "ACTION: Change Play Time", names)
        hexedit.set_play_time(path, slot_ind, time)
        popup("Success")

    def validate_hr(P):
        if len(P) > 0 and len(P) < 5 and P.isdigit():
            return True
        else:
            return False

    def validate_min_sec(P):
        if len(P) > 0 and len(P) < 3 and P.isdigit() and int(P) < 61:
            return True
        else:
            return False

    name = fetch_listbox_entry(lb)[0]
    if name == "":
        popup("No listbox item selected.")
        return
    path = f"{save_dir}{name}/{ext()}"
    names = get_char_names_from_file(path)
    if names is False:
        popup(
            "FileNotFoundError: This is a known issue.\nPlease try "
            "re-importing your save file."
        )

    chars = []
    for ind, i in enumerate(names):
        if i is not None:
            chars.append(f"{ind + 1}. {i}")

    rwin = Toplevel(root)
    rwin.title("Set Play Time")
    rwin.geometry("200x250")

    vcmd_hr = (rwin.register(validate_hr), "%P")
    vcmd_min_sec = (rwin.register(validate_min_sec), "%P")

    bolded = FNT.Font(weight="bold")  # will use the default font
    x = root.winfo_x()
    y = root.winfo_y()
    rwin.geometry("+%d+%d" % (x + 250, y + 200))

    opts = chars
    vars = StringVar(rwin)
    vars.set("Character")

    drop = OptionMenu(rwin, vars, *opts)
    drop.grid(row=0, column=0, padx=(15, 0), pady=(15, 0))
    drop.configure(width=20)

    hr_lab = Label(rwin, text="Hours: ")
    hr_lab.grid(row=1, column=0, padx=(15, 0), pady=(15, 0), sticky="w")
    hr_ent = Entry(
        rwin, borderwidth=5, width=5, validate="key", validatecommand=vcmd_hr
    )
    hr_ent.grid(row=1, column=0, padx=(70, 0), pady=(15, 0))

    min_lab = Label(rwin, text="Minutes: ")
    min_lab.grid(row=2, column=0, padx=(15, 0), pady=(15, 0), sticky="w")
    min_ent = Entry(
        rwin,
        borderwidth=5,
        width=5,
        validate="key",
        validatecommand=vcmd_min_sec,
    )
    min_ent.grid(row=2, column=0, padx=(70, 0), pady=(15, 0))

    min_lab = Label(rwin, text="Seconds: ")
    min_lab.grid(row=3, column=0, padx=(15, 0), pady=(15, 0), sticky="w")
    sec_ent = Entry(
        rwin,
        borderwidth=5,
        width=5,
        validate="key",
        validatecommand=vcmd_min_sec,
    )
    sec_ent.grid(row=3, column=0, padx=(70, 0), pady=(15, 0))

    but_go = Button(rwin, text="Set", borderwidth=5, command=set)
    but_go.config(font=bolded)
    but_go.grid(row=4, column=0, padx=(15, 0), pady=(20, 0))


def set_starting_class_menu():
    def set_attr():
        if class_var.get() == "Class":
            popup("No class selected!")
            return
        if char_var.get() == "Character":
            popup("No Character Selected!")
            return
        src_ind = int(char_var.get().split(".")[0])
        selected_name = char_var.get().split(".")[1]
        archive_file(
            path, name, f"Modified starting class of {selected_name}", names
        )
        hexedit.set_starting_class(path, src_ind, class_var.get())
        popup("Success!")
        return

    # Populate dropdown containing characters.
    name = fetch_listbox_entry(lb)[0]
    if name == "":
        popup("No listbox item selected.")
        return
    path = f"{save_dir}{name}/{ext()}"
    names = get_char_names_from_file(path)
    if names is False:
        popup(
            "FileNotFoundError: This is a known issue.\nPlease try "
            "re-importing your save file.",
            root_element=root,
        )

    chars = []
    for ind, i in enumerate(names):
        if i is not None:
            chars.append(f"{ind + 1}. {i}")

    rwin = Toplevel(root)
    rwin.title("Set Starting Class")
    rwin.geometry("200x190")

    bolded_font = FNT.Font(weight="bold")  # will use the default font
    x = root.winfo_x()
    y = root.winfo_y()
    rwin.geometry("+%d+%d" % (x + 250, y + 200))

    opts = chars
    char_var = StringVar(rwin)
    char_var.set("Character")

    drop = OptionMenu(rwin, char_var, *opts)
    drop.grid(row=0, column=0, padx=(15, 0), pady=(15, 0))
    drop.configure(width=20)

    class_opts = [
        "Vagabond",
        "Warrior",
        "Hero",
        "Bandit",
        "Astrologer",
        "Prophet",
        "Confessor",
        "Samurai",
        "Prisoner",
        "Wretch",
    ]
    class_var = StringVar(rwin)
    class_var.set("Class")

    class_drop = OptionMenu(rwin, class_var, *class_opts)
    class_drop.grid(row=1, column=0, padx=(15, 0), pady=(15, 0))

    but_set = Button(rwin, text="Set", borderwidth=5, command=set_attr)
    but_set.config(font=bolded_font)
    but_set.grid(row=4, column=0, padx=(15, 0), pady=(20, 0))


def change_default_steamid_menu():
    def done():
        steam_id = ent.get()
        if not len(steam_id) == 17:
            popup("SteamID should be 17 digits long")
            return
        config.set("steamid", steam_id)

        popup("Successfully changed default SteamID")
        pop_up_win.destroy()

    def cancel():
        pop_up_win.destroy()

    def validate(P):
        if len(P) == 0:
            return True
        elif len(P) < 18 and P.isdigit():
            return True
        else:
            # Anything else, reject it
            return False

    pop_up_win = Toplevel(root)
    pop_up_win.title("Set SteamID")
    vcmd = (pop_up_win.register(validate), "%P")
    # pop_up_win.geometry("200x70")

    s_id = config.cfg["steamid"]
    lab = Label(pop_up_win, text=f"Current ID: {s_id}\nEnter new ID:")
    lab.grid(row=0, column=0)
    ent = Entry(pop_up_win, borderwidth=5, validate="key", validatecommand=vcmd)
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


def import_save_menu(directory: bool = False):
    """Opens file explorer to choose a save file to import, Then checks if
    the files steam ID matches users, and replaces it with users id"""

    if os.path.isdir(save_dir) is False:
        os.makedirs(save_dir)
    if directory:
        d = directory
    else:
        d = fd.askopenfilename()

    if len(d) < 1:
        return

    if not d.endswith(ext()):
        popup(
            "Select a valid save file!\nIt should be named: ER0000.sl2 or "
            "ER0000.co2 if seamless co-op is enabled.",
            root_element=root,
        )
        return

    def cancel():
        pop_up_win.destroy()

    def done():
        name = ent.get().strip()
        if len(name) < 1:
            popup("No name entered.", root_element=root)
            return
        is_forbidden = False
        for char in name:
            if char in r"~'{};:./\,:*?<>|-!@#$%^&()+":
                is_forbidden = True
        if is_forbidden is True:
            popup("Forbidden character used", root_element=root)
            return
        elif is_forbidden is False:
            entries = []
            for entry in os.listdir(save_dir):
                entries.append(entry)
            if name.replace(" ", "-") in entries:
                popup("Name already exists", root_element=root)
                return

        names = get_char_names_from_file(d)
        archive_file(d, name, "ACTION: Imported", names)

        new_dir = "{}{}/".format(save_dir, name.replace(" ", "-"))

        def cp_to_saves_cmd():
            return copy_file(d, new_dir)

        if os.path.isdir(new_dir) is False:
            cmd_out = run_command(lambda: os.makedirs(new_dir))

            if cmd_out[0] == "error":
                print("---ERROR #1----")
                return

            lb.insert(END, "  " + name)
            cmd_out = run_command(cp_to_saves_cmd)
            if cmd_out[0] == "error":
                return
            create_notes(name, f"{save_dir}{name.replace(' ', '-')}")
            file_id = hexedit.get_id(f"{new_dir}/{ext()}")
            user_id = config.cfg["steamid"]
            if len(user_id) < 17:
                pop_up_win.destroy()
                return
            if file_id != int(user_id):
                popup(
                    f"File SteamID: {file_id}\nYour SteamID: {user_id}",
                    buttons=True,
                    button_names=("Patch with your ID", "Leave it"),
                    b_width=(15, 8),
                    functions=(
                        lambda: hexedit.replace_id(
                            f"{new_dir}/{ext()}", int(user_id)
                        ),
                        do_nothing,
                    ),
                )
                # hexedit.replace_id(f"{new_dir}/ER0000.sl2", int(id))

            pop_up_win.destroy()

    pop_up_win = Toplevel(root)
    pop_up_win.title("Import")
    # pop_up_win.geometry("200x70")
    lab = Label(pop_up_win, text="Enter a Name:")
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


def god_mode_menu():
    def run_cheat():
        char = c_vars.get()  # "1. charname"
        if char == "Character" or char == "":
            popup(
                "Character not selected",
                parent_window=pop_up_win,
                root_element=root,
            )
            return

        if char.split(".")[1] == " ":
            popup(
                "Can't write to empty slot.\nGo in-game and create a "
                "character to overwrite.",
                parent_window=pop_up_win,
            )
            return

        name = fetch_listbox_entry(lb1)[0]  # Save file name. EX: main
        if len(name) < 1:
            popup(text="Slot not selected", parent_window=pop_up_win)
            return

        dest_file = f"{save_dir}{name}/{ext()}"
        char_ind = int(char.split(".")[0])

        archive_file(
            dest_file,
            name,
            "ACTION: CHEAT GOD-MODE",
            get_char_names_from_file(dest_file),
        )
        try:
            hexedit.set_attributes(
                dest_file, char_ind, [99, 99, 99], cheat=True
            )
            popup("Success!", parent_window=pop_up_win)
        except Exception:
            # traceback.print_exc()
            # str_err = "".join(traceback.format_exc())
            # popup(str_err, parent_window=pop_up_win)
            popup(
                "Unable to acquire stats/level.\nYour character level may be "
                "incorrect.\nFix now?",
                functions=(
                    lambda: fix_stats_menu(dest_file, char_ind),
                    lambda: pop_up_win.destroy(),
                ),
                buttons=True,
                button_names=("Yes", "No"),
                parent_window=pop_up_win,
            )

    pop_up_win = Toplevel(root)
    pop_up_win.title("God Mode")
    pop_up_win.resizable(width=True, height=True)
    pop_up_win.geometry("510x470")

    x = root.winfo_x()
    y = root.winfo_y()
    pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))

    main_label = Label(
        pop_up_win,
        text="DO NOT use this feature online! You will most certainly get "
        "banned.\n\nThis will set your HP,ST,FP to 60,000\n\n Note: Your "
        "stats will return to normal after leveling up or equipping a "
        "stat boosting item. \n\nNote: Remove any stat boosting gear "
        "from your character before doing this or it won't work.\n\n",
    )
    main_label.pack()

    # MAIN SAVE FILE LISTBOX
    lb1 = Listbox(
        pop_up_win, borderwidth=3, width=15, height=10, exportselection=0
    )
    lb1.config(font=bolded)
    lb1.pack()
    load_listbox(lb1)

    but_select1 = Button(
        pop_up_win,
        text="Select",
        command=lambda: get_char_names(lb1, dropdown1, c_vars),
    )
    but_select1.pack()

    # CHARACTER DROPDOWN MENU
    opts = [""]
    c_vars = StringVar(pop_up_win)
    c_vars.set("Character")
    dropdown1 = OptionMenu(pop_up_win, c_vars, *opts)
    dropdown1.pack()

    # SELECT LISTBOX ITEM BUTTON
    but_set = Button(pop_up_win, text="Set", command=run_cheat)
    but_set.config(font=bolded)
    but_set.pack()


def fix_stats_menu(dest_file, char_ind):
    def validate(P):
        if len(P) == 0:
            return True
        elif len(P) < 3 and P.isdigit() and int(P) > 0:
            return True
        else:
            # Anything else, reject it
            return False

    def fix():
        for entry in entries:
            if len(entry.get()) < 1:
                popup(
                    "Not all stats entered!",
                    root_element=root,
                    parent_window=pop_up_win,
                )
                return

        stat_lst = [int(i.get()) for i in entries]

        name = dest_file.split("/")[-2]
        print(f"DEST: {dest_file}   ==  char_ind {char_ind} ---   {stat_lst}")
        archive_file(
            dest_file,
            name,
            "ACTION: Fix Level",
            get_char_names_from_file(dest_file),
        )
        x = hexedit.fix_stats(dest_file, char_ind, stat_lst)
        if x is True:
            popup(
                "Successfully found stats and patched level!",
                parent_window=pop_up_win,
            )
        elif x is False:
            popup(
                "Unable to find stats, ensure you entered your stats "
                "correctly.\nMake sure your stats aren't boosted by an item.",
                root_element=root,
                parent_window=pop_up_win,
            )
            return

    # Main GUI content STAT
    pop_up_win = Toplevel(root)
    pop_up_win.title("Fix Level")
    pop_up_win.resizable(width=True, height=True)
    pop_up_win.geometry("580x550")
    vcmd = (pop_up_win.register(validate), "%P")
    bolded_font = FNT.Font(weight="bold")  # will use the default font
    x = root.winfo_x()
    y = root.winfo_y()
    pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))

    main_label = Label(
        pop_up_win,
        text="Enter your character stats.\n\nGo in-game and remove any stat "
        "boosting gear and take note of your stats and enter them here:",
    )
    main_label.grid(row=0, column=0, padx=(20, 0), pady=(5, 0), sticky="n")

    # VIGOR
    vig_lab = Label(pop_up_win, text="VIGOR:")
    vig_lab.config(font=bolded_font)
    vig_lab.grid(row=0, column=0, padx=(20, 0), pady=(75, 0), sticky="n")

    vig_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    vig_ent.grid(row=0, column=0, padx=(120, 0), pady=(75, 0), sticky="n")

    # MIND
    min_lab = Label(pop_up_win, text="MIND:")
    min_lab.config(font=bolded_font)
    min_lab.grid(row=0, column=0, padx=(20, 0), pady=(115, 0), sticky="n")

    min_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    min_ent.grid(row=0, column=0, padx=(120, 0), pady=(115, 0), sticky="n")

    # ENDURANCE
    end_lab = Label(pop_up_win, text="END:")
    end_lab.config(font=bolded_font)
    end_lab.grid(row=0, column=0, padx=(20, 0), pady=(155, 0), sticky="n")

    end_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    end_ent.grid(row=0, column=0, padx=(120, 0), pady=(155, 0), sticky="n")

    # STRENGTH
    str_lab = Label(pop_up_win, text="STR:")
    str_lab.config(font=bolded_font)
    str_lab.grid(row=0, column=0, padx=(20, 0), pady=(195, 0), sticky="n")

    str_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    str_ent.grid(row=0, column=0, padx=(120, 0), pady=(195, 0), sticky="n")

    # DEXTERITY
    dex_lab = Label(pop_up_win, text="DEX:")
    dex_lab.config(font=bolded_font)
    dex_lab.grid(row=0, column=0, padx=(20, 0), pady=(235, 0), sticky="n")

    dex_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    dex_ent.grid(row=0, column=0, padx=(120, 0), pady=(235, 0), sticky="n")

    # INTELLIGENCE
    int_lab = Label(pop_up_win, text="INT:")
    int_lab.config(font=bolded_font)
    int_lab.grid(row=0, column=0, padx=(20, 0), pady=(275, 0), sticky="n")

    int_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    int_ent.grid(row=0, column=0, padx=(120, 0), pady=(275, 0), sticky="n")

    # FAITH
    fai_lab = Label(pop_up_win, text="FAITH:")
    fai_lab.config(font=bolded_font)
    fai_lab.grid(row=0, column=0, padx=(20, 0), pady=(315, 0), sticky="n")

    fai_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    fai_ent.grid(row=0, column=0, padx=(120, 0), pady=(315, 0), sticky="n")

    # ARCANE
    arc_lab = Label(pop_up_win, text="ARC:")
    arc_lab.config(font=bolded_font)
    arc_lab.grid(row=0, column=0, padx=(20, 0), pady=(355, 0), sticky="n")

    arc_ent = Entry(
        pop_up_win, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    arc_ent.grid(row=0, column=0, padx=(120, 0), pady=(355, 0), sticky="n")

    # lIST OF ALL ENTRIES
    entries = [
        vig_ent,
        min_ent,
        end_ent,
        str_ent,
        dex_ent,
        int_ent,
        fai_ent,
        arc_ent,
    ]

    # SET STATS BUTTON
    but_set_stats = Button(pop_up_win, text="Fix", width=12, command=fix)
    but_set_stats.config(font=bolded_font)
    but_set_stats.grid(row=0, column=0, padx=(25, 0), pady=(420, 0), sticky="n")


def set_runes_menu():
    def validate(P):

        if P.isdigit():
            return True
        else:
            return False

    def set_rune_count():
        old_quantity = old_q_ent.get()
        new_quantity = new_q_ent.get()

        char = c_vars.get()  # "1. charname"
        if char == "Character" or char == "":
            popup("Character not selected", parent_window=pop_up_win)
            return

        if char.split(".")[1] == " ":
            popup(
                "Can't write to empty slot.\nGo in-game and create a "
                "character to overwrite.",
                parent_window=pop_up_win,
            )
            return

        name = fetch_listbox_entry(lb1)[0]  # Save file name. EX: main
        if len(name) < 1:
            popup(text="Slot not selected", parent_window=pop_up_win)
            return

        dest_file = f"{save_dir}{name}/{ext()}"
        char_ind = int(char.split(".")[0])

        if old_quantity == "" or new_quantity == "":
            popup(
                text="Enter a rune quantity",
                root_element=root,
                parent_window=pop_up_win,
            )
            return

        if int(old_quantity) < 1000 or int(new_quantity) < 1000:
            popup(
                text="Rune count is too low! Enter a value greater than 1000",
                root_element=root,
                parent_window=pop_up_win,
            )
            return
        if int(new_quantity) > 999999999:  # Max quantity in-game
            new_quantity = 999999999

        archive_file(
            dest_file,
            fetch_listbox_entry(lb1)[0],
            "ACTION: Set rune count",
            get_char_names_from_file(dest_file),
        )
        out = hexedit.set_runes(
            dest_file, char_ind, int(old_quantity), int(new_quantity)
        )
        if out is False:
            popup(
                "Unable to find rune count!\nMake sure you have a larger "
                "value with the number being fairly random. Ex: 85732",
                root_element=root,
                parent_window=pop_up_win,
            )
            return
        else:
            popup(
                f"Successfully set rune count to {new_quantity}",
                root_element=root,
                parent_window=pop_up_win,
            )

    pop_up_win = Toplevel(root)
    pop_up_win.title("Set Rune Count")
    pop_up_win.resizable(width=True, height=True)
    pop_up_win.geometry("510x590")

    x = root.winfo_x()
    y = root.winfo_y()
    pop_up_win.geometry("+%d+%d" % (x + 200, y + 200))
    vcmd = (pop_up_win.register(validate), "%P")

    main_label = Label(
        pop_up_win,
        text="Go in-game and take note of how many held runes the character "
        "has.\nBigger numbers ensure the program finds the proper "
        "location of your runes.\n",
    )
    main_label.pack()

    # MAIN SAVE FILE LISTBOX
    lb1 = Listbox(
        pop_up_win, borderwidth=3, width=15, height=10, exportselection=0
    )
    lb1.config(font=bolded)

    lb1.pack()
    load_listbox(lb1)

    but_select1 = Button(
        pop_up_win,
        text="Select",
        command=lambda: get_char_names(lb1, dropdown1, c_vars),
    )
    but_select1.pack()

    # CHARACTER DROPDOWN MENU
    opts = [""]
    c_vars = StringVar(pop_up_win)
    c_vars.set("Character")
    dropdown1 = OptionMenu(pop_up_win, c_vars, *opts)
    dropdown1.pack()

    padding_lab1 = Label(pop_up_win, text="\n\n")
    padding_lab1.pack()

    # OLD QUANTITY LABEL
    old_q_label = Label(pop_up_win, text="Enter Current rune count:")
    old_q_label.pack()

    # OLD QUANTITY ENTRY
    old_q_ent = Entry(
        pop_up_win, borderwidth=5, validate="key", validatecommand=vcmd
    )
    old_q_ent.pack()

    # NEW QUANTITY LABEL
    new_q_label = Label(pop_up_win, text="Enter new rune count:")
    new_q_label.pack()

    # NEW QUANTITY ENTRY
    new_q_ent = Entry(
        pop_up_win, borderwidth=5, validate="key", validatecommand=vcmd
    )
    new_q_ent.pack()

    padding_lab3 = Label(pop_up_win, text="\n\n")
    padding_lab3.pack()

    # SET BUTTON
    but_set = Button(pop_up_win, text="Set", command=set_rune_count)
    but_set.config(font=bolded)
    but_set.pack()
