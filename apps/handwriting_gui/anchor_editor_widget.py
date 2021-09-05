import tkinter as tk
from tkinter import messagebox

from gui import ButtonTwoStates, EntryIntegerWithLabel
from gui.button_state import ButtonState
from handwriting.misc.exceptions import ObjectNotFound


class AnchorEditorWidget(tk.Frame):
    def __init__(self, root, grid_width):
        tk.Frame.__init__(self, root)
        self.parent = root

        self._continue_point_redraw = None
        self._mouse_position = None

        # TODO pack all widgets
        self.button_edit_anchors = ButtonTwoStates(
            self, grid_width,
            ButtonState("Edit anchors", self.enable_edit_anchor_points),
            ButtonState("Stop edit anchors", self.disable_edit_anchor_points)
        )

        self.format_anchor_index = "line: {0:<3} point: {1:<3}"
        self.var_anchor_indices = tk.StringVar(self)
        label_anchor_index = tk.Label(self, textvariable=self.var_anchor_indices, width=grid_width)
        self.update_anchor_indices()

        self.entry_lines_count = EntryIntegerWithLabel(self, "Lines:", grid_width, 1 / 3)
        self.entry_lines_count.set(0)

        label_create_lines = tk.Label(self, text="Create more lines:")

        self.btn_create_lines = tk.Button(self, text="Create lines", width=grid_width,
                                          command=self.handle_create_more_lines)
        self.btn_create_lines.config(state=tk.DISABLED)

    def enable_edit_anchor_points(self):
        self.btn_create_lines.config(state=tk.NORMAL)
        self.select_anchor_point_handlers()
        self.page_iterator.start_anchor_editing(self.canvas)
        self.update_anchor_indices()

    def disable_edit_anchor_points(self):
        self.btn_create_lines.config(state=tk.DISABLED)
        self.select_page_switch_handlers()
        self.page_iterator.stop_anchor_editing()
        self.update_anchor_indices()

    def handle_create_more_lines(self, event=None):
        """
        Creates multiple lines from first two rows of anchor points
        Using value from entry, creates N intermediate points with equal intervals between adjacent points

        To make this function work properly, user must create the same number of points in both lines
        Otherwise, lines below will be skewed
        """

        if self.page_iterator.page_exists():
            lines_num = int(self.entry_lines_count.get())
            if lines_num > 0:
                if not self.page_iterator.anchor_manager.add_intermediate_lines(0, 1, lines_num):
                    messagebox.showinfo("Error", "Cannot create intermediate lines\nfrom first two lines")

    def constant_redraw_last_anchor(self, point):
        if self.page_iterator.is_started_anchor_editing():
            self.page_iterator.anchor_manager.redraw_pointer_point(point)

        if self._continue_point_redraw:
            self.root.after(17, self.constant_redraw_last_anchor, self.mouse_position)

    def update_anchor_indices(self):
        try:
            indices = self.page_iterator.get_anchor_indices()
        except ObjectNotFound:
            indices = ("-", "-")

        anchor_indices_string = self.format_anchor_index.format(*indices)
        self.var_anchor_indices.set(anchor_indices_string)

    def set_mouse_position(self, point):
        self._mouse_position = point
