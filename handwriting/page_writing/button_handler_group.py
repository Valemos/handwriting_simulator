class ButtonHandlerGroup:
    """
    This class contains interface to multiple button handlers
    Allows to change handlers class to perform another group of tasks
    """

    @staticmethod
    def left(app):
        raise NotImplementedError

    @staticmethod
    def right(app):
        raise NotImplementedError

    @staticmethod
    def up(app):
        raise NotImplementedError

    @staticmethod
    def down(app):
        raise NotImplementedError
