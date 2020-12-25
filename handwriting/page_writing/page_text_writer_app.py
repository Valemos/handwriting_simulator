import threading
import tkinter as tk
from math import sqrt
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring
from pathlib import Path
import random

from PIL import ImageDraw
from PIL.ImageTk import PhotoImage

from handwriting.canvas_objects_manager import CanvasObjectsManager
from handwriting.event_handler import EventManager
from handwriting.grid_manager import GridManager
from handwriting.page_writing.button_handler_group import ButtonHandlerGroup
from handwriting.page_writing.page_manager import PageManager
from handwriting.path_management.dictionary_manager import DictionaryManager
from handwriting.path_management.point import Point
from handwriting.path_management.signature_dictionary import SignatureDictionary
from handwriting.path_management.handwritten_path import HandwrittenPath
from handwriting.page_writing.anchor_points_handlers import AnchorPointsHandlers
from handwriting.page_writing.page_button_handlers import PageButtonHandlers


class PageTextWriterApp(tk.Frame,
                        DictionaryManager,
                        CanvasObjectsManager,
                        GridManager,
                        EventManager):

    msg_not_selected = '-'
    default_pages_directory = Path("pages")

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root

        self.letters_dictionary = None
        self.pages_manager = PageManager()

        self.text_image = None

        self.mouse_position = None
        self.setup_UI()
        self.reset_canvas()
        self.update_pages_menu()

        self.arrow_handlers: ButtonHandlerGroup = None
        self.select_page_switch_handlers()

        # self.open_dictionary(r"D:\coding\Python_codes\Handwriting_extractor_project\paths_format_transition\anton.dict")
        self.open_pages_directory(r"D:\coding\Python_codes\Handwriting_extractor_project\pages")
        # self.entry_draw_text.insert(1.0, "прив")

        def update_after_creation(app):
            app.update_current_page()
            exit(0)
        threading.Thread(target=update_after_creation, args=(self,)).start()

        # allow to edit canvas after it was created
        CanvasObjectsManager.__init__(self)

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
                    "Left": (self.root, self.button_left),
                    "Right": (self.root, self.button_right),
                    "Up": (self.root, self.button_up),
                    "Down": (self.root, self.button_down),
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

        label_dict_path = tk.Label(root, text="Dictionary:")
        self.field_dict_path = tk.StringVar(root)
        self.entry_dict_path = tk.Entry(root, width=round(grid_width / 2), textvariable=self.field_dict_path)

        label_pages_dir = tk.Label(root, text="Pages folder:")
        self.field_pages_dir = tk.StringVar(root)
        self.entry_pages_dir = tk.Entry(root, width=round(grid_width / 2), textvariable=self.field_pages_dir)

        self.var_page_name = tk.StringVar(self)
        self.menu_pages = tk.OptionMenu(root, self.var_page_name, value=None)
        self.update_page_name()

        self.menu_pages.config(width=grid_width)

        frame_page_controls = tk.Frame(root, width=grid_width)
        btn_prev_page = tk.Button(frame_page_controls, text='<-', command=self.handle_prev_page,
                                  width=round(grid_width / 2))
        btn_next_page = tk.Button(frame_page_controls, text='->', command=self.handle_next_page,
                                  width=round(grid_width / 2))
        btn_prev_page.pack(side=tk.LEFT)
        btn_next_page.pack(side=tk.RIGHT)

        btn_rename_page = tk.Button(root, text="Rename page", width=round(grid_width * 2 / 3),
                                    command=self.handle_rename_page)

        btn_remove_page = tk.Button(root, text="Remove page", width=round(grid_width * 2 / 3),
                                    command=self.handle_delete_page)

        btn_draw_text = tk.Button(root, text="Draw text", width=round(grid_width * 2 / 3),
                                  command=lambda: self.handle_draw_text())

        btn_reset_text = tk.Button(root, text="Reset text", width=round(grid_width * 2 / 3),
                                   command=lambda: self.handle_reset_text())

        label_space_sz = tk.Label(root, text="Space size")

        self.space_sz_var = tk.StringVar(self)
        self.space_sz_var.set(50)
        entry_space_sz = tk.Entry(root, width=grid_width, textvariable=self.space_sz_var)
        self.entry_draw_text = tk.Text(root, width=grid_width * 2 - 8, height=20)

        btn_open_dict = tk.Button(root, text="Open dictionary", width=grid_width,
                                  command=self.open_dictionary)

        btn_open_pages = tk.Button(root, text="Open pages", width=grid_width,
                                   command=self.open_pages_directory)

        btn_pages_from_images = tk.Button(root, text="Images to pages", width=grid_width,
                                          command=self.open_images_to_pages)

        btn_save_pages = tk.Button(root, text="Save pages", width=grid_width,
                                   command=self.save_pages_to_files)

        self.name_btn_edit_anchors = "Edit anchors"
        self.name_btn_stop_edit_anchors = "Stop edit anchors"
        self.var_edit_page_anchors = tk.StringVar()
        self.var_edit_page_anchors.set(self.name_btn_edit_anchors)
        btn_edit_page_anchors = tk.Button(root, textvariable=self.var_edit_page_anchors, width=grid_width,
                                          command=self.handle_edit_page_points)


        self.format_anchor_index = "line: {0:<3} point: {1:<3}"
        self.var_anchor_index = tk.StringVar(root)
        label_anchor_index = tk.Label(root, textvariable=self.var_anchor_index, width=grid_width)
        self.update_anchor_indices()

        self.var_lines_count = tk.StringVar(root)
        self.var_lines_count.set("0")
        entry_lines_count = tk.Entry(root, width=grid_width, textvariable=self.var_lines_count)

        label_create_lines = tk.Label(root, text="Create more lines:")

        self.btn_create_lines = tk.Button(root, text="Create lines", width=grid_width,
                                          command=self.handle_create_more_lines)
        self.btn_create_lines.config(state=tk.DISABLED)

        # arrange table
        widgets_table_rows = [
            [label_dict_path,    self.entry_dict_path,  btn_open_dict],
            [label_pages_dir,    self.entry_pages_dir,  btn_open_pages,         btn_pages_from_images],
            [btn_rename_page,    self.menu_pages,       btn_remove_page,        btn_edit_page_anchors],
            [btn_save_pages,     frame_page_controls,   btn_reset_text,         btn_draw_text],
            [label_create_lines, entry_lines_count,     self.btn_create_lines],
            [None,               label_space_sz,         entry_space_sz,        label_anchor_index],
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
        self.open_dictionary(self.field_dict_path.get())

    def open_dictionary(self, path=None):
        self.root.focus()
        path = self.get_dictionary_file_path(path)
        self.letters_dictionary = SignatureDictionary.from_file(path)
        self.field_dict_path.set(str(path))

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
        self.open_pages_directory(self.field_pages_dir.get())

    def open_pages_directory(self, path=None):
        file_path = self.get_pages_directory(path)
        self.field_pages_dir.set(str(file_path))
        self.update_pages(file_path)
        self.update_current_page()
        self.update_pages_menu()
        self.update_page_name()

    def open_images_to_pages(self, path=None):
        file_path = self.get_pages_directory(path)
        self.field_pages_dir.set(str(file_path))
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

    @staticmethod
    def draw_point_scope(canvas, point, color="black"):
        """creates scope shape on canvas and returns list of all created canvas objects"""
        lst = []
        r = 10
        lst.append(canvas.create_oval((point.x - r, point.y - r, point.x + r, point.y + r), outline=color))
        lst.append(canvas.create_line(point.x, point.y - r, point.x, point.y + r, fill=color))
        lst.append(canvas.create_line(point.x - r, point.y, point.x + r, point.y, fill=color))
        return lst

    def handle_delete_page(self, event=None):
        self.pages_manager.delete_current_page()
        self.update_current_page()
        self.update_pages_menu()
        self.update_page_name()

    def handle_page_chosen(self, choice):
        if self.pages_manager.anchor_manager is not None:
            self.disable_edit_anchor_points()
        self.pages_manager.select_page(choice)
        self.update_current_page()
        self.update_page_name()

    def select_page_switch_handlers(self):
        """Selects set of handlers to move between pages"""
        self.arrow_handlers = PageButtonHandlers

    def select_anchor_point_handlers(self):
        """Selects set of handlers to move between anchor points on this page"""
        self.arrow_handlers = AnchorPointsHandlers

    def enable_edit_anchor_points(self):
        self.var_edit_page_anchors.set(self.name_btn_stop_edit_anchors)

        # turn on button for line creation
        self.btn_create_lines.config(state=tk.NORMAL)

        self.select_anchor_point_handlers()

        # start modifying page anchor points
        self.pages_manager.start_anchor_editing(self.canvas, self.draw_point_scope)
        self.update_anchor_indices()

    def disable_edit_anchor_points(self):
        self.var_edit_page_anchors.set(self.name_btn_edit_anchors)
        # turn off button for line creation
        self.btn_create_lines.config(state=tk.DISABLED)

        self.select_page_switch_handlers()

        self.pages_manager.stop_anchor_editing()
        self.update_anchor_indices()

    def handle_edit_page_points(self, event=None):
        """Switches modes for button interaction"""

        if self.var_edit_page_anchors.get() == self.name_btn_edit_anchors:
            self.enable_edit_anchor_points()
        else:
            self.disable_edit_anchor_points()

    def handle_create_more_lines(self, event=None):
        """
        Creates multiple lines from first two rows of points
        Using value from entry, creates N intermediate points with equal intervals between adjacent points

        To make this function work properly, user must create the same number of points in both lines
        Otherwise, lines below will be skewed
        """
        update_integer_field(self.var_lines_count)

        if self.pages_manager.anchor_manager is not None:
            lines_num = int(self.var_lines_count.get())
            if lines_num > 0:
                if not self.pages_manager.anchor_manager.add_intermediate_lines(0, 1, lines_num):
                    messagebox.showinfo("Error", "Cannot create intermediate lines\nfrom first two lines")


    def handle_canvas_enter(self, event=None):
        if event.widget == self.canvas:
            if self.arrow_handlers == AnchorPointsHandlers:
                self.continue_point_redraw = True
                if self.mouse_position is not None:
                    self.constant_redraw_last_anchor(self.mouse_position)

    def handle_canvas_leave(self, event=None):
        if event.widget == self.canvas:
            if self.pages_manager.anchor_manager is not None:
                self.pages_manager.anchor_manager.delete_temp_point()
                self.continue_point_redraw = False


    def handle_mouse_motion(self, event):
        self.mouse_position = Point(event.x, event.y)

    def handle_left_mouse_release(self, event):
        if self.pages_manager.anchor_manager is not None:
            self.pages_manager.anchor_manager.update_current_point(Point(event.x, event.y))

            if self.pages_manager.anchor_manager.get_current_point() is not None:
                self.pages_manager.anchor_manager.move_right()

            self.update_anchor_indices()

    def handle_right_mouse_release(self, event):
        if self.pages_manager.anchor_manager is not None:
            self.pages_manager.anchor_manager.delete_current_point()
            self.update_anchor_indices()


    def constant_redraw_last_anchor(self, point):
        """
        Deletes last drawn objects from canvas and draws new point scope
        using anchor manager functions
        :param point: tuple or list with two elements - x and y coordinates
        """

        if self.pages_manager.anchor_manager is not None:
            self.pages_manager.anchor_manager.redraw_pointer_point(point)

        if self.continue_point_redraw:
            self.root.after(17, self.constant_redraw_last_anchor, self.mouse_position)

    def button_left(self, event=None):
        self.arrow_handlers.left(self)

    def button_right(self, event=None):
        self.arrow_handlers.right(self)

    def button_up(self, event=None):
        self.arrow_handlers.up(self)

    def button_down(self, event=None):
        self.arrow_handlers.down(self)

    def handle_next_page(self, event=None):
        if self.pages_manager.anchor_manager is not None:
            self.disable_edit_anchor_points()

        self.pages_manager.next_page()
        self.update_current_page()
        self.update_page_name()

    def handle_prev_page(self, event=None):
        if self.pages_manager.anchor_manager is not None:
            self.disable_edit_anchor_points()

        self.pages_manager.previous_page()
        self.update_current_page()
        self.update_page_name()

    def update_anchor_indices(self):
        line_i, point_i = -1, -1
        if self.pages_manager.anchor_manager is not None:
            line_iter = self.pages_manager.anchor_manager.line_iterator
            if line_iter is not None:
                line_i = line_iter.object_index
                point_i = line_iter.current().object_index if line_iter.current() is not None else 0
        res = self.format_anchor_index.format(line_i, point_i)
        self.var_anchor_index.set(self.format_anchor_index.format(line_i, point_i))

    def update_current_page(self):
        self.reset_canvas()
        self.update_anchor_indices()
        if self.pages_manager.current_page() is not None:
            self.current_page_image = PhotoImage(
                self.pages_manager.current_page().current_image.resize((
                    self.canvas.winfo_width(),
                    self.canvas.winfo_height()
                ))
            )
            self.canvas.create_image((0, 0), anchor=tk.NW, image=self.current_page_image)

    def update_pages_menu(self):
        """Sets image_initial names and their indices as menu options"""

        choices = None
        if len(self.pages_manager.pages) > 0:
            choices = {self.pages_manager.pages[page_i].name: page_i for page_i in range(len(self.pages_manager.pages))}

        self.set_menu_choices(self.menu_pages, choices, self.handle_page_chosen)

    def update_page_name(self):
        if self.pages_manager.current_page() is not None:
            self.var_page_name.set(self.pages_manager.current_page().name)
        else:
            self.var_page_name.set(self.msg_not_selected)

    def handle_draw_text(self):
        """Draws text on current page"""

        self.pages_manager.current_page().create_text_image()
        self.draw_text_on_image(self.entry_draw_text.get(1.0, tk.END),
                                self.pages_manager.current_page().current_image)
        self.update_current_page()

    def draw_text_on_image(self, text, image):
        """uses reference to image and translates text to it"""
        if self.letters_dictionary is None:
            return

        # create path from letter paths
        total_path_curves = []
        for char in text:
            path_group = self.letters_dictionary[char]
            if path_group is not None:
                path_index = random.randrange(0, len(path_group) - 1)
                path_group[path_index].set_position(Point(0, 0))
                total_path_curves.extend(path_group[path_index].components)
            else:
                print(f"char not found \"{char}\"")

        draw = ImageDraw.Draw(image)
        total_path = HandwrittenPath("text", total_path_curves)
        total_path.set_position(Point(100, 400))

        for p1, p2 in total_path:
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
        """Renames current selected page"""
        if self.pages_manager.current_page() is not None:
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
