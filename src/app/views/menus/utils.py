from tkinter import Button, Label, OptionMenu, StringVar

from src.app.views.consts import bolded
from src.app.views.listbox import list_box_1, list_box_2
from src.app.views.menus.main import help_menu_dict_list
from src.app.views.menus.menu import EldenMenu
from src.app.views.menus.pop_up import (
    EldenToplevel,
    char_menu_bar,
    char_pop_up_win,
)
from src.menu import get_char_names
from src.utils import load_listbox


def get_char_manager_menu():
    EldenMenu(char_menu_bar, command_list_dict=help_menu_dict_list)

    src_label = Label(char_pop_up_win, text="Source File")
    src_label.config(font=bolded)
    src_label.grid(row=0, column=0, padx=(70, 0), pady=(20, 0))

    list(map(lambda lb: load_listbox(lb), [list_box_1, list_box_2]))

    opts = [""]
    opts2 = [""]
    vars1 = StringVar(char_pop_up_win)
    vars1.set("Character")

    vars2 = StringVar(char_pop_up_win)
    vars2.set("Character")

    dropdown1 = OptionMenu(char_pop_up_win, vars1, *opts)
    dropdown1.grid(row=4, column=0, padx=(70, 0), pady=(20, 0))

    dropdown2 = OptionMenu(char_pop_up_win, vars2, *opts2)
    dropdown2.grid(row=4, column=1, padx=(175, 0), pady=(20, 0))

    but_select1 = Button(
        char_pop_up_win,
        text="Select",
        command=lambda: get_char_names(list_box_1, dropdown1, vars1),
    )
    but_select1.grid(row=3, column=0, padx=(70, 0), pady=(10, 0))

    but_select2 = Button(
        char_pop_up_win,
        text="Select",
        command=lambda: get_char_names(list_box_2, dropdown2, vars2),
    )
    but_select2.grid(row=3, column=1, padx=(175, 0), pady=(10, 0))

    def do_copy():
        """
        A function to copy the selected items from the source to the
        destination. Searches local string_var objects to determine source
        and destination locations

        Returns:

        """
        src_char = vars1.get()
        dest_char = vars2.get()
        key_val = "Character"
        if src_char == key_val or dest_char == key_val:
            win = EldenToplevel(char_pop_up_win, title="Manager")
            lab = Label(win, text="Select a character.py first")
            lab.grid(row=0, column=0, padx=15, pady=15, columspan=2)

    but_copy = Button(char_pop_up_win, text="Copy", command=do_copy)
    but_copy.config(font=bolded)
    but_copy.grid(row=5, column=1, padx=(175, 0), pady=(50, 0))

    but_cancel = Button(
        char_pop_up_win, text="Cancel", command=lambda: char_pop_up_win.destroy
    )
    but_cancel.config(font=bolded)
    but_cancel.grid(row=5, column=0, padx=(70, 0), pady=(50, 0))
