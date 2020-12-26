import tkinter as tk

from handwriting.gui_parts.entry_with_label import EntryWithLabel


class EntryIntegerWithLabel(EntryWithLabel):

    def __init__(self, root, label, width, label_width_ratio):
        super().__init__(root, label, width, label_width_ratio)

    @staticmethod
    def str_is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @classmethod
    def update_integer_field(cls, field):
        if not cls.str_is_int(field.get()):
            field.set(str(int('0' + ''.join((i for i in field.get() if i.isdigit())))))

    def get(self):
        self.update_integer_field(self.str_variable)
        return int(self.str_variable.get())

    def set(self, value: int):
        self.str_variable.set(str(value))