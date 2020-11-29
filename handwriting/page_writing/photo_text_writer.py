import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

from handwriting.canvas_objects_manager import CanvasObjectsManager
from handwriting.event_handler import EventManager
from handwriting.grid_manager import GridManager
from handwriting.option_menu_manager import OptionMenuManager
from handwriting.page_writing.page_text_manager import PageTextManager
from handwriting.path_management.dictionary_manager import DictionaryManager


class PhotoTextWriter(tk.Frame, DictionaryManager, CanvasObjectsManager, GridManager, EventManager, OptionMenuManager):

    msg_not_selected = '-'

    def __init__(self, root):
        root.geometry("800x650")
        tk.Frame.__init__(self, root)
        self.root = root

        self.grid_width = 15
        self.grid_height = 1

        self.brush_size = 5
        self.brush_color = "black"

        self.cur_text_writer = None
        self.pages_manager = PageTextManager()
        self.pages_iterator = self.pages_manager.get_iterator()

        self.text_image = None
        self.photoimage_page = None

        self.points_counter = 0
        self.points_colors = ['red', 'red', 'black']

        self.text_points_format = '({0}, {1})/({2}, {3})\n({4}, {5})'

        self.image_suffix = '.png'

        self.shift_paths_open_mode = tk.BooleanVar()
        self.shift_paths_open_mode.set(0)

        self.setup_UI()
        self.reset_canvas()

        CanvasObjectsManager.__init__(self)

    def create_events_dict(self):
        return \
            {
                # event type
                "B1": {
                    "ButtonRelease": (self.canvas, self.handle_mouse_release),
                    "Motion": (self.canvas, self.handle_motion_draw)
                },
                "KeyPress": {
                    "Left": (self.root, self.handle_prev_page),
                    "Right": (self.root, self.handle_next_page),
                    "Return": [
                        (self.entry_dict_path, self.handle_update_dict_path),
                        (self.entry_pages_dir, self.handle_update_pages_path)
                    ],
                    "Delete": self.handle_delete_path,
                    "space": self.handle_create_new_path
                }
            }

    def create_ui_grid(self, root):
        """
        Grid must be created before event binding
        :return: grid of objects
        """

        grid_width = 15
        self.canvas = tk.Canvas(self, bg="white", height=600)
        self.reset_canvas()

        label_dict_path = tk.Label(self, text="Choose dictionary: ")
        self.field_dict_path = tk.StringVar(self)
        self.entry_dict_path = tk.Entry(self, width=grid_width, textvariable=self.field_dict_path)

        label_pages_dir = tk.Label(self, text="Choose pages folder: ")
        self.field_pages_dir = tk.StringVar(self)
        self.entry_pages_dir = tk.Entry(self, width=grid_width, textvariable=self.field_pages_dir)

        self.cur_page_name_var = tk.StringVar(self)
        self.ch_page_menu = tk.OptionMenu(self, self.cur_page_name_var, value=None)
        self.update_pages_menu()

        self.ch_page_menu.config(width=grid_width, height=self.grid_height)

        frame_page_buttons = tk.Frame(self)
        btn_prev_page = tk.Button(frame_page_buttons, text='<<', command=lambda: self.handle_prev_page(),
                                  width=round(grid_width / 2))
        btn_next_page = tk.Button(frame_page_buttons, text='>>', command=lambda: self.handle_next_page(),
                                  width=round(grid_width / 2))
        btn_prev_page.pack(side=tk.LEFT)
        btn_next_page.pack(side=tk.RIGHT)

        draw_text_btn = tk.Button(self, text="Remove image", width=round(grid_width * 2 / 3),
                                  height=self.grid_height, command=lambda: self.handle_remove_page())

        draw_text_btn = tk.Button(self, text="Draw text", width=round(grid_width * 2 / 3), height=self.grid_height,
                                  command=lambda: self.handle_draw_text())

        reset_text_btn = tk.Button(self, text="Reset text", width=round(grid_width * 2 / 3),
                                   command=lambda: self.handle_reset_text())

        # text area abs_points
        points_btn = tk.Button(self, text="Points", width=grid_width, height=self.grid_height,
                               command=lambda: self.handle_init_text_points())

        self.points_values_var = tk.StringVar(self)
        self.points_values_var.set(self.text_points_format.format(*[0] * 6))
        points_values_str = tk.Label(self, width=grid_width,
                                     textvariable=self.points_values_var)  # 500,500,500,500,500,500))

        space_sz_label = tk.Label(self, text="Space size")

        self.space_sz_var = tk.StringVar(self)
        self.space_sz_var.set(50)
        space_sz_entry = tk.Entry(self, width=grid_width, textvariable=self.space_sz_var)
        self.draw_text_var = tk.Text(self, width=grid_width * 3, height=self.grid_height * 3)

        # arrange table
        widgets_table_rows = [
            [points_btn, space_sz_label, points_values_str],
            [label_dict_path, self.entry_dict_path, self.ch_page_menu, space_sz_entry],
            [label_pages_dir, frame_page_buttons, draw_text_btn,
             (self.draw_text_var, {"rowspan": 2, "columnspan": 3})],
            [reset_text_btn, points_values_str],
            [],
            [(self.canvas, {"columnspan": 7, "sticky": None})],
        ]

        # if argument not specifyed explicitly, take it from global arguments
        global_arguments = {"padx": 5, "pady": 5, "sticky": tk.EW}

        columns_count = max(len(row) for row in widgets_table_rows)
        root.columnconfigure(columns_count, weight=1)
        root.rowconfigure(len(widgets_table_rows), weight=1)

        return widgets_table_rows, global_arguments

    def setup_UI(self):

        self.root.title("Text writer")
        self.pack(fill=tk.BOTH, expand=1)

        self.put_objects_on_grid(*self.create_ui_grid(self))
        self.bind_handlers(self.create_events_dict())

    def reset_canvas(self):
        self.canvas.delete("all")
        self.text_image = None
        self.photoimage_page = None

    def canvas_delete_points(self):
        for obj in self.points_draw_objects:
            self.canvas.delete(obj)

        self.points_draw_objects = []

    def handle_path_entry_update(self, event=None):
        self.root.focus()

        self.dictionary_groups, self.paths_iterator = \
            open_dictionary_file(
                get_dictionary_file_path(self.field_dict_path)
            )

    def handle_update_dict_path(self, event=None):
        directory = self.get_pages_directory()
        # open all images from directory
        pass

    def get_pages_directory(self, directory_str: str = None):
        directory = Path(directory_str) if directory_str is not None else Path(self.field_pages_dir.get())

        if not directory.is_dir():
            directory = directory.with_suffix('')

        if not directory.exists():
            directory.mkdir(parents=True)

        return directory

    def handle_update_pages_path(self, event=None):
        file_path = self.get_dictionary_file_path(self.field_dict_path)
        self.update_page_images(file_path)
        self.update_current_page()

    def handle_reset_text(self):
        pass

    def draw_point_scope(self, point, color):
        lst = []
        r = 10
        lst.append(self.canvas.create_oval((point[0] - r, point[1] - r, point[0] + r, point[1] + r), outline=color))
        lst.append(self.canvas.create_line(point[0], point[1] - r, point[0], point[1] + r, fill=color))
        lst.append(self.canvas.create_line(point[0] - r, point[1], point[0] + r, point[1], fill=color))

        self.points_draw_objects.extend(lst)

    def handle_remove_page(self):
        self.pages_iterator

    def handle_page_chosen(self, label_var, choice):
        pass

    def handle_next_page(self, event=None):
        self.pages_iterator.next()
        self.update_current_page()

    def handle_prev_page(self, event=None):
        self.pages_iterator.prev()
        self.update_current_page()

    def update_current_page(self):
        if self.pages_iterator.current() is not None:
            self.canvas.create_image((0, 0), anchor=tk.NW, image=self.pages_iterator.current().image)

    def update_pages_menu(self):
        """
        Sets image names and their indices as menu options
        :return:
        """

        self.set_menu_choices(self.ch_page_menu, self.cur_page_name_var, )



def main():
    root = tk.Tk()
    app = PhotoTextWriter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
