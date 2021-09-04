import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring

from PIL import ImageDraw
from PIL.ImageTk import PhotoImage

from gui.canvas_display import CanvasDisplay
from gui.event_bind_manager import EventBindManager
from gui.widget_positioning import put_objects_on_grid
from handwriting.page_writing.anchor_points_handlers import AnchorPointHandlers
from handwriting.page_writing.arrow_button_handlers import ArrowButtonHandlers
from handwriting.page_writing.button_handler_group import ButtonHandlerGroup
from handwriting.page_writing.handwritten_text_writer import PathTextWriter
from handwriting.page_writing.page import Page
from handwriting.page_writing.page_button_handlers import PageSwitchHandlers
from handwriting.page_writing.page_manager import PagesIterator
from handwriting.paths_dictionary.dictionary_manager import DictionaryManager
from handwriting.path.curve.point import Point
from handwriting_gui.anchor_editor_widget import AnchorEditorWidget
from handwriting_gui.dictionary_opener_widget import DictionaryOpenerWidget
from handwriting_gui.page_cursor_widget import PageCursorWidget
from handwriting_gui.page_opener_widget import PageOpenerWidget
from handwriting_gui.text_writer_widget import TextWriterWidget


class PageTextWriterApp(tk.Frame,
                        EventBindManager,
                        ArrowButtonHandlers):
    default_pages_directory = Path("../pages")

    def __init__(self, root):
        super().__init__(self, root)
        self.root = root
        self.root.title("Text writer")

        self.dictionary_manager = DictionaryManager()
        self.page_manager = PagesIterator()


        grid_width = 15
        self.ui_grid = tk.Frame(self)

        self.canvas = tk.Canvas(self, bg="white", width=Page.default_size[0], height=Page.default_size[1])
        self.display = CanvasDisplay(self.canvas)

        self.dictionary_opener = DictionaryOpenerWidget(self.ui_grid, grid_width, self.dictionary_manager)

        self.page_cursor = PageCursorWidget(self.ui_grid, grid_width, self.page_manager, self.display, lambda _: None)
        self.page_opener = PageOpenerWidget(self.ui_grid, grid_width, self.page_manager)
        self.anchor_editor = AnchorEditorWidget(self.ui_grid, grid_width)
        self.text_writer = TextWriterWidget(self.ui_grid, grid_width, self.page_manager)

        self.setup_ui()
        self.update_pages_menu()

        self.arrow_handlers: ButtonHandlerGroup = None
        self.select_page_switch_handlers()

    @staticmethod
    def main():
        root = tk.Tk()
        app = PageTextWriterApp(root)
        app.wait_visibility()
        app.initialize()
        app.handle_draw_text()
        root.mainloop()

    def initialize(self):
        self.text_writer.entry_draw_text.insert(tk.END, "тестовая")
        self.dictionary_opener.entry_dict_path.set(r"D:\coding\Python_codes\Handwriting_extractor_project\paths_format_transition\anton.dict")
        self.dictionary_opener.open_from_entry_path()
        # self.open_pages_directory(r"D:\coding\Python_codes\Handwriting_extractor_project\pages")
        self.handle_draw_text()

    def create_events_dict(self):
        return \
            {
                "Enter": (self.root, self.handle_canvas_enter),
                "Leave": (self.root, self.handle_canvas_leave),
                "ButtonRelease": {
                    "1": (self.canvas, self.handle_left_mouse_release),
                    "3": (self.canvas, self.handle_right_mouse_release)
                },
                "Motion": (self.root, self.handle_mouse_motion),
                "KeyPress": {
                    "Left": (self.root, self.handle_button_left),
                    "Right": (self.root, self.handle_button_right),
                    "Up": (self.root, self.handle_button_up),
                    "Down": (self.root, self.handle_button_down),
                    "Return": [
                        (self.entry_dict_path, self.handle_update_dict_path),
                        (self.entry_pages_dir, self.handle_update_pages_path)
                    ],
                    "Delete": (self.root, self.handle_delete_page)
                },
            }

    def create_ui_grid(self, root):
        """
        Grid must be created before event binding
        :return: grid of canvas_objects
        """

        # arrange table
        widgets_table_rows = [
            [self.dictionary_opener],
            [self.page_opener],
            [self.page_cursor],
            [self.anchor_editor],
            [self.text_writer],
        ]

        # if argument not specified explicitly, take it from global arguments
        global_arguments = {"padx": 4, "pady": 4, "sticky": tk.EW}

        columns_count = max(len(row) for row in widgets_table_rows)
        root.columnconfigure(columns_count, weight=1)
        root.rowconfigure(len(widgets_table_rows), weight=1)

        return widgets_table_rows, global_arguments

    def setup_ui(self):
        self.top_align_grid = tk.Frame(self.ui_grid, height=Page.default_size[1])
        put_objects_on_grid(*self.create_ui_grid(self.top_align_grid))
        self.top_align_grid.pack(anchor=tk.NW)

        self.rowconfigure(1)
        self.columnconfigure(2)
        self.ui_grid.pack(side="left")
        self.canvas.pack(side="right")
        self.pack(fill=tk.BOTH, expand=1)

        self.bind_handlers(self.create_events_dict())

    def select_page_switch_handlers(self):
        self.arrow_handlers = PageSwitchHandlers

    def select_anchor_point_handlers(self):
        self.arrow_handlers = AnchorPointHandlers

    def handle_canvas_enter(self, event=None):
        if event.widget == self.canvas:
            if self.arrow_handlers == AnchorPointHandlers:
                self.continue_point_redraw = True
                if self.mouse_position is not None:
                    self.constant_redraw_last_anchor(self.mouse_position)

    def handle_canvas_leave(self, event=None):
        if event.widget == self.canvas:
            if self.page_manager.is_started_anchor_editing():
                self.page_manager.anchor_manager.delete_temp_point()
                self.continue_point_redraw = False

    def handle_mouse_motion(self, event):
        self.mouse_position = Point(event.x, event.y)

    def handle_left_mouse_release(self, event):
        if self.page_manager.is_started_anchor_editing():
            self.page_manager.anchor_manager.update_current(Point(event.x, event.y))

            self.page_manager.anchor_manager.move_right()
            self.update_anchor_indices()

    def handle_right_mouse_release(self, event):
        if self.page_manager.is_started_anchor_editing():
            self.page_manager.anchor_manager.delete_current_point()
            self.update_anchor_indices()


if __name__ == "__main__":
    PageTextWriterApp.main()
