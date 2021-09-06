from handwriting.page_writing.button_handler_group import ArrowButtonsHandler


class AnchorPointHandlers(ArrowButtonsHandler):

    @staticmethod
    def left(app):
        if app.page_drawer.anchor_manager is not None:
            app.page_drawer.anchor_manager.move_left()
            app.update_anchor_indices()

    @staticmethod
    def right(app):
        if app.page_drawer.anchor_manager is not None:
            app.page_drawer.anchor_manager.move_right()
            app.update_anchor_indices()

    @staticmethod
    def up(app):
        if app.page_drawer.anchor_manager is not None:
            app.page_drawer.anchor_manager.move_up()
            app.update_anchor_indices()

    @staticmethod
    def down(app):
        if app.page_drawer.anchor_manager is not None:
            app.page_drawer.anchor_manager.move_down()
            app.update_anchor_indices()
