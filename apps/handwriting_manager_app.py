import tkinter as tk
from tkinter import messagebox

from gui.canvas_display import CanvasDisplay
from gui.event_bind_manager import EventBindManager
from gui.widget_positioning import *
from handwriting.path.curve.point import Point
from handwriting.path.path_drawer import PathDrawer
from handwriting.paths_dictionary.dictionary_manager import DictionaryManager
from handwriting_gui.dictionary_editor_widget import DictionaryEditorWidget
from handwriting_gui.dictionary_opener_widget import DictionaryOpenerWidget
from handwriting_gui.path_cursor_widget import PathCursorWidget
from handwriting_gui.point_entry_widget import PointEntry

# testing
import threading
import time


class HandwritingShiftModifier(tk.Frame, EventBindManager):

    message_warning_cannot_draw = "You cannot draw path without group. Create new group and path using " \
                                  "entries \"Group\" and \"Variant\" and press button \"New path\" " \
                                  "or press \"Space\" on keyboard"

    def __init__(self, root):
        super().__init__(self, root)
        self.parent = root
        self.parent.title("Handwriting manager")

        self._mouse_released = True
        grid_width = 15

        # dict_manager of path groups with default value
        self.dictionary_manager = DictionaryManager()

        self.canvas = tk.Canvas(root, width=500, height=450, bg="white")
        display = CanvasDisplay(self.canvas)
        self.path_drawer = PathDrawer(self.dictionary_manager, display)

        self.point_entry = PointEntry(root, grid_width)
        self.point_entry.set(Point(100, 100))

        self.path_drawer.set_global_shift(self.point_entry.get_point())

        self.path_cursor = PathCursorWidget(root, grid_width, self.path_drawer)
        self.path_cursor.update_menu_labels()

        self.dictionary_opener = DictionaryOpenerWidget(root,
                                                        grid_width,
                                                        self.dictionary_manager,
                                                        self.path_drawer.redraw,
                                                        self.path_cursor.update_menus)

        self.dictionary_editor = DictionaryEditorWidget(root,
                                                        grid_width,
                                                        self.dictionary_manager,
                                                        self.path_cursor.update_menus,
                                                        self.path_drawer.redraw)

        put_objects_on_grid([
            [tk.Label(root, text="Base shift: "), self.point_entry],
            [self.dictionary_opener],
            [self.path_cursor],
            [self.dictionary_editor],
            [self.canvas],
        ])

        self.bind_handlers(self.create_events_dict())

    @staticmethod
    def main():
        root = tk.Tk()
        app = HandwritingShiftModifier(root)
        app.wait_visibility()
        app.test_init()
        root.mainloop()

    def test_init(self):
        from handwriting.paths_dictionary.signature_dictionary import SignatureDictionary
        self.dictionary_opener.entry_dict_path.set(SignatureDictionary.default_path)
        self.dictionary_opener.open_from_entry_path()
        self.path_cursor.update_menus()

    def create_events_dict(self):
        return \
            {
                "B1": {
                    "ButtonRelease": (self.canvas, self.handle_mouse_release),
                    "Motion": (self.canvas, self.handle_motion_draw)
                },
                "KeyPress": {
                    "Left": (self.parent, self.path_cursor.handle_prev_letter),
                    "Right": (self.parent, self.path_cursor.handle_next_letter),
                    "Return": [
                        (self.point_entry.entry_shift_x, self.handle_draw_path),
                        (self.point_entry.entry_shift_y, self.handle_draw_path),
                    ],
                    "Delete": (self.parent, self.dictionary_editor.handle_delete_path),
                    "space": (self.parent, self.dictionary_editor.handle_create_path)
                }
            }

    def handle_motion_draw(self, event):
        if self.path_drawer.try_draw():
            if self._mouse_released:
                self._mouse_released = False
                self.path_drawer.start_curve(Point(event.x, event.y))
            else:
                self.path_drawer.continue_curve(Point(event.x, event.y))
        else:
            messagebox.showinfo("Warning", self.message_warning_cannot_draw)

    def handle_mouse_release(self, event):
        self._mouse_released = True

    def redraw_current_path(self):
        self.path_drawer.set_global_shift(self.point_entry.get_point())
        self.path_drawer.redraw()

    def handle_draw_path(self, event):
        self.redraw_current_path()
        self.parent.focus()


if __name__ == "__main__":
    HandwritingShiftModifier.main()
