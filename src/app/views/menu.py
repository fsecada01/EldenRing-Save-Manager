from tkinter import Menu
from tkinter.ttk import Button, Frame, Label
from typing import Any

from src.logging import logger


class EldenMenu(Menu):
    def __init__(
        self,
        master,
        command_list_dict: list[dict[str, Any]] | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(self, master, *args, **kwargs)
        self.master = master

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
