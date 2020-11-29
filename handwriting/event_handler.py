from abc import ABC


class EventManager(ABC):
    """
    Implementing this class allows to organize binding key handling to some specific objects
    To use this interface, user must implement function, returning dictionary with handler functions
    """

    def create_events_dict(self):
        """
        this function must be called after all GUI objects was created

        dictionary with keys as events and handler functions as values
        format as follows <modifier-type-first_part>, handler at the end of the chain

        handler MUST be a tuple of Tkinter object and function to bind to corresponding event
        """
        raise NotImplementedError

    @staticmethod
    def bind_handlers(handler, first_part=None, second_part=None):
        """
        Recursively takes dictionary of dictionaries of tuples
        and combines them to bind tkinter event functions to objects

        :param handler: object to iterate through
        :param first_part: the first part of command
        :param second_part: the second part of command
        :return:
        """
        if isinstance(handler, dict):
            for part, func in handler.items():
                if first_part is None:
                    EventManager.bind_handlers(func, part)
                else:
                    EventManager.bind_handlers(func, first_part, part)
            return

        if isinstance(handler, list):
            for func in handler:
                EventManager.bind_handlers(func, first_part, second_part)
            return

        if isinstance(handler, tuple):
            bind_object, handler = handler
            bind_object.bind(f"<{first_part}>"
                             if second_part is None else
                             f"<{first_part}-{second_part}>",
                             handler)
        else:
            raise ValueError("handler is not a tuple of object and function")

