from tkinter import Listbox

from src.app.views import root
from src.app.views.consts import bolded


def get_list_box(
    master,
    border_width: int = 3,
    width: int = 15,
    height: int = 10,
    export_selection: int = 0,
    grid: dict | None = None,
    config: dict | None = None,
):
    list_box = Listbox(
        master,
        borderwidth=border_width,
        width=width,
        height=height,
        exportselection=export_selection,
    )
    if grid:
        list_box.grid(**grid)
    if config:
        list_box.config(**config)
    return list_box


list_box_1 = get_list_box(
    master=root,
    grid={"row": 1, "column": 0, "padx": (70, 0), "pady": (0, 0)},
    config={"font": bolded},
)

list_box_2 = get_list_box(
    master=root,
    grid={"row": 1, "column": 1, "padx": (175, 0), "pady": (0, 0)},
    config={"font": bolded},
)
