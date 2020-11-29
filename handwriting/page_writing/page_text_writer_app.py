import tkinter as tk
from math import sqrt
from tkinter import filedialog
from tkinter.simpledialog import askstring
from pathlib import Path


from handwriting.canvas_objects_manager import CanvasObjectsManager
from handwriting.event_handler import EventManager
from handwriting.grid_manager import GridManager
from handwriting.option_menu_manager import OptionMenuManager
from handwriting.page_writing.page_text_manager import PageManager
from handwriting.path_management.dictionary_manager import DictionaryManager
from handwriting.path_management.signature_dictionary import SignatureDictionary


class PageTextWriterApp(tk.Frame, DictionaryManager, CanvasObjectsManager, GridManager, EventManager, OptionMenuManager):

    msg_not_selected = '-'
    default_pages_directory = Path("pages")

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root

        self.brush_size = 5
        self.brush_color = "black"

        self.letters_dictionary = None
        self.pages_manager = PageManager()
        self.pages_iterator = self.pages_manager.get_iterator()

        self.text_image = None

        self.points_counter = 0
        self.points_colors = ['red', 'red', 'black']

        self.text_points_format = '({0}, {1})/({2}, {3})\n({4}, {5})'

        self.image_suffix = '.png'

        self.shift_paths_open_mode = tk.BooleanVar()
        self.shift_paths_open_mode.set(0)

        self.setup_UI()
        self.reset_canvas()
        self.update_pages_menu()

        # allow to edit canvas after it was created
        CanvasObjectsManager.__init__(self)

    def create_events_dict(self):
        return \
            {
                # "B1": {
                #     "ButtonRelease": (self.canvas, self.handle_mouse_release),
                #     "Motion": (self.canvas, self.handle_motion_draw)
                # },
                "KeyPress": {
                    "Left": (self.root, self.handle_prev_page),
                    "Right": (self.root, self.handle_next_page),
                    "Return": [
                        (self.entry_dict_path, self.handle_update_dict_path),
                        (self.entry_pages_dir, self.handle_update_pages_path)
                    ],
                    "Delete": (self.root, self.handle_delete_page)
                }
            }

    def create_ui_grid(self, root):
        """
        Grid must be created before event binding
        :return: grid of objects
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

        self.var_points_str = tk.StringVar(self)
        self.var_points_str.set(self.text_points_format.format(*[0] * 6))
        field_points_str = tk.Label(root, width=grid_width,
                                    textvariable=self.var_points_str)

        label_space_sz = tk.Label(root, text="Space size")

        self.space_sz_var = tk.StringVar(self)
        self.space_sz_var.set(50)
        entry_space_sz = tk.Entry(root, width=grid_width, textvariable=self.space_sz_var)
        self.entry_draw_text = tk.Text(root, width=grid_width * 2 - 8, height=20)

        btn_open_dict = tk.Button(root, text="Open dictionary", width=grid_width,
                                  command=self.open_dictionary)

        btn_open_pages = tk.Button(root, text="Open images", width=grid_width,
                                   command=self.open_pages_directory)

        # arrange table
        widgets_table_rows = [
            [None,              label_space_sz,         entry_space_sz,     field_points_str],
            [label_dict_path,   self.entry_dict_path,   btn_open_dict],
            [label_pages_dir,   self.entry_pages_dir,   self.menu_pages,    frame_page_controls],
            [None,              btn_open_pages,         btn_rename_page,    btn_remove_page],
            [None,              None,                   btn_reset_text,    btn_draw_text],
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
        self.update_page_images(file_path)
        self.update_current_page()
        self.update_page_name()

    def handle_reset_text(self):
        pass

    def draw_point_scope(self, point, color):
        lst = []
        r = 10
        lst.append(self.canvas.create_oval((point[0] - r, point[1] - r, point[0] + r, point[1] + r), outline=color))
        lst.append(self.canvas.create_line(point[0], point[1] - r, point[0], point[1] + r, fill=color))
        lst.append(self.canvas.create_line(point[0] - r, point[1], point[0] + r, point[1], fill=color))

        self.points_draw_objects.extend(lst)

    def handle_delete_page(self, event=None):
        if self.pages_iterator.current() is not None:
            self.pages_manager.pages.pop(self.pages_iterator.object_index)
            self.pages_iterator.prev()

    def handle_page_chosen(self, choice):
        self.pages_iterator.select(choice)
        self.update_current_page()
        self.update_page_name()

    def handle_next_page(self, event=None):
        self.pages_iterator.next()
        self.update_current_page()
        self.update_page_name()

    def handle_prev_page(self, event=None):
        self.pages_iterator.prev()
        self.update_current_page()
        self.update_page_name()

    def update_current_page(self):
        if self.pages_iterator.current() is not None:
            self.reset_canvas()
            self.canvas.create_image((0, 0), anchor=tk.NW, image=self.pages_iterator.current().image)

    def update_pages_menu(self):
        """Sets image names and their indices as menu options"""

        choices = None
        if len(self.pages_manager.pages) > 0:
            choices = {self.pages_manager.pages[page_i].name: page_i for page_i in range(len(self.pages_manager.pages))}

        self.set_menu_choices(self.menu_pages, choices, self.handle_page_chosen)

    def update_page_name(self):
        if self.pages_iterator.current() is not None:
            self.var_page_name.set(self.pages_iterator.current().name)
        else:
            self.var_page_name.set(self.msg_not_selected)

    def handle_draw_text(self):
        """Draws text on current page"""
        pass

    def update_page_images(self, file_path):
        self.pages_manager.pages = []
        self.pages_manager.read_pages_from_dir(file_path)
        self.pages_iterator = self.pages_manager.get_iterator()

    def handle_rename_page(self):
        """Renames current selected page"""
        if self.pages_iterator.current() is not None:
            self.pages_iterator.current().name = askstring("Rename", "Enter new page name")
            self.update_page_name()

def main():
    root = tk.Tk()
    app = PageTextWriterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
