from pprint import pformat
from tkinter import Menu
from typing import Any

from src.logging import logger


class EldenMenu(Menu):
    def __init__(
        self,
        master=None,
        name: str | None = None,
        command_list_dict: list[dict[str, Any]] | None = None,
        cnf: dict | None = None,
        **kw,
    ):
        cnf = {} if not cnf else cnf
        # self.tk = master.tk
        Menu.__init__(self, master, cnf, **kw)
        if name:
            self._name = name

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
            try:
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
            except Exception as e:
                logger.debug(
                    f"Setting commands failed. See error message: "
                    f"{type(e), e, e.args}"
                )
        else:
            logger.info(
                "Command List dict object is empty. Please provide a "
                "list of commands dict objects to process."
            )


def get_elden_menu(master, command_list_dict, name):
    """
    A generator function to return the class instance of the `EldenMenu` object.
    Args:
        master:
        command_list_dict:
        name:

    Returns:

    """
    logger.info(pformat(f"{command_list_dict}, {name}"))
    return EldenMenu(
        master=master, command_list_dict=command_list_dict, name=name
    )
