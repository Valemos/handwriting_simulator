import tkinter as tk


class MenuWithHandler(tk.OptionMenu):

    default_choice = "-"

    def __init__(self, root, width, handler):
        self.variable_menu = tk.StringVar(root)
        super().__init__(root, self.variable_menu, value=None)
        self.configure(width=width)

        if not callable(handler):
            raise ValueError("menu must have choice function handler")

        self.choice_handler = handler

    def update_choices(self, new_choices: dict):
        """
        Values in dict_manager will be passed to handler function
        """

        self['menu'].delete(0, 'end')  # delete all elements from menu

        if new_choices is None:
            self.variable_menu.set(self.default_choice)
            return

        for choice_name, choice_object in new_choices.items():
            self['menu'].add_command(
                label=choice_name,
                command=lambda c=choice_object: self.choice_handler(c))

    def set(self, group_name):
        self.variable_menu.set(group_name if group_name is not None else self.default_choice)