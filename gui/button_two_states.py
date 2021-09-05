import tkinter as tk

from gui.button_state import ButtonState

class ButtonTwoStates(tk.Frame):

    def __init__(self, root, width, state_on, state_off):
        tk.Frame.__init__(self, root)

        self.state_on: ButtonState = state_on
        self.state_off: ButtonState = state_off

        self.current_state = state_on

        self.var_button_name = tk.StringVar()
        self.var_button_name.set(self.current_state.name)
        self.button = tk.Button(self, textvariable=self.var_button_name, width=width,
                                command=self.switch_state)
        self.button.pack(fill=tk.BOTH)

    def switch_state(self):
        if self.current_state is self.state_on:
            self.current_state = self.state_off
        else:
            self.current_state = self.state_on

        self.var_button_name.set(self.current_state.name)
        self.current_state.handle_state()
