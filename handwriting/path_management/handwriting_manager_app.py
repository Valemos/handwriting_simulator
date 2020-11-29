import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from tkinter import filedialog

from PIL import Image
from PIL.ImageTk import PhotoImage

from handwriting.path_management.point import Point
from handwriting.path_management.handwritten_path import HandwrittenPath, HandwrittenPathLinesIterator
from handwriting.path_management.path_group import PathGroup
from handwriting.path_management.dictionary_manager import DictionaryManager
from handwriting.grid_manager import GridManager
from handwriting.event_handler import EventManager
from handwriting.option_menu_manager import OptionMenuManager
from handwriting.tkinter_shortcuts import *


class HandwritingShiftModifyer(tk.Frame, DictionaryManager, GridManager, EventManager, OptionMenuManager):
    default_background_path = Path('default_bg.gif')
    not_selected = '-'

    def __init__(self, root):
        root.geometry("510x650")
        tk.Frame.__init__(self, root)
        self.root = root

        self.brush_size = 5
        self.brush_color = "black"

        # dictionary of path groups with default value
        self.dictionary_groups = None
        # iterator inside dictionary through all groups and path variants
        self.paths_iterator = None

        # current path from self.paths_iterator
        self.current_path: HandwrittenPath = None
        # iterator inside path to draw lines
        self.current_path_iterator: HandwrittenPathLinesIterator = None

        self._mouse_released = True

        self.background_image = None
        self.setup_UI()
        self.reset_canvas()

        self.update_menu_names()

    def create_events_dict(self):
        return \
            {
                "B1": {
                    "ButtonRelease": (self.canvas, self.handle_mouse_release),
                    "Motion": (self.canvas, self.handle_motion_draw)
                },
                "KeyPress": {
                    "Left": (self.root, self.handle_prev_letter),
                    "Right": (self.root, self.handle_next_letter),
                    "Return": [
                        (self.entry_shift_x, self.handle_draw_path),
                        (self.entry_shift_y, self.handle_draw_path),
                        (self.file_entry, self.handle_path_entry_update),
                        (self.entry_new_group, self.handle_create_new_path),
                        (self.entry_new_variant, self.handle_create_new_path)
                    ],
                    "Delete": (self.root, self.handle_delete_path),
                    "space": (self.root, self.handle_create_new_path)
                }
            }

    def create_ui_grid(self, root):
        """
        Grid must be created before event binding
        :return: grid of objects
        """

        grid_width = 15

        self.canvas = tk.Canvas(root, width=500, height=450, bg="white")
        self.reset_canvas()
        general_lab = tk.Label(root, text="General: ")

        frame_shift_x = tk.Frame(root)
        label_shift_x = tk.Label(frame_shift_x, text="X:", width=round(grid_width / 5))
        self.field_shift_x = tk.StringVar(root)
        self.entry_shift_x = tk.Entry(frame_shift_x, width=round(grid_width * 4 / 5), textvariable=self.field_shift_x)
        self.field_shift_x.set("100")
        label_shift_x.pack(side=tk.LEFT)
        self.entry_shift_x.pack(side=tk.RIGHT)

        frame_shift_y = tk.Frame(root)
        label_shift_y = tk.Label(frame_shift_y, text="Y:", width=round(grid_width / 5))
        self.field_shift_y = tk.StringVar(root)
        self.entry_shift_y = tk.Entry(frame_shift_y, width=round(grid_width * 4 / 5), textvariable=self.field_shift_y)
        self.field_shift_y.set('100')
        label_shift_y.pack(side=tk.LEFT)
        self.entry_shift_y.pack(side=tk.RIGHT)

        label_ch_file = tk.Label(root, text="File path: ")
        label_path_gr = tk.Label(root, text="Path: ")
        btn_open_file = tk.Button(root, text="Open file", width=grid_width,
                                  command=self.handle_path_entry_update)
        btn_save_file = tk.Button(root, text="Save file", width=grid_width,
                                  command=self.save_selected_file)

        self.field_file_path = tk.StringVar(root)
        self.file_entry = tk.Entry(root, width=grid_width, textvariable=self.field_file_path)

        # this menu lets user select path group
        self.field_group = tk.StringVar(self)
        self.menu_path_group = tk.OptionMenu(root, self.field_group, value=None)
        self.menu_path_group.configure(width=grid_width)

        # menu for path variant
        self.field_path_variant = tk.StringVar(self)
        self.menu_path_variant = tk.OptionMenu(root, self.field_path_variant, value=None)
        self.menu_path_variant.configure(width=grid_width)
        self.update_menu_names()

        frame_switch_paths = tk.Frame(root)
        btn_prev_path = tk.Button(frame_switch_paths, text='<-', command=self.handle_prev_letter,
                                  width=round(grid_width / 2))
        btn_next_path = tk.Button(frame_switch_paths, text='->', command=self.handle_next_letter,
                                  width=round(grid_width / 2))
        btn_prev_path.pack(side=tk.LEFT)
        btn_next_path.pack(side=tk.RIGHT)

        btn_clear = tk.Button(root, text="Clear path", width=grid_width, command=self.handle_clear_path)
        btn_del = tk.Button(root, text="Delete path", width=grid_width, command=self.handle_delete_path)

        frame_new_group = tk.Frame(root)
        label_new_group = tk.Label(frame_new_group, text='Group:',
                                   width=round(grid_width / 3))
        self.field_new_group = tk.StringVar(self)
        self.entry_new_group = tk.Entry(frame_new_group, textvariable=self.field_new_group,
                                        width=round(grid_width * 2 / 3))
        label_new_group.pack(side=tk.LEFT)
        self.entry_new_group.pack(side=tk.RIGHT)

        frame_new_variant = tk.Frame(root)
        label_new_variant = tk.Label(frame_new_variant, text='Variant:',
                                     width=round(grid_width / 3))
        self.field_new_variant = tk.StringVar(self)
        self.entry_new_variant = tk.Entry(frame_new_variant, textvariable=self.field_new_variant,
                                          width=round(grid_width * 2 / 3))
        label_new_variant.pack(side=tk.LEFT)
        self.entry_new_variant.pack(side=tk.RIGHT)

        label_new_path = tk.Label(root, text="New names")
        new_path_btn = tk.Button(root, text="New path", width=grid_width,
                                 command=self.handle_create_new_path)

        """
        list of rows with widget objects, representing grid of corresponding widgets
        to specify parameters for .grid function object is wrapped into dict with all it's parameters
        """

        widgets_table_rows = [
            [general_lab,       frame_shift_x,          frame_shift_y],
            [label_ch_file,     self.file_entry,        btn_open_file,              btn_save_file],
            [label_path_gr,     self.menu_path_group,   self.menu_path_variant,     frame_switch_paths],
            [label_new_path,    frame_new_group,        frame_new_variant,          new_path_btn],
            [None,              None, btn_clear,        btn_del],
            [(self.canvas, {"columnspan": 6, "sticky": None})]
        ]

        # if argument not specifyed explicitly, take it from global arguments
        global_arguments = {"padx": 5, "pady": 5, "sticky": tk.EW}

        columns_count = max(len(row) for row in widgets_table_rows)
        root.columnconfigure(columns_count, weight=1)
        root.rowconfigure(len(widgets_table_rows), weight=1)

        return widgets_table_rows, global_arguments

    def setup_UI(self):

        self.root.title("Handwriting manager")
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
        """
        After new point is appended, iterator will be updated and will be able to give another line
        If this event begins new curve (mouse was previously released and now it was pressed)
        New_curve is created for path and first point is appended to it

        Only one point is not enough for line, so, for this iteration self.current_path_iterator
        must not return anything, but point must be appended
        :param event: tkinter Event object
        """

        if self.current_path is not None:
            if self._mouse_released:
                self._mouse_released = False
                self.current_path.new_curve(Point(event.x, event.y))
            else:
                self.current_path.append_absolute(Point(event.x, event.y))
                self.draw_iterator(self.current_path_iterator)
        else:
            messagebox.showinfo("Attention", "You cannot draw path without group. Create new group and path using "
                                             "entries \"Group\" and \"Variant\" and press button \"New path\" "
                                             "or press \"Space\" on keyboard")

    def handle_mouse_release(self, event):
        self._mouse_released = True

    # draw paths
    def draw_line(self, point1: Point, point2: Point):
        self.canvas.create_line(point1.x, point1.y, point2.x, point2.y, fill=self.brush_color, width=self.brush_size)

    def draw_iterator(self, path_iterator):
        """
        Draws current path lines using HandwrittenPath iterator

        :param path_iterator: iterator for current path
        """
        while True:
            try:
                p1, p2 = next(path_iterator)
                self.draw_line(p1, p2)
            except StopIteration:
                break

    def handle_detect_letter(self, event):
        pass

    def handle_group_chosen(self, index):
        if self.paths_iterator is not None:
            self.paths_iterator.select(index)
            self.reset_current_group()

    def handle_variant_chosen(self, index):
        if self.paths_iterator is not None:
            self.paths_iterator.select(self.paths_iterator.group_iter, index)
            self.update_current_path()
            self.update_menu_names()

    def reset_current_group(self):
        """
        Function resets resets current group menu and variables
        """
        self.update_menu_path_variants()
        self.update_current_path()
        self.update_menu_names()

    def update_current_path(self, anchor_point: Point = None):
        """
        Function assumes, that self.paths_iterator is not None

        Updates current path variables and applies shift to new path
        Draws current iterator lines

        :param anchor_point: if anchor_point is not None,
                            updates absolute position of current path
        """
        if self.paths_iterator is not None:
            self.current_path = self.paths_iterator.current()
            if self.current_path is not None:
                if anchor_point is not None:
                    self.current_path.set_position(anchor_point)
                else:
                    self.current_path.set_position(self.get_shift_point())
                self.current_path_iterator = iter(self.current_path)

                self.reset_canvas()
                self.draw_iterator(self.current_path_iterator)
            else:
                self.reset_canvas()

    def handle_create_new_path(self, event=None):
        """
        If current group name not in paths dictionary, creates new paths group
        else, selects current path group and creates new path with specifyed name

        Creates new empty to current path group using default (or specifyed) additional name
        """
        group_name = self.field_new_group.get()
        group_index = None
        for group_i in range(len(self.dictionary_groups)):
            if group_name == self.dictionary_groups[group_i].name:
                group_index = group_i
                break

        if group_index is None:
            # create new group with desired name
            if self.check_name_valid(group_name):
                self.dictionary_groups.append_group(PathGroup(group_name))
                group_index = len(self.dictionary_groups) - 1
                self.update_menu_groups()
            else:
                messagebox.showinfo("Group name invalid", "name must be a single line\nwith length no more than 128")
                return

        self.paths_iterator.select(group_index)
        path_name = self.field_new_variant.get()
        if self.check_name_valid(path_name):
            self.paths_iterator.current_group().append_path(HandwrittenPath(path_name))
            self.paths_iterator.select(group_index, len(self.paths_iterator.current_group()) - 1)

            # may be problem with path with no curves
            self.update_current_path()
            self.update_menu_path_variants()
        else:
            messagebox.showinfo("Path name invalid", "name must be a single line\nwith length no more than 128")
            return

        self.update_menu_names()
        self.root.focus()

    def handle_draw_path(self, event):
        self.update_current_path()
        self.root.focus()

    def handle_clear_path(self, event=None):
        """Sets new path instead of current chosen letter"""
        if self.paths_iterator is not None:
            if self.paths_iterator.current() is not None:
                self.paths_iterator.current().components = []
                self.update_current_path()

    def handle_delete_group(self):
        """Removes current group from dictionary"""
        self.paths_iterator.delete_group()
        self.update_current_path()
        self.update_menu_names()
        self.update_menu_groups()

    def handle_delete_path(self, event=None):
        """Removes current path from selected path group"""
        if self.paths_iterator.current_group() is not None:
            if len(self.paths_iterator.current_group()) > 0:
                self.paths_iterator.delete_current()
                self.update_current_path()
                self.update_menu_names()
                self.update_menu_path_variants()
            else:
                self.handle_delete_group()

    def handle_next_letter(self, event=None):
        if self.paths_iterator is not None:
            prev_group = self.paths_iterator.group_iter

            self.paths_iterator.next()
            self.update_current_path()
            self.update_menu_names()

            if self.paths_iterator.group_iter != prev_group:
                self.update_menu_path_variants()

    def handle_prev_letter(self, event=None):
        if self.paths_iterator is not None:
            prev_group = self.paths_iterator.group_iter

            self.paths_iterator.prev()
            self.update_current_path()
            self.update_menu_names()

            if self.paths_iterator.group_iter != prev_group:
                self.update_menu_path_variants()

    def update_menu_groups(self):
        """
        If self.dictionary_groups is None, than sets default name for list and clears all previous options
        """

        choices = None
        if self.dictionary_groups is not None:
            choices = {self.dictionary_groups[i].name: i for i in range(len(self.dictionary_groups))}

        self.set_menu_choices(self.menu_path_group, choices, self.handle_group_chosen)

    def update_menu_path_variants(self):
        """
        If self.dictionary_groups is None, than sets default name for list and clears all previous options
        """

        choices = None
        if self.dictionary_groups is not None:
            if self.paths_iterator is not None:
                group = self.paths_iterator.current_group()
                if group is not None:
                    choices = {get_index_name(group[i].name, i + 1): i for i in range(len(group))}

        self.set_menu_choices(self.menu_path_variant, choices, self.handle_variant_chosen)

    def update_menu_names(self):
        if self.paths_iterator is not None:
            group = self.paths_iterator.current_group()
            path = self.paths_iterator.current()
            self.field_group.set(
                group.name
                if group is not None else
                self.not_selected
            )
            self.field_path_variant.set(
                get_index_name(path.name, self.paths_iterator.variant_iter.object_index + 1)
                if path is not None else
                self.not_selected
            )
        else:
            self.field_group.set(self.not_selected)
            self.field_path_variant.set(self.not_selected)

    # working with dictionary file
    def handle_path_entry_update(self, event=None):
        self.root.focus()

        dict_file = self.get_dictionary_file_path(self.field_file_path.get())
        self.field_file_path.set(str(dict_file))
        self.dictionary_groups, self.paths_iterator = self.open_dictionary_file(dict_file)

        self.update_menu_groups()
        self.reset_current_group()

    def save_selected_file(self):
        if self.dictionary_groups is not None:
            self.dictionary_groups.save_file(
                self.get_dictionary_file_path(self.field_file_path)
            )

    # other methods
    def get_shift_point(self):
        """Reads values of two corresponding fields and returns Point object"""
        update_integer_field(self.field_shift_x)
        update_integer_field(self.field_shift_y)

        return Point(int(self.field_shift_x.get()), int(self.field_shift_y.get()))

    @staticmethod
    def check_name_valid(name):
        """Checks if name for HandwrittenPath or SignatureDictionary can be written to file and is one line"""
        return all((i not in name for i in '\t\n')) and len(name) <= 128


def main():
    root = tk.Tk()
    app = HandwritingShiftModifyer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
