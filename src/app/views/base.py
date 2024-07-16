from tkinter.ttk import Button, Frame, Label


class BaseView(Frame):
    def __init__(self, parent, label_name: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
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
