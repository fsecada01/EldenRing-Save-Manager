from .base import ObservableModel


class Item(ObservableModel):
    def __init__(self):
        super().__init__()
        self.id = ""
        self.name = ""


class Save(ObservableModel):
    def __init__(self):
        super().__init__()
        self.name = ""
        self.items = []
        self.playtime = 0
        self.playtime_formatted = ""
        self.playtime_formatted_short = ""
        self.steam_id = ""

    def backup_save(self, save):
        self.trigger_event("backup_save", save)

    def restore_save(self, save):
        self.trigger_event("restore_save", save)

    def modify_save(self, save):
        self.trigger_event("modify_save", save)


class Inventory(ObservableModel):
    def __init__(self):
        super().__init__()
        self.items: list[Item] = []
        self.items_by_name = {}
        self.items_by_id = {}

    def add_item(self, item):
        self.trigger_event("add_item", item)

    def modify_item_count(self, item, new_value: int):
        self.trigger_event("modify_item_count", item, new_value=new_value)
