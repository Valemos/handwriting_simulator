import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from PIL import Image
from PIL.ImageTk import PhotoImage

from handwriting.gui_parts.entry_integer_with_label import EntryIntegerWithLabel
from handwriting.gui_parts.entry_with_label import EntryWithLabel
from handwriting.gui_parts.left_right_buttons import LeftRightButtons
from handwriting.gui_parts.menu_indexed_with_handler import MenuIndexedWithHandler
from handwriting.gui_parts.menu_with_handler import MenuWithHandler
from handwriting.path.curve.point import Point
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.path_lines_iterator import PathLinesIterator
from handwriting.path.path_group import PathGroup
from handwriting.path.dictionary_manager import DictionaryManager
from handwriting.grid_manager import GridManager
from handwriting.event_handler import EventManager


class HandwritingShiftModifier(tk.Frame, GridManager, EventManager):
    default_background_path = Path('default_bg.gif')

    message_warning_cannot_draw = "You cannot draw path without group. Create new group and path using " \
                                  "entries \"Group\" and \"Variant\" and press button \"New path\" " \
                                  "or press \"Space\" on keyboard"

    message_path_name_invalid = "name must be a single line\nwith length no more than 128"

    def __init__(self, root):
        root.geometry("510x650")
        tk.Frame.__init__(self, root)
        self.parent = root

        self._brush_size = 5
        self._brush_color = "black"
        self._mouse_released = True

        # dict_manager of path groups with default value
        self.dict_manager = DictionaryManager()
        self.cur_path_iterator: PathLinesIterator = None

        self.background_image = None
        self.setup_ui()
        self.reset_canvas()

        self.update_menu_names()

    @staticmethod
    def main():
        root = tk.Tk()
        app = HandwritingShiftModifier(root)
        root.mainloop()

    def create_events_dict(self):
        return \
            {
                "B1": {
                    "ButtonRelease": (self.canvas, self.handle_mouse_release),
                    "Motion": (self.canvas, self.handle_motion_draw)
                },
                "KeyPress": {
                    "Left": (self.parent, self.handle_prev_letter),
                    "Right": (self.parent, self.handle_next_letter),
                    "Return": [
                        (self.entry_shift_x.entry, self.handle_draw_path),
                        (self.entry_shift_y.entry, self.handle_draw_path),
                        (self.entry_dict_path, self.open_dictionary_from_entry_path),
                        (self.entry_new_group, self.handle_create_new_path),
                        (self.entry_new_variant, self.handle_create_new_path)
                    ],
                    "Delete": (self.parent, self.handle_delete_path),
                    "space": (self.parent, self.handle_create_new_path)
                }
            }

    def create_ui_grid(self, root):
        """
        Grid must be created before event binding
        :return: grid of canvas_objects
        """

        grid_width = 15

        self.canvas = tk.Canvas(root, width=500, height=450, bg="white")
        self.reset_canvas()
        general_lab = tk.Label(root, text="General: ")

        self.entry_shift_x = EntryIntegerWithLabel(root, "X:", grid_width, 1 / 5)
        self.entry_shift_y = EntryIntegerWithLabel(root, "Y:", grid_width, 1 / 5)
        self.entry_shift_x.set(100)
        self.entry_shift_y.set(100)

        label_path_gr = tk.Label(root, text="Path: ")
        btn_open_file = tk.Button(root, text="Open file", width=grid_width,
                                  command=self.open_dictionary_from_entry_path)
        btn_save_file = tk.Button(root, text="Save file", width=grid_width,
                                  command=self.save_dictionary_to_file)

        self.entry_dict_path = EntryWithLabel(root, "File path:", grid_width * 2, 1 / 3)

        # this menu lets user select path group
        self.menu_path_group = MenuWithHandler(root, grid_width, self.handle_group_chosen)
        self.menu_path_variant = MenuIndexedWithHandler(root, grid_width, self.handle_variant_chosen)

        # menu for path variant
        self.update_menu_names()

        buttons_move_paths = LeftRightButtons(root, grid_width, self.handle_prev_letter, self.handle_next_letter)

        btn_clear = tk.Button(root, text="Clear path", width=grid_width, command=self.handle_clear_path)
        btn_del = tk.Button(root, text="Delete path", width=grid_width, command=self.handle_delete_path)

        self.entry_new_group = EntryWithLabel(root, 'Group:', grid_width, 1 / 3)
        self.entry_new_variant = EntryWithLabel(root, 'Variant:', grid_width, 1 / 3)

        label_new_path = tk.Label(root, text="New names")
        new_path_btn = tk.Button(root, text="New path", width=grid_width,
                                 command=self.handle_create_new_path)

        """
        list of rows with widget canvas_objects, representing grid of corresponding widgets
        to specify parameters for .grid function object is wrapped into dict with all it's parameters
        """

        widgets_table_rows = [
            [general_lab,           self.entry_shift_x,         self.entry_shift_y],
            [(self.entry_dict_path, {"columnspan": 2}), None, btn_open_file, btn_save_file],
            [label_path_gr,         self.menu_path_group,       self.menu_path_variant,     buttons_move_paths],
            [label_new_path,        self.entry_new_group,       self.entry_new_variant,          new_path_btn],
            [None,              None, btn_clear,        btn_del],
            [(self.canvas, {"columnspan": 6, "sticky": None})]
        ]

        # if argument not specified explicitly, take it from global arguments
        global_arguments = {"padx": 5, "pady": 5, "sticky": tk.EW}

        columns_count = max(len(row) for row in widgets_table_rows)
        root.columnconfigure(columns_count, weight=1)
        root.rowconfigure(len(widgets_table_rows), weight=1)

        return widgets_table_rows, global_arguments

    def setup_ui(self):

        self.parent.title("Handwriting manager")
        self.pack(fill=tk.BOTH, expand=1)

        self.put_objects_on_grid(*self.create_ui_grid(self))

        self.bind_handlers(self.create_events_dict())

    def reset_canvas(self):

        self.canvas.delete("all")
        if self.background_image is not None:
            self.canvas.create_image((int(self.background_image.width() / 2), int(self.background_image.height() / 2)),
                                     image=self.background_image)
        else:
            self.update_background_image()

    def update_background_image(self):
        if self.background_image is not None:
            self.canvas.create_image(
                (
                    int(self.background_image.width() / 2),
                    int(self.background_image.height() / 2)
                ),
                image=self.background_image)

        elif self.default_background_path.exists():
            image = Image.open(self.default_background_path) \
                .resize((int(self.canvas['width']), int(self.canvas['height'])))
            self.background_image = PhotoImage(image)
            self.update_background_image()

    def handle_motion_draw(self, event):
        if self.cur_path_iterator is not None:
            if self._mouse_released:
                self._mouse_released = False
                self.cur_path_iterator.new_curve(Point(event.x, event.y))
            else:
                self.cur_path_iterator.append_absolute(Point(event.x, event.y))
                self.draw_iterator_lines(self.cur_path_iterator)

        else:
            messagebox.showinfo("Warning", self.message_warning_cannot_draw)

    def handle_mouse_release(self, event):
        self._mouse_released = True

    # draw path
    def draw_line(self, point1: Point, point2: Point):
        self.canvas.create_line(point1.x, point1.y, point2.x, point2.y, fill=self._brush_color, width=self._brush_size)

    def draw_iterator_lines(self, path_iterator):
        while True:
            try:
                p1, p2 = next(path_iterator)
                self.draw_line(p1, p2)
            except StopIteration:
                break

    def handle_group_chosen(self, index):
        if self.dict_manager.exists():
            self.dict_manager.iterator.select_group(index)
            self.update_selected_group()

    def handle_variant_chosen(self, variant_index):
        if self.dict_manager.exists():
            group_index = self.dict_manager.iterator.group_iter.index
            self.dict_manager.iterator.select_group(group_index)
            self.dict_manager.iterator.select_variant(variant_index)
            self.update_current_path()
            self.update_menu_names()

    def update_selected_group(self):
        self.update_menu_path_variants()
        self.update_current_path()
        self.update_menu_names()

    def update_current_path(self):
        if self.dict_manager.exists():
            self.reset_canvas()
            current_path = self.dict_manager.iterator.current()

            if current_path is not None:
                # place path at (0, 0) and shift according to entered shift point
                current_path.set_position(Point(0, 0))
                self.cur_path_iterator = current_path.get_iterator(self.get_shift_point())
                self.draw_iterator_lines(self.cur_path_iterator)

    def handle_create_new_path(self, event=None):
        if not self.dict_manager.exists():
            new_path = self.dict_manager.create_default()
            self.entry_dict_path.set(str(new_path))

        group_name = self.entry_new_group.get()
        if not self.dict_manager.dictionary.check_group_exists(group_name):
            if not self.create_new_group(group_name):
                return

        path_name = self.entry_new_variant.get()
        if not self.create_new_path_variant(path_name):
            return

        self.update_menu_names()
        self.parent.focus()

    def handle_draw_path(self, event):
        self.update_current_path()
        self.parent.focus()

    def handle_clear_path(self, event=None):
        if self.dict_manager.exists():
            if self.dict_manager.iterator.current() is not None:
                self.dict_manager.iterator.current().components = []
                self.update_current_path()

    def handle_delete_group(self):
        if self.dict_manager.exists():
            self.dict_manager.iterator.delete_group()
            self.update_current_path()
            self.update_menu_names()
            self.update_menu_groups()

    def handle_delete_path(self, event=None):
        if self.dict_manager.exists() is not None:
            if len(self.dict_manager.iterator.current_group()) > 0:
                self.dict_manager.iterator.delete_current()
                self.update_current_path()
                self.update_menu_names()
                self.update_menu_path_variants()
            else:
                self.handle_delete_group()

    def handle_next_letter(self, event=None):
        if self.dict_manager.exists():
            prev_group = self.dict_manager.iterator.group_iter

            self.dict_manager.iterator.next()
            self.update_current_path()
            self.update_menu_names()

            if self.dict_manager.iterator.group_iter != prev_group:
                self.update_menu_path_variants()

    def handle_prev_letter(self, event=None):
        if self.dict_manager.exists():
            prev_group = self.dict_manager.iterator.group_iter

            self.dict_manager.iterator.prev()
            self.update_current_path()
            self.update_menu_names()

            if self.dict_manager.iterator.group_iter != prev_group:
                self.update_menu_path_variants()

    def update_menu_groups(self):
        group_choices = None
        if self.dict_manager.exists():
            all_groups = self.dict_manager.dictionary.groups
            group_choices = {all_groups[i].name: i for i in range(len(all_groups))}

        self.menu_path_group.update_choices(group_choices)

    def update_menu_path_variants(self):
        choices = None
        if self.dict_manager.exists():
            group = self.dict_manager.iterator.current_group()
            if group is not None:
                choices = {group[i].name: i for i in range(len(group))}

        self.menu_path_variant.update_choices(choices)

    def update_menu_names(self):
        if self.dict_manager.exists():
            current_group = self.dict_manager.iterator.current_group()
            current_path = self.dict_manager.iterator.current()
            self.menu_path_group.set(current_group.name if current_group is not None else None)
            self.update_menu_variant_name(current_path)
        else:
            self.menu_path_group.set(None)
            self.menu_path_variant.set(None)

    def update_menu_variant_name(self, path):
        if path is not None:
            variant_index = self.dict_manager.iterator.variant_iter.index + 1
            self.menu_path_variant.set_indexed_name(variant_index, path.name)
        else:
            self.menu_path_variant.set(None)

    def open_dictionary_from_entry_path(self, event=None):
        new_path = self.dict_manager.read_from_file(self.entry_dict_path.get())
        self.entry_dict_path.set(str(new_path))

        self.parent.focus()
        self.update_menu_groups()
        self.update_selected_group()

    def save_dictionary_to_file(self):
        if self.dict_manager.exists():
            self.dict_manager.save_file(self.entry_dict_path.get())

    def get_shift_point(self):
        return Point(self.entry_shift_x.get(), self.entry_shift_y.get())

    @staticmethod
    def check_name_valid(name):
        """Checks if name for HandwrittenPath or SignatureDictionary can be written to file and is one line"""
        return all((i not in name for i in '\t\n')) and len(name) <= 128

    def create_new_group(self, group_name):
        if self.check_name_valid(group_name):
            self.dict_manager.dictionary.append_group(PathGroup(group_name))
            self.dict_manager.iterator.select_group(len(self.dict_manager.dictionary) - 1)
            self.update_menu_groups()
            return True
        else:
            messagebox.showinfo("Group name invalid", self.message_path_name_invalid)
            return False

    def create_new_path_variant(self, path_name):
        if self.check_name_valid(path_name):
            current_group = self.dict_manager.iterator.current_group()
            current_group.append_path(HandwrittenPath(path_name))
            self.dict_manager.iterator.select_variant(len(current_group) - 1)

            self.update_current_path()
            self.update_menu_path_variants()
            return True
        else:
            messagebox.showinfo("Path name invalid", self.message_path_name_invalid)
            return False


if __name__ == "__main__":
    HandwritingShiftModifier.main()
