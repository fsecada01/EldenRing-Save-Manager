import webbrowser

from src.app.consts import lb
from src.app.views.base import BaseView
from src.app.views.root import root
from src.os_layer import video_url
from src.utils import change_default_dir, changelog, open_folder, update_app


class HomeView(BaseView):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, "Elden Ring Save Manager", *args, **kwargs)
        self.set_button("Change Default Directory", change_default_dir)
        self.set_button(
            "Open Folder", lambda: open_folder(list_box=lb, root_element=root)
        )
        self.set_button("Update", update_app)
        self.set_button("Changelog", changelog)
        self.set_button(
            "Open Video", lambda: webbrowser.open_new_tab(video_url)
        )
        self.set_button(
            "Open Steam",
            lambda: webbrowser.open_new_tab(
                "https://store.steampowered.com/app/1245620"
            ),
        )
        self.set_button(
            "View Source Code/Contribute!",
            lambda: webbrowser.open_new_tab(
                "https://github.com/vaalberith/EldenRing-Save-Manager"
            ),
        )
