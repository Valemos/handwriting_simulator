import tkinter as tk


class LeftRightButtons(tk.Frame):

    def __init__(self, root, width, command_left, command_right):
        super().__init__(root)
        self.root = root
        self.button_left = tk.Button(self, text='<-', command=command_left, width=round(width / 2))
        self.button_right = tk.Button(self, text='->', command=command_right, width=round(width / 2))
        self.button_left.pack(side=tk.LEFT)
        self.button_right.pack(side=tk.RIGHT)