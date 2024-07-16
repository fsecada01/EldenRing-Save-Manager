from src.app.controllers.character import CharSelectionController
from src.app.models.main import Model
from src.app.views.main import View


class Controller:
    def __init__(self, model: Model, view: View):
        self.view = view
        self.model = model
        self.char_selection_controller = CharSelectionController(
            self.model, self.view
        )
