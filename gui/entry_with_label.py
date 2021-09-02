import tkinter as tk


class EntryWithLabel(tk.Frame):

    def __init__(self, root, label, width, label_width_ratio):
        super().__init__(root)

        label_obj = tk.Label(self, text=label,
                             width=round(width * label_width_ratio))
        self.str_variable = tk.StringVar(self)
        self.entry = tk.Entry(self, textvariable=self.str_variable,
                              width=round(width * (1 - label_width_ratio)))
        label_obj.pack(side=tk.LEFT)
        self.entry.pack(side=tk.RIGHT)

    def get(self):
        return self.str_variable.get()

    def set(self, new_content):
        self.str_variable.set(new_content)
