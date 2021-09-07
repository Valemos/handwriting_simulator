from handwriting.page_writing.button_handler_group import ArrowButtonsHandler


class ArrowButtonHandlers:

    def __init__(self):
        self.arrows_handler: ArrowButtonsHandler = None

    def handle_button_left(self, event=None):
        self.arrows_handler.left()

    def handle_button_right(self, event=None):
        self.arrows_handler.right()

    def handle_button_up(self, event=None):
        self.arrows_handler.up()

    def handle_button_down(self, event=None):
        self.arrows_handler.down()
