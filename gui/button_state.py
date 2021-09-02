class ButtonState:
    def __init__(self, name, handler):
        self.name = name
        self.handler = handler

    def handle_state(self):
        self.handler()