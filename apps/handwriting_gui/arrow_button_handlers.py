from handwriting.page_writing.button_handler_group import ArrowButtonsHandler


class ArrowButtonHandlers:

    def __init__(self):
        self.arrows_handler: ArrowButtonsHandler = None

    def handle_button_left(self, event=None):
        self.arrows_handler.left(self)

    def handle_button_right(self, event=None):
        self.arrows_handler.right(self)

    def handle_button_up(self, event=None):
        self.arrows_handler.up(self)

    def handle_button_down(self, event=None):
        self.arrows_handler.down(self)