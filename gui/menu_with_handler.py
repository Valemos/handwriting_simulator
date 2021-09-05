import tkinter as tk


class MenuWithHandler(tk.OptionMenu):

    default_choice = "-"

    def __init__(self, root, width, handler):
        self.variable_menu = tk.StringVar(root)
        tk.OptionMenu.__init__(self, root, self.variable_menu, None)
        self.configure(width=width)

        if not callable(handler):
            raise ValueError("menu must have choice function handler")

        self.choice_handler = handler

    def update_choices(self, new_choices: list):
        """
        Values in dict_manager will be passed to handler function
        """

        self['menu'].delete(0, 'end')  # delete all elements from menu

        if new_choices is None:
            self.variable_menu.set(self.default_choice)
            return

        for index, name in enumerate(new_choices):
            self['menu'].add_command(
                label=name,
                command=lambda i=index: self.choice_handler(i))

    def set(self, group_name):
        self.variable_menu.set(group_name if group_name is not None and group_name != "" else self.default_choice)
