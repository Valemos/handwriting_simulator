import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import copy

from handwriting.handwritten_path import HandwrittenPath
from handwriting.path_group import PathGroup
from handwriting.point import Point
from handwriting.signature_dictionary import SignatureDictionary


class HandwritingShiftModifyer(tk.Frame):
    default_bg_path = 'default_bg.gif'

    no_choices_message = 'no options'
    can_select_message = 'select'

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.grid_width = 15

        self.brush_size = 5
        self.brush_color = "black"

        # dictionary of path groups
        self.paths_dictionary: SignatureDictionary = None
        self.paths_iterator = None

        self.background_image = None

        self.setup_UI()
        self.reset_canvas()

    def create_events_dict(self):
        """
        dictionary with keys as events and handler functions as values
        format as follows <modifier-type-first_part>, handler at the end of the chain
        handler handler can be a tuple of Tkinter object and handler handler to bind to it
        if bind object is not specifyed, event will be bound to root
        """
        return \
            {
                # event type
                "B1": {
                    "ButtonPress": (self.canvas, self.handle_mouse_press),
                    "ButtonRelease": (self.canvas, self.handle_mouse_release),
                    "Motion": (self.canvas, self.handle_motion_draw)
                },
                "Control-Key": {
                    "d": lambda e: self.reset_canvas()
                },
                "Left": lambda e: self.go_to_prev_letter(),
                "Right": lambda e: self.go_to_next_letter(),
                "KeyRelease": {
                    "Return": [
                        (self.shift_x_entry, self.handle_draw_path),
                        (self.shift_y_entry, self.handle_draw_path),
                        (self.file_entry, self.handle_enter_on_path),
                        (self.new_char_entry, lambda e: self.handle_save_new_letter())
                    ],
                }
            }

    def _bind_function(self, handler, first_part, second_part=None):
        if isinstance(handler, dict):
            for second_part, func in handler.items():
                self._bind_function(func, first_part, second_part)
            return

        if isinstance(handler, list):
            for func in handler:
                self._bind_function(func, first_part, second_part)
            return

        if isinstance(handler, tuple):
            bind_object, handler = handler
            bind_object.bind(f"<{first_part}>"
                             if second_part is None else
                             f"<{first_part}-{second_part}>",
                             handler)
        else:
            self.bind(f"<{first_part}>"
                      if second_part is None else
                      f"<{first_part}-{second_part}>",
                      handler)

    def bind_window_events(self, events_dict):
        for first_part, function in events_dict.items():
            self._bind_function(function, first_part)

    def create_grid(self, root):
        """
        Grid must be created before event binding
        :return: grid of objects
        """

        self.canvas = tk.Canvas(root, bg="white")
        self.reset_canvas()
        general_lab = tk.Label(root, text="General: ")
        # ?
        clear_btn = tk.Button(root, text="Clear all", width=self.grid_width, command=lambda: self.reset_canvas())

        shift_x_label = tk.Label(root, text="Shift X: ")
        self.shift_x_field = tk.StringVar(root)
        self.shift_x_field.set('100')
        self.shift_x_field.trace('w', self.limit_is_int_shx)
        self.shift_x_entry = tk.Entry(root, width=self.grid_width, textvariable=self.shift_x_field)

        shift_y_label = tk.Label(root, text="Shift Y: ")
        self.shift_y_field = tk.StringVar(root)
        self.shift_y_field.set('100')
        self.shift_y_field.trace('w', self.limit_is_int_shy)
        self.shift_y_entry = tk.Entry(root, width=self.grid_width, textvariable=self.shift_y_field)

        ch_file_lab = tk.Label(root, text="Choose file path: ")
        ch_let_lab = tk.Label(root, text="Choose file letter: ")
        open_file_btn = tk.Button(root, text="Open file", width=self.grid_width,
                                  command=lambda: self.open_selected_file())
        save_file_btn = tk.Button(root, text="Save file", width=self.grid_width,
                                  command=lambda: self.save_selected_file())

        self.file_path_field = tk.StringVar(self)
        self.file_entry = tk.Entry(root, width=self.grid_width, textvariable=self.file_path_field)

        # enter press opens files
        self.cur_path_name_field = tk.StringVar(self)
        self.cur_path_name_field.set(self.no_choices_message)
        self.ch_letter_menu = tk.OptionMenu(root, self.cur_path_name_field, value=None)
        self.ch_letter_menu.configure(width=self.grid_width)
        self.set_field_choices(self.ch_letter_menu, self.cur_path_name_field, None)

        control_btn_frame = tk.Frame(root)
        control_btn_frame.grid(row=2, column=2, sticky=tk.EW)
        control_btn_prev = tk.Button(control_btn_frame, text='<<', command=lambda: self.go_to_prev_letter(),
                                     width=round(self.grid_width / 2))
        control_btn_next = tk.Button(control_btn_frame, text='>>', command=lambda: self.go_to_next_letter(),
                                     width=round(self.grid_width / 2))
        control_btn_prev.pack(side=tk.LEFT)
        control_btn_next.pack(side=tk.RIGHT)

        # ?
        draw_curve_btn = tk.Button(root, text="Draw path", command=self.handle_draw_path)

        edit_btn = tk.Button(root, text="Edit path", width=self.grid_width, command=self.handle_edit_letter)
        del_btn = tk.Button(root, text="Delete path", width=self.grid_width, command=self.handle_delete_letter)
        create_let_lab = tk.Label(root, text="Create new path: ")
        new_char_frame = tk.Frame(root)
        new_char_label = tk.Label(new_char_frame, text='New name:', width=round(self.grid_width / 2))
        new_char_label.pack(side=tk.LEFT)

        self.new_char_field = tk.StringVar(self)
        self.new_char_entry = tk.Entry(new_char_frame, width=10, textvariable=self.new_char_field)
        self.new_char_entry.pack(side=tk.RIGHT)

        save_let_btn = tk.Button(root, text="Save and continue", width=self.grid_width,
                                 command=self.handle_save_new_letter)

        detect_let_btn = tk.Button(root, text="Detect current letter", width=self.grid_width,
                                   command=self.handle_detect_letter)

        # list of rows with widget objects, representing grid of corresponding widgets
        # to specify parameters for .grid function object is wrapped into dict with all it's parameters

        widgets_table_rows = [
            [general_lab, clear_btn, shift_x_label, self.shift_x_entry, shift_y_label, self.shift_y_entry],
            [ch_file_lab, self.file_entry, open_file_btn, save_file_btn],
            [ch_let_lab, self.ch_letter_menu, None, draw_curve_btn, edit_btn, del_btn],
            [],
            [create_let_lab, new_char_frame, save_let_btn],  # detect_let_btn
            [(self.canvas, {"columnspan": 6, "sticky": tk.NSEW})]
        ]
        # if argument not specifyed explicitly, take it from global arguments
        global_arguments = {"padx": 5, "pady": 5, "sticky": tk.EW}

        root.columnconfigure(max(len(row) for row in widgets_table_rows), weight=1)
        root.rowconfigure(len(widgets_table_rows), weight=1)

        return widgets_table_rows, global_arguments

    @staticmethod
    def put_objects_on_grid(grid_rows, arguments):
        for row in range(len(grid_rows)):
            for col in range(len(grid_rows[row])):
                if grid_rows[row][col] is None:
                    continue
                elif isinstance(grid_rows[row][col], tuple):
                    obj, args = grid_rows[row][col]
                    for arg_name, value in arguments.items():
                        if arg_name not in args:
                            args[arg_name] = value

                    obj.grid(row=row, column=col, **args)
                else:
                    grid_rows[row][col].grid(row=row, column=col, **arguments)

    def setup_UI(self):

        self.parent.title("Handwriting manager")
        self.pack(fill=tk.BOTH, expand=1)

        grid, arguments = self.create_grid(self)
        self.put_objects_on_grid(grid, arguments)

        self.bind_window_events(self.create_events_dict())

    def reset_canvas(self):

        self.canvas.delete("all")
        if self.background_image is not None:
            self.canvas.create_image((int(self.background_image.width() / 2), int(self.background_image.height() / 2)),
                                     image=self.background_image)
        else:
            self.update_background_image()

    def update_background_image(self):
        if Path(self.default_bg_path).exists():
            self.background_image = tk.PhotoImage(file=str(Path(self.default_bg_path).resolve()))
            self.canvas.create_image(
                (
                    int(self.background_image.width() / 2),
                    int(self.background_image.height() / 2)
                ),
                image=self.background_image)

    def handle_mouse_press(self, event: tk.Event):
        pass

    def handle_motion_draw(self, event: tk.Event):
        # self.current_path.append_absolute(Point(event.x, event.y))
        pass

    def handle_mouse_release(self, event: tk.Event):
        pass

    def draw_line(self, point1: Point, point2: Point):
        self.canvas.create_line(point1.x, point1.y, point2.x, point2.y, fill=self.brush_color, width=self.brush_size)

    def draw_current_path(self, anchor_point=None):
        """
        Draws current path lines using HandwrittenPath iterator

        :param anchor_point: if anchor_point is not None,
                            updates absolute position of current path
        """

        if self.paths_iterator is not None:
            path = self.paths_iterator.current()
            if path is not None:
                if anchor_point is not None:
                    path.set_position(anchor_point)

                self.reset_canvas()
                for p1, p2 in path:
                    self.draw_line(p1, p2)

    def handle_detect_letter(self, event):
        pass

    def handle_letter_chosen(self, label_var, choice):
        pass

    def handle_enter_on_path(self, event):
        file_path = self.handle_file_path(self.file_path_field.get())
        self.paths_dictionary = SignatureDictionary.from_file(file_path)
        self.paths_iterator = self.paths_dictionary.get_iterator()

    def handle_save_new_letter(self, event):
        """Saves letter to path group using default (or specifyed) additional name"""
        pass

    def handle_draw_path(self, event):
        self.draw_current_path()

    def handle_edit_letter(self, event):
        """Sets new path instead of current chosen letter"""
        pass

    def handle_delete_letter(self, event):
        """Removes current letter from selected path group"""
        pass

    def go_to_next_letter(self):
        if self.paths_iterator is not None:
            self.paths_iterator.next()
            self.draw_current_path(self.get_shift_point())

    def go_to_prev_letter(self):
        if self.paths_iterator is not None:
            self.paths_iterator.prev()
            self.draw_current_path(self.get_shift_point())

    def limit_is_int_shx(self, *args):
        value = self.shift_x_field.get()
        if not self.str_is_int(value):
            self.shift_x_field.set(''.join([i for i in value if i.isdigit()]))

    def limit_is_int_shy(self, *args):
        value = self.shift_y_field.get()
        if not self.str_is_int(value):
            self.shift_y_field.set(''.join([i for i in value if i.isdigit()]))

    def str_is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def set_field_choices(self, option_menu, label_var, choices: dict = None, default=None):
        # option_menu['menu'].delete(0, 'end')
        label_var.set(self.no_choices_message if choices is None else self.can_select_message)
        if choices is None:
            return

        for choice in choices:
            option_menu['menu'].add_command(label=choice,
                                            command=lambda c=choice: self.handle_letter_chosen(label_var, c))

        if default is not None:
            label_var.set(default)

    def open_selected_file(self):
        file_path = self.handle_file_path(self.file_path_field.get())

        # if path is None:
        #     file_path = self.handle_file_path(is_shift_file=self.shift_mode.get())
        # else:
        #     file_path = path
        #
        # if self.shift_mode.get() and not str(file_path.with_suffix('')).endswith(self.d_shift_suffix):
        #     file_path = self.handle_file_path(str(file_path.with_suffix('')) + self.d_shift_suffix + self.d_file_suffix)
        #     self.file_path_field.set(str(file_path))
        #
        # if file_path.exists():
        #     temp_paths = HandwrittenPath.from_file(self.shift_mode.get())
        #     temp_dict = {}
        #     for path in temp_paths:
        #         path.name = self.make_unique_name(path.name, temp_dict)
        #         temp_dict[path.name] = path
        #
        #     self.all_paths_dict = temp_dict
        #     self.refresh_letter_choices(temp_dict)
        #     if len(self.all_paths_dict) > 0:
        #         self.handle_letter_chosen(self.cur_path_name_field, list(self.all_paths_dict.keys())[0])
        #         self.new_char_field.set(list(self.all_paths_dict.values())[0].name)
        #     else:
        #         self.new_char_field.set('')
        return None

    def save_selected_file(self):
        self.paths_dictionary.save_file()

    def refresh_letter_choices(self, choices: dict, default=None):
        self.set_field_choices(self.ch_letter_menu, self.cur_path_name_field, choices, default)

    def handle_file_path(self, path_str=None):
        file_path = Path(path_str) if path_str is not None else Path(self.file_path_field.get())

        sfx = SignatureDictionary.dictionary_suffix
        if file_path.suffix != sfx:
            file_path = file_path.with_suffix(sfx)

        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            messagebox.showinfo('Handwriting manager', 'Successfully created file\n' + str(file_path))

        self.file_path_field.set(str(file_path))
        return file_path

    @staticmethod
    def get_int(field):
        try:
            return int(field.get())
        except ValueError:
            return 0

    def get_shift_point(self):
        """Reads values of two corresponding fields and returns Point object"""
        return Point(self.get_int(self.shift_x_field), self.get_int(self.shift_y_field))


def main():
    root = tk.Tk()
    root.geometry("800x700")
    app = HandwritingShiftModifyer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
