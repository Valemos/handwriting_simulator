class ArrowButtonsHandler:
    """
    This class contains interface to multiple button handlers
    Allows to change handlers class to perform another group of tasks
    """

    def left(self):
        raise NotImplementedError

    def right(self):
        raise NotImplementedError

    def up(self):
        raise NotImplementedError

    def down(self):
        raise NotImplementedError
