from src.app.models.main import Model
from src.app.views.main import View


class BaseController:
    model: Model | None = None
    view: View | None = None
    frame_name: str | None = None

    def __init__(self):
        self.frame = self.get_frame()
        self._bind()

    def get_frame(self):
        return self.view.frames[self.frame_name]

    def _bind(self):
        pass
