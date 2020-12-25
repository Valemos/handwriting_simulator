import tkinter as tk

class EntryIntegerWithLabel(tk.Frame):

    def __init__(self, root, label, width):
        super().__init__(root)
        self.root = root
        label = tk.Label(self, text=label, width=round(width / 5))
        self.str_variable = tk.StringVar(root)
        self.entry = tk.Entry(self, width=round(width * 4 / 5), textvariable=self.str_variable)
        label.pack(side=tk.LEFT)
        self.entry.pack(side=tk.RIGHT)

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