import tkinter as tk

from handwriting.gui_parts.menu_choices_with_handler import MenuChoicesWithHandler


class MenuIndexedChoicesWithHandler(MenuChoicesWithHandler):

    def __init__(self, root, width, handler):
        super().__init__(root, width, handler)

    @staticmethod
    def indexed_name(name):
        pass

    def update_choices(self, new_choices: dict):
        if new_choices is not None:
            new_choices = {self.indexed_name(name): value for name, value in new_choices.items()}

        super().update_choices(new_choices)