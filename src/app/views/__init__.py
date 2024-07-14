from tkinter import Menu

from .menu import cheat_menu, edit_menu, file_menu, help_menu, root, tool_menu

menubar = Menu(root)

for name, menu in [
    ("File", file_menu),
    ("Edit", edit_menu),
    ("Tool", tool_menu),
    ("Cheat", cheat_menu),
    ("Help", help_menu),
]:
    menubar.add_cascade(label=name, menu=menu)
