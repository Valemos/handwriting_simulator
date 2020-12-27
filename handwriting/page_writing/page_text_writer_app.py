import random
import threading
import tkinter as tk
from math import sqrt
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring

from PIL import ImageDraw
from PIL.ImageTk import PhotoImage

from handwriting.event_handler import EventManager
from handwriting.grid_manager import GridManager
from handwriting.gui_parts.button_state import ButtonState
from handwriting.gui_parts.button_with_two_states import ButtonWithTwoStates
from handwriting.gui_parts.entry_integer_with_label import EntryIntegerWithLabel
from handwriting.gui_parts.entry_with_label import EntryWithLabel
from handwriting.gui_parts.left_right_buttons import LeftRightButtons
from handwriting.gui_parts.menu_with_handler import MenuWithHandler
from handwriting.page_writing.anchor_points_handlers import AnchorPointHandlers
from handwriting.page_writing.arrow_button_handlers import ArrowButtonHandlers
from handwriting.page_writing.button_handler_group import ButtonHandlerGroup
from handwriting.page_writing.handwritten_text_writer import HandwrittenTextWriter
from handwriting.page_writing.page_button_handlers import PageSwitchHandlers
from handwriting.page_writing.page_manager import PageManager
from handwriting.path_management.dictionary_manager import DictionaryManager
from handwriting.path_management.handwritten_path import HandwrittenPath
from handwriting.path_management.point import Point


class PageTextWriterApp(tk.Frame,
                        GridManager,
                        EventManager,
                        ArrowButtonHandlers):

    default_pages_directory = Path("pages")

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root

        self.dictionary_manager = DictionaryManager()
        self.pages_manager = PageManager()

        self.text_image = None

        self.mouse_position = None
        self.setup_UI()
        self.reset_canvas()
        self.update_pages_menu()

        self.arrow_handlers: ButtonHandlerGroup = None
        self.select_page_switch_handlers()

        # self.open_pages_directory(r"D:\coding\Python_codes\Handwriting_extractor_project\pages")

        def update_after_creation(app):
            app.update_current_page()
            exit(0)
        threading.Thread(target=update_after_creation, args=(self,)).start()

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

        grid_width = 15

        self.entry_dict_path = EntryWithLabel(root, "Dictionary:", grid_width * 2, 1/2)
        self.entry_pages_dir = EntryWithLabel(root, "Pages folder:", grid_width * 2, 1/2)

        self.menu_pages = MenuWithHandler(root, grid_width, self.handle_page_chosen)
        self.update_page_name()

        self.menu_pages.config(width=grid_width)

        buttons_page_controls = LeftRightButtons(root, grid_width, self.handle_prev_page, self.handle_next_page)

        btn_rename_page = tk.Button(root, text="Rename page", width=round(grid_width * 2 / 3),
                                    command=self.handle_rename_page)

        btn_remove_page = tk.Button(root, text="Remove page", width=round(grid_width * 2 / 3),
                                    command=self.handle_delete_page)

        btn_draw_text = tk.Button(root, text="Draw text", width=round(grid_width * 2 / 3),
                                  command=lambda: self.handle_draw_text())

        btn_reset_text = tk.Button(root, text="Reset text", width=round(grid_width * 2 / 3),
                                   command=lambda: self.handle_reset_text())

        self.entry_space_sz = EntryIntegerWithLabel(root, "Space size:", grid_width * 2, 1/2)
        self.entry_space_sz.set(50)

        self.entry_draw_text = tk.Text(root, width=grid_width * 2 - 8, height=20)

        btn_open_dict = tk.Button(root, text="Open dict_manager", width=grid_width,
                                  command=self.open_dictionary)

        btn_open_pages = tk.Button(root, text="Open pages", width=grid_width,
                                   command=self.open_pages_directory)

        btn_pages_from_images = tk.Button(root, text="Images to pages", width=grid_width,
                                          command=self.open_images_to_pages)

        btn_save_pages = tk.Button(root, text="Save pages", width=grid_width,
                                   command=self.save_pages_to_files)


        self.button_edit_anchors = ButtonWithTwoStates(
            root, grid_width,
            ButtonState("Edit anchors", self.enable_edit_anchor_points),
            ButtonState("Stop edit anchors", self.disable_edit_anchor_points)
        )

        self.format_anchor_index = "line: {0:<3} point: {1:<3}"
        self.var_anchor_indices = tk.StringVar(root)
        label_anchor_index = tk.Label(root, textvariable=self.var_anchor_indices, width=grid_width)
        self.update_anchor_indices()

        self.entry_lines_count = EntryIntegerWithLabel(root, "Lines:", grid_width, 1 / 3)
        self.entry_lines_count.set(0)

        label_create_lines = tk.Label(root, text="Create more lines:")

        self.btn_create_lines = tk.Button(root, text="Create lines", width=grid_width,
                                          command=self.handle_create_more_lines)
        self.btn_create_lines.config(state=tk.DISABLED)

        # arrange table
        widgets_table_rows = [
            [(self.entry_dict_path, {"columnspan": 2}), None,   btn_open_dict],
            [(self.entry_pages_dir, {"columnspan": 2}), None,   btn_open_pages,         btn_pages_from_images],
            [btn_rename_page,       self.menu_pages,            btn_remove_page,        self.button_edit_anchors],
            [btn_save_pages,        buttons_page_controls,      btn_reset_text,         btn_draw_text],
            [label_create_lines,    self.entry_lines_count,     self.btn_create_lines],
            [(self.entry_space_sz, {"columnspan": 2}), None,    label_anchor_index],
            [(self.entry_draw_text, {"columnspan": 4})]
        ]

        # if argument not specifyed explicitly, take it from global arguments
        global_arguments = {"padx": 4, "pady": 4, "sticky": tk.EW}

        columns_count = max(len(row) for row in widgets_table_rows)
        root.columnconfigure(columns_count, weight=1)
        root.rowconfigure(len(widgets_table_rows), weight=1)

        return widgets_table_rows, global_arguments

    def setup_UI(self):
        self.root.title("Text writer")

        self.ui_grid = tk.Frame(self)

        self.top_align_grid = tk.Frame(self.ui_grid, height=round(210 * 2 * sqrt(2)))
        self.put_objects_on_grid(*self.create_ui_grid(self.top_align_grid))
        self.top_align_grid.pack(anchor=tk.NW)

        self.canvas = tk.Canvas(self, bg="white", width=210 * 2, height=round(210 * 2 * sqrt(2)))
        self.reset_canvas()

        self.rowconfigure(1)
        self.columnconfigure(2)
        self.ui_grid.grid(row=0, column=0)
        self.canvas.grid(row=0, column=1)
        self.pack(fill=tk.BOTH, expand=1)

        self.bind_handlers(self.create_events_dict())

    def reset_canvas(self):
        self.canvas.delete("all")

    def canvas_delete_points(self):
        for obj in self.points_draw_objects:
            self.canvas.delete(obj)

        self.points_draw_objects = []

    def handle_update_dict_path(self, event=None):
        self.open_dictionary(self.entry_dict_path.get())

    def open_dictionary(self, path):
        self.root.focus()
        edited_path = self.dictionary_manager.read_from_file(path)
        self.entry_dict_path.set(str(edited_path))

    def get_pages_directory(self, directory_str: str = None):
        if directory_str is not None:
            directory = Path(directory_str)
        else:
            directory = filedialog.askdirectory()
            directory = Path(directory) if directory != '' else self.default_pages_directory

        if not directory.is_dir():
            directory = directory.with_suffix('')

        if not directory.exists():
            directory.mkdir(parents=True)

        return directory

    def handle_update_pages_path(self, event=None):
        self.open_pages_directory(self.entry_pages_dir.get())

    def open_pages_directory(self, path=None):
        file_path = self.get_pages_directory(path)
        self.entry_pages_dir.set(str(file_path))
        self.update_pages(file_path)
        self.update_current_page()
        self.update_pages_menu()
        self.update_page_name()

    def open_images_to_pages(self, path=None):
        file_path = self.get_pages_directory(path)
        self.entry_pages_dir.set(str(file_path))
        self.read_images_to_pages(file_path)
        self.update_current_page()
        self.update_pages_menu()
        self.update_page_name()

    def save_pages_to_files(self):
        self.disable_edit_anchor_points()
        for page in self.pages_manager.pages:
            page.save_file()

    def handle_reset_text(self):
        self.pages_manager.current_page().image_text = None
        self.pages_manager.current_page().set_current_image_initial()
        self.update_current_page()

    def handle_delete_page(self, event=None):
        self.pages_manager.delete_current_page()
        self.update_current_page()
        self.update_pages_menu()
        self.update_page_name()

    def handle_page_chosen(self, choice):
        if self.pages_manager.current_page_exists():
            self.disable_edit_anchor_points()
        self.pages_manager.select_page(choice)
        self.update_current_page()
        self.update_page_name()

    def select_page_switch_handlers(self):
        self.arrow_handlers = PageSwitchHandlers

    def select_anchor_point_handlers(self):
        self.arrow_handlers = AnchorPointHandlers

    def enable_edit_anchor_points(self):
        self.btn_create_lines.config(state=tk.NORMAL)
        self.select_anchor_point_handlers()
        self.pages_manager.start_anchor_editing(self.canvas)
        self.update_anchor_indices()

    def disable_edit_anchor_points(self):
        self.btn_create_lines.config(state=tk.DISABLED)
        self.select_page_switch_handlers()
        self.pages_manager.stop_anchor_editing()
        self.update_anchor_indices()

    def handle_create_more_lines(self, event=None):
        """
        Creates multiple lines from first two rows of anchor points
        Using value from entry, creates N intermediate points with equal intervals between adjacent points

        To make this function work properly, user must create the same number of points in both lines
        Otherwise, lines below will be skewed
        """

        if self.pages_manager.current_page_exists():
            lines_num = int(self.entry_lines_count.get())
            if lines_num > 0:
                if not self.pages_manager.anchor_manager.add_intermediate_lines(0, 1, lines_num):
                    messagebox.showinfo("Error", "Cannot create intermediate lines\nfrom first two lines")

    def handle_canvas_enter(self, event=None):
        if event.widget == self.canvas:
            if self.arrow_handlers == AnchorPointHandlers:
                self.continue_point_redraw = True
                if self.mouse_position is not None:
                    self.constant_redraw_last_anchor(self.mouse_position)

    def handle_canvas_leave(self, event=None):
        if event.widget == self.canvas:
            if self.pages_manager.check_started_anchor_editing():
                self.pages_manager.anchor_manager.delete_temp_point()
                self.continue_point_redraw = False

    def handle_mouse_motion(self, event):
        self.mouse_position = Point(event.x, event.y)

    def handle_left_mouse_release(self, event):
        if self.pages_manager.check_started_anchor_editing():
            self.pages_manager.anchor_manager.update_current_point(Point(event.x, event.y))

            if self.pages_manager.anchor_manager.get_current_point() is not None:
                self.pages_manager.anchor_manager.move_right()

            self.update_anchor_indices()

    def handle_right_mouse_release(self, event):
        if self.pages_manager.check_started_anchor_editing():
            self.pages_manager.anchor_manager.delete_current_point()
            self.update_anchor_indices()

    def constant_redraw_last_anchor(self, point):
        if self.pages_manager.check_started_anchor_editing():
            self.pages_manager.anchor_manager.redraw_pointer_point(point)

        if self.continue_point_redraw:
            self.root.after(17, self.constant_redraw_last_anchor, self.mouse_position)

    def handle_next_page(self, event=None):
        if self.pages_manager.check_started_anchor_editing():
            self.disable_edit_anchor_points()

        self.pages_manager.next_page()
        self.update_current_page()
        self.update_page_name()

    def handle_prev_page(self, event=None):
        if self.pages_manager.check_started_anchor_editing():
            self.disable_edit_anchor_points()

        self.pages_manager.previous_page()
        self.update_current_page()
        self.update_page_name()

    def update_anchor_indices(self):
        line_i, point_i = self.get_current_anchor_indices()
        anchor_indices_string = self.format_anchor_index.format(line_i, point_i)
        self.var_anchor_indices.set(anchor_indices_string)

    def get_current_anchor_indices(self):
        line_i, point_i = -1, -1
        if self.pages_manager.check_started_anchor_editing():
            line_iter = self.pages_manager.anchor_manager.line_iterator
            if line_iter is not None:
                line_i = line_iter.object_index
                point_i = line_iter.current().object_index if line_iter.current() is not None else 0
        return line_i, point_i

    def update_current_page(self):
        self.reset_canvas()
        self.update_anchor_indices()
        if self.pages_manager.current_page_exists():
            self.current_page_image = self.get_resized_current_page_image()
            self.canvas.create_image((0, 0), anchor=tk.NW, image=self.current_page_image)

    def get_resized_current_page_image(self):
        return PhotoImage(
            self.pages_manager.current_page().current_image.resize((
                self.canvas.winfo_width(),
                self.canvas.winfo_height()
            ))
        )

    def update_pages_menu(self):
        choices = None
        if len(self.pages_manager.pages) > 0:
            choices = {self.pages_manager.pages[page_i].name: page_i for page_i in range(len(self.pages_manager.pages))}

        self.menu_pages.update_choices(choices)

    def update_page_name(self):
        if self.pages_manager.current_page_exists():
            self.menu_pages.set(self.pages_manager.current_page().name)

    def handle_draw_text(self):
        text = self.entry_draw_text.get(1.0, tk.END)
        self.draw_text_on_page(text, self.pages_manager.current_page())
        self.update_current_page()

    def draw_text_on_page(self, text, page):
        if not self.dictionary_manager.exists():
            return

        text_drawer = HandwrittenTextWriter(page, self.dictionary_manager.dictionary)

        draw = ImageDraw.Draw(page)
        for p1, p2 in text_drawer.write_text(text):
            draw.line((*p1, *p2), fill=0, width=4)

    def update_pages(self, file_path):
        self.pages_manager.pages = []
        self.pages_manager.read_pages_from_dir(file_path)

    def read_images_to_pages(self, file_path):
        self.pages_manager.pages = []
        self.pages_manager.read_images_to_pages(file_path)
        self.update_current_page()
        self.update_pages_menu()
        self.update_page_name()

    def handle_rename_page(self):
        if self.pages_manager.current_page_exists():
            new_name = askstring("Rename", "Enter new page name")
            if new_name is not None:
                self.pages_manager.current_page().set_name(new_name)
                self.update_pages_menu()
                self.update_page_name()

def main():
    root = tk.Tk()
    app = PageTextWriterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
