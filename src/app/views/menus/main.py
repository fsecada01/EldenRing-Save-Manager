import webbrowser
from tkinter import Menu

from src.app.consts import lb
from src.app.views.menus.menu import EldenMenu, get_elden_menu
from src.app.views.root import root
from src.app.views.utils import load_backup
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
from src.os_layer import video_url
from src.utils import (
    change_default_dir,
    changelog,
    force_quit,
    open_folder,
    open_game_save_dir,
    popup,
    rename_slot,
    update_app,
    update_slot,
)

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
right_click_menu_dict_list = [
    {
        "label": "Rename Save",
        "command": lambda: rename_slot(list_box=lb),
    },
    {
        "label": "Rename Characters",
        "command": rename_characters_menu,
    },
    {
        "label": "Update",
        "command": lambda: update_slot(list_box=lb, root_element=root),
    },
    {
        "label": "Change SteamID",
        "command": set_steam_id_menu,
    },
    {
        "label": "Open File Location",
        "command": lambda: open_folder(list_box=lb, root_element=root),
    },
]
rt_click_menu = EldenMenu(
    lb,
    name="Right Click Menu",
    command_list_dict=right_click_menu_dict_list,
    tearoff=0,
)

file_menu, edit_menu, tool_menu, cheat_menu, help_menu = list(
    map(
        lambda args: get_elden_menu(
            master=root, command_list_dict=args[0], name=args[1]
        ),
        [
            (file_menu_dict_list[:4], "File"),
            (edit_menu_dict_list, "Edit"),
            (tool_menu_dict_list, "Tool"),
            (cheat_menu_dict_list, "Cheat"),
            (help_menu_dict_list, "Help"),
        ],
    )
)

file_menu.set_commands(
    separator=True, command_list_dict=file_menu_dict_list[4:]
)
menubar = Menu(root)

for name, menu in [
    ("File", file_menu),
    ("Edit", edit_menu),
    ("Tool", tool_menu),
    ("Cheat", cheat_menu),
    ("Help", help_menu),
]:
    menubar.add_cascade(label=name, menu=menu)
