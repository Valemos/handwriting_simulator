import tkinter as tk

from handwriting.gui_parts.menu_with_handler import MenuWithHandler


class MenuIndexedWithHandler(MenuWithHandler):

    def __init__(self, root, width, handler):
        super().__init__(root, width, handler)

    @staticmethod
    def indexed_name(index, name):
        return f"{index}.{name}" if name != '' else f"{index}"

    def update_choices(self, new_choices: dict):
        if new_choices is not None:
            new_choices = {
                self.indexed_name(index, item[0]): item[1]
                for index, item in
                zip(range(1, len(new_choices) + 1), new_choices.items())
            }

        super().update_choices(new_choices)

    def set_indexed_name(self, index, group_name):
        super().set(self.indexed_name(index, group_name))