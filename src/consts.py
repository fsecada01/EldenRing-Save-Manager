from tkinter import Entry, Listbox, Tk

from save_manager import Config

config = Config()
root = Tk()
cr_save_ent = Entry(root, borderwidth=5)
lb = Listbox(root, borderwidth=3, width=25, height=16)
