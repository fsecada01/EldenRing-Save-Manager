from tkinter.ttk import Frame
from typing import Type

from src.app.views.home import HomeView
from src.app.views.root import root


class View:
    def __init__(self):
        self.root = root
        self.frames = {}

        self._add_frame(HomeView, "home")

    def _add_frame(self, frame: Type[Frame], name: str):
        """
        Add a frame to the application. We use key-assignments to the dict
        object to ensure that we can set the grid position of the frame.
        Args:
            frame: Type[Frame]:
            name: str

        Returns:
            None
        """

        self.frames[name] = frame(self.root)
        self.frames[name].grid(row=0, column=0, sticky="nsew")

    def switch(self, name: str):
        """
        Switch frames based on the frame name value.
        Args:
            name: str

        Returns:
            None
        """
        frame = self.frames[name]
        frame.tkraise()

    def start_mainloop(self):
        self.root.mainloop()
