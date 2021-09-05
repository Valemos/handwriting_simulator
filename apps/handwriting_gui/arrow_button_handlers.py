from handwriting.page_writing.button_handler_group import ButtonHandlerGroup


class ArrowButtonHandlers:

    def __init__(self):
        self.arrow_handlers: ButtonHandlerGroup = None

    def handle_button_left(self, event=None):
        self.arrow_handlers.left(self)

    def handle_button_right(self, event=None):
        self.arrow_handlers.right(self)

    def handle_button_up(self, event=None):
        self.arrow_handlers.up(self)

    def handle_button_down(self, event=None):
        self.arrow_handlers.down(self)