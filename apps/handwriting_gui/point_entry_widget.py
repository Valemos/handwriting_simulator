import tkinter as tk

from gui import EntryIntegerWithLabel
from handwriting.path.curve.point import Point


class PointEntry(tk.Frame):
    def __init__(self, root, grid_width):
        tk.Frame.__init__(self, root)

        self.entry_shift_x = EntryIntegerWithLabel(self, "X:", grid_width, 1 / 5)
        self.entry_shift_y = EntryIntegerWithLabel(self, "Y:", grid_width, 1 / 5)
        self.entry_shift_x.pack(side="left")
        self.entry_shift_y.pack(side="left")

    def set(self, point: Point):
        self.entry_shift_x.set(point.x)
        self.entry_shift_y.set(point.y)

    def get_point(self):
        return Point(self.entry_shift_x.get(), self.entry_shift_y.get())
