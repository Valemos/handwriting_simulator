from handwriting.page_writing.button_handler_group import ButtonHandlerGroup

class AnchorPointsHandlers(ButtonHandlerGroup):

    @staticmethod
    def left(app):
        if app.pages_manager.anchor_manager is not None:
            app.pages_manager.anchor_manager.move_left()

    @staticmethod
    def right(app):
        if app.pages_manager.anchor_manager is not None:
            app.pages_manager.anchor_manager.move_right()

    @staticmethod
    def up(app):
        if app.pages_manager.anchor_manager is not None:
            app.pages_manager.anchor_manager.move_up()

    @staticmethod
    def down(app):
        if app.pages_manager.anchor_manager is not None:
            app.pages_manager.anchor_manager.move_down()