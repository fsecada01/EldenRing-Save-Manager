from pathlib import Path
from tkinter import Entry, Listbox, Tk

BASE_DIR = (Path("__name__") / "..").resolve()

root = Tk()
cr_save_ent = Entry(root, borderwidth=5)
lb = Listbox(root, borderwidth=3, width=25, height=16)
