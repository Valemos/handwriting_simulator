import tkinter as tk
from pathlib import Path

from gui.canvas_display import CanvasDisplay
from gui.event_bind_manager import EventBindManager
from gui.widget_positioning import put_objects_on_grid
from handwriting.page_writing.anchor_points_handlers import AnchorPointHandlers
from handwriting_gui.arrow_button_handlers import ArrowButtonHandlers
from handwriting.page_writing.button_handler_group import ArrowButtonsHandler
from handwriting.page_writing.page import Page
from handwriting_gui.page_button_handlers import PageSwitchHandlers
from handwriting.page_writing.page_drawer import PageDrawer
from handwriting.page_writing.page_iterator import PageIterator
from handwriting.paths_dictionary.dictionary_manager import DictionaryManager
from handwriting_gui.dictionary_opener_widget import DictionaryOpenerWidget
from handwriting_gui.page_cursor_widget import PageCursorWidget
from handwriting_gui.page_opener_widget import PageOpenerWidget
from handwriting_gui.text_writer_widget import TextWriterWidget


class PageTextWriterApp(tk.Frame,
                        EventBindManager,
                        ArrowButtonHandlers):
    default_pages_directory = Path("../pages")

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self.root.title("Text writer")

        self.dictionary_manager = DictionaryManager()
        self.page_iterator = PageIterator()

        grid_width = 15
        self.ui_grid = tk.Frame(self)

        self.canvas = tk.Canvas(self, bg="white", width=Page.default_size[0], height=Page.default_size[1])
        self.display = CanvasDisplay(self.canvas)

        self.dictionary_opener = DictionaryOpenerWidget(self.ui_grid, grid_width, self.dictionary_manager)

        self.page_drawer = PageDrawer(self.display, self.page_iterator)

        self.page_cursor = PageCursorWidget(
            self.ui_grid,
            grid_width,
            self.page_iterator,
            self.page_drawer.draw_current_page)

        self.page_opener = PageOpenerWidget(
            self.ui_grid,
            grid_width,
            self.page_iterator,
            self.page_drawer.draw_current_page)

        self.text_writer = TextWriterWidget(self.ui_grid, grid_width, self.page_drawer, self.dictionary_manager)
        # self.anchor_editor = AnchorEditorWidget(self.ui_grid, grid_width)

        self.setup_ui()
        self.page_cursor.update_menus()

        self.arrows_handler: ArrowButtonsHandler = None
        self.select_page_switch_handlers()

    @staticmethod
    def main():
        app = PageTextWriterApp(tk.Tk())
        app.wait_visibility()
        app.initialize()
        app.mainloop()

    def initialize(self):
        self.text_writer.entry_draw_text.insert(tk.END, "тестовая")
        self.dictionary_opener.entry_dict_path.set(r"/media/data/coding/Python_codes/Handwriting_extractor_project/paths_format_transition/anton.dict")
        self.dictionary_opener.open_from_entry_path()
        self.text_writer.handle_write_text()
        self.page_drawer.draw_current_page()

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
                    "Delete": (self.root, self.page_cursor.handle_delete_page)
                },
            }

    def setup_ui(self):

        # if argument not specified explicitly, take it from global arguments
        global_arguments = {"padx": 4, "pady": 4, "sticky": tk.EW}

        put_objects_on_grid(self.ui_grid, [
            [self.dictionary_opener],
            [self.page_opener],
            [self.page_cursor],
            # [self.anchor_editor],
            [self.text_writer],
        ], global_arguments)

        self.rowconfigure(1)
        self.columnconfigure(2)
        self.ui_grid.pack(side="left")
        self.canvas.pack(side="right")
        self.pack(fill=tk.BOTH, expand=1)

        self.bind_handlers(self.create_events_dict())

    def select_page_switch_handlers(self):
        self.arrows_handler = self.page_cursor

    def select_anchor_point_handlers(self):
        self.arrows_handler = self.an

    def handle_canvas_enter(self, event=None):
        # TODO add anchors
        pass

    def handle_canvas_leave(self, event=None):
        # TODO add anchors
        pass

    def handle_mouse_motion(self, event):
        # todo add anchor editing
        # self.anchor_editor.set_mouse_position(Point(event.x, event.y))
        pass

    def handle_left_mouse_release(self, event):
        # TODO add anchors
        pass

    def handle_right_mouse_release(self, event):
        # TODO add anchors
        pass


if __name__ == "__main__":
    PageTextWriterApp.main()
