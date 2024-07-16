from tkinter import Button, OptionMenu, StringVar

from src.app.controllers.base import BaseController
from src.app.models.character import Character
from src.app.models.main import Model
from src.app.views import tool_menu
from src.app.views.character import CharacterView
from src.app.views.consts import bolded
from src.app.views.listbox import list_box_1, list_box_2
from src.app.views.main import View
from src.menu import get_char_names
from src.utils import load_listbox


class CharSelectionController(BaseController):
    model = Character
    view = CharacterView
    frame_name = "character_selection"

    def __init__(self, model: Model, view: View):
        super().__init__()
        self._bind()

    def _bind(self):
        self.frame.but_select1.configure(command=lambda: self._select_char())

    def _select_char(self):
        """
        Creates a pop-up window with from which a list of characters is
        presented. The user can select the character.py and proceed with the
        workflow.
        Returns:
        """
        pop_up_win = tool_menu
        pop_up_win.master = self.frame
        list(map(lambda lb: load_listbox(lb), (list_box_1, list_box_2)))
        opts = [""]
        opts2 = [""]
        vars1 = StringVar(pop_up_win)
        vars1.set("Character")

        vars2 = StringVar(pop_up_win)
        vars2.set("Character")

        dropdown_1 = OptionMenu(pop_up_win, vars1, *opts)
        dropdown_1.grid(row=4, column=0, padx=(70, 0), pady=(20, 0))

        dropdown_2 = OptionMenu(pop_up_win, vars2, *opts2)
        dropdown_2.grid(row=4, column=1, padx=(175, 0), pady=(20, 0))

        but_select1 = Button(
            pop_up_win,
            text="Select",
            command=lambda: get_char_names(list_box_1, dropdown_1, vars1),
        )
        but_select1.grid(row=3, column=0, padx=(70, 0), pady=(10, 0))

        but_select2 = Button(
            pop_up_win,
            text="Select",
            command=lambda: get_char_names(list_box_2, dropdown_2, vars2),
        )
        but_select2.grid(row=3, column=1, padx=(175, 0), pady=(10, 0))

        but_copy = Button(pop_up_win, text="Copy", command=self._do_copy)
        but_copy.config(font=bolded)
        but_copy.grid(row=5, column=1, padx=(175, 0), pady=(50, 0))

        but_cancel = Button(
            pop_up_win, text="Cancel", command=lambda: pop_up_win.destroy()
        )
        but_cancel.config(font=bolded)
        but_cancel.grid(row=5, column=0, padx=(70, 0), pady=(50, 0))
