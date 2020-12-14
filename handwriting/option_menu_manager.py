
class OptionMenuManager:

    @staticmethod
    def set_menu_choices(menu, choices: dict, handler):
        """
        this function is used to set choices dictionary to tkinter.OptionMenu and apply handler to them
        if choices is None, deletes all options in path and returns
        :param menu: OptionMenu object
        :param choices: dictionary with name and value for choice function
        :param handler: handler function for all chosen canvas_objects
        """
        menu['menu'].delete(0, 'end')  # delete all elements from menu

        if choices is None:
            return

        for choice_name, choice_object in choices.items():
            menu['menu'].add_command(
                label=choice_name,
                command=lambda c=choice_object: handler(c))
