from handwriting.page_writing.button_handler_group import ButtonHandlerGroup

class AnchorPointsHandlers(ButtonHandlerGroup):

    @staticmethod
    def left(app):
        app.pages_manager.move_left()

    @staticmethod
    def right(app):
        app.pages_manager.move_right()

    @staticmethod
    def up(app):
        app.pages_manager.move_up()

    @staticmethod
    def down(app):
        app.pages_manager.move_down()