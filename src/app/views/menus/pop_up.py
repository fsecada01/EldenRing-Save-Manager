from tkinter import Menu, Toplevel

from src.app.views import root


class EldenToplevel(Toplevel):
    def __init__(
        self,
        master,
        title: str | None = None,
        geo_x_coord: int | None = None,
        geo_y_coord: int | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.master.bind("<Escape>", lambda event: self.destroy())
        self.master.bind("<FocusOut>", lambda event: self.destroy())
        self.master.bind("<FocusIn>", lambda event: self.focus_set())
        self.master.bind("<Return>", lambda event: self.destroy())
        self.master.bind("<KP_Enter>", lambda event: self.destroy())
        self.master.bind("<Button-1>", lambda event: self.destroy())
        self.master.bind("<ButtonRelease-1>", lambda event: self.destroy())
        self.master.bind("<ButtonPress-1>", lambda event: self.focus_set())
        self.master.bind("<ButtonPress-2>", lambda event: self.focus_set())
        self.master.bind("<ButtonPress-3>", lambda event: self.focus_set())
        self.master.bind("<ButtonPress-4>", lambda event: self.focus_set())

        if title:
            self.title(title)
        self.resizable(width=True, height=True)
        if not all((geo_x_coord, geo_y_coord)):
            x, y = [getattr(self, f"winfo_{x}")() for x in ("x", "y")]
        else:
            x, y = geo_x_coord, geo_y_coord
        # self.geometry('620x500')
        self.geometry(f"+{x + 200}+{y + 200}")


char_pop_up_win = EldenToplevel(master=root, title="Character Manager")
char_menu_bar = Menu(char_pop_up_win)
char_pop_up_win.config(menu=char_menu_bar)
