from tkinter import Label, PhotoImage, Tk

from PIL import Image, ImageTk

from src.logging import logger
from src.os_layer import (
    app_title,
    background_img,
    bk_p,
    force_close_process,
    icon_file,
    version,
)


class Root(Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{app_title} {version}")
        self.geometry("830x561")
        self.resizable(False, False)
        self.get_icon()
        self.protocol("WM_DELETE_WINDOW", force_close_process)
        # self.bind("<Escape>", lambda e: self.destroy())
        # self.bind("<Control-s>", lambda e: self.save())
        # self.bind("<Control-S>", lambda e: self.save())
        # self.bind("<Control-o>", lambda e: self.open())
        # self.bind("<Control-O>", lambda e: self.open())
        # self.bind("<Control-n>", lambda e: self.new())
        # self.bind("<Control-N>", lambda e: self.new())
        # self.bind("<Control-q>", lambda e: self.quit())
        # self.bind("<Control-Q>", lambda e: self.quit())
        # self.bind("<Control-r>", lambda e: self.recover())
        # self.bind("<Control-R>", lambda e: self.recover())
        self.set_background()

    def get_icon(self):
        try:
            self.iconbitmap(icon_file)
        except Exception as e:
            logger.info(f"Getting bitmap failed: {type(e), e, e.args}")
            logger.info(
                "Unix doesn't support .ico - setting the background as app icon"
            )
            self.iconphoto(True, PhotoImage(background_img))

    def set_background(self):
        bg_img = ImageTk.PhotoImage(image=Image.open(background_img))
        background = Label(self, image=bg_img)  # noqa
        background.place(x=bk_p[0], y=bk_p[1], relwidth=1, relheight=1)


root = Root()
