import webbrowser
from tkinter import Menu
from tkinter.ttk import Button, Frame, Label
from typing import Any

from src.app.views.root import root
from src.app.views.utils import load_backup
from src.logging import logger
from src.menu import (
    change_default_steamid_menu,
    char_manager_menu,
    god_mode_menu,
    import_save_menu,
    inventory_editor_menu,
    recovery_menu,
    seamless_coop_menu,
    set_runes_menu,
    stat_editor_menu,
)
from src.os_layer import video_url
from src.utils import (
    change_default_dir,
    changelog,
    force_quit,
    open_game_save_dir,
    popup,
    update_app,
)


class EldenMenu(Menu):
    def __init__(
        self,
        master,
        label: str,
        command_list_dict: list[dict[str, Any]] | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(self, master, *args, **kwargs)
        self.master = master
        self.label = label

        if command_list_dict is None:
            command_list_dict = []

        self.set_commands(command_list_dict=command_list_dict)

    def set_commands(
        self,
        command_list_dict: list[dict[str, Any]] | None = None,
        separator: bool = False,
    ):
        if separator:
            self.add_separator()
        if command_list_dict:
            list(
                map(
                    lambda menu_dict: self.add_command(
                        label=menu_dict["label"].split()[0].title(),
                        command=menu_dict["command"],
                    ),
                    command_list_dict,
                )
            )

            logger.info(
                f"Commands set for the following commands: "
                f"{[x.get('Label') for x in command_list_dict]}"
            )
        else:
            logger.info(
                "Command List dict object is empty. Please provide a "
                "list of commands dict objects to process."
            )


class View(Frame):
    def __init__(self, parent, label_name: str):
        super().__init__(parent)

        self.parent = parent
        self.label = Label(self, text=label_name)
        self.label.grid(row=1, column=0)
        self.controller = None
        self.button_count = 0
        self.label_count = 1

    def set_controller(self, controller):
        self.controller = controller

    def set_button(self, button_name: str, command):
        button = Button(self, text=button_name, command=command)
        button.grid(row=self.button_count + 1, column=0)
        setattr(self, f"{button_name.lower()}_button", button)
        self.button_count += 1

    def set_label(self, label_name: str):
        label = Label(self, text=label_name)
        label.grid(row=self.label_count + 1, column=0)
        setattr(self, f"{label_name.lower()}_label", label)
        self.label_count += 1


file_menu_dict_list = [
    {
        "label": "Import Save File",
        "command": import_save_menu,
    },
    {
        "label": "Seamless Co-op Mode",
        "command": seamless_coop_menu,
    },
    {
        "label": "Force Quit Elden Ring",
        "command": force_quit,
    },
    {
        "label": "Open Default Game Save Directory",
        "command": open_game_save_dir,
    },
    {
        "label": "Load Backup",
        "command": lambda: load_backup(),
    },
    {
        "label": "Donate",
        "command": lambda: webbrowser.open_new_tab(
            "https://www.paypal.com/donate/?hosted_button_id" "=H2X24U55NUJJW"
        ),
    },
    {
        "label": "Exit",
        "command": lambda: exit(),
    },
]

edit_menu_dict_list = [
    {
        "label": "Change Default Directory",
        "command": change_default_dir,
    },
    {
        "label": "Change Default SteamID",
        "command": change_default_steamid_menu,
    },
    {
        "label": "Check for updates",
        "command": update_app,
    },
]

tool_menu_dict_list = [
    {
        "label": "Character Manager",
        "command": char_manager_menu,
    },
    {
        "label": "Stat Editor",
        "command": stat_editor_menu,
    },
    {
        "label": "Inventory Editor",
        "command": inventory_editor_menu,
    },
    {
        "label": "File Recovery",
        "command": recovery_menu,
    },
]

cheat_menu_dict_list = [
    {
        "label": "God Mode",
        "command": god_mode_menu,
    },
    {
        "label": "Set Runes",
        "command": set_runes_menu,
    },
]

help_menu_dict_list = [
    {
        "label": "Watch Video",
        "command": lambda: webbrowser.open_new_tab(video_url),
    },
    {
        "label": "Changelog",
        "command": lambda: changelog(run=True),
    },
    {
        "label": "Report a Bug",
        "command": lambda: popup(
            "Please report any bugs you find on the GitHub page.\n"
            "https://github.com/EldenRingTeam/EldenRingSaveEditor"
            "/issues",
            root_element=root,
        ),
    },
]

file_menu, edit_menu, tool_menu, cheat_menu, help_menu = [
    EldenMenu(root, command_list_dict=menu_dict_list, label=label_name)
    for menu_dict_list, label_name in [
        (file_menu_dict_list[:4], "File"),
        (edit_menu_dict_list, "Edit"),
        (tool_menu_dict_list, "Tool"),
        (cheat_menu_dict_list, "Cheat"),
        (help_menu_dict_list, "Help"),
    ]
]
file_menu.set_commands(
    separator=True, command_list_dict=file_menu_dict_list[4:]
)
