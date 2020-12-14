from handwriting.page_writing.button_handler_group import ButtonHandlerGroup

class PageButtonHandlers(ButtonHandlerGroup):

    @staticmethod
    def left(app):
        app.handle_prev_page()

    @staticmethod
    def right(app):
        app.handle_next_page()

    @staticmethod
    def up(app):
        pass

    @staticmethod
    def down(app):
        pass
